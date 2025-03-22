import discord
from discord.ext import commands
import sqlite3
from datetime import datetime, timedelta
import os
import logging
from discord.ext import tasks

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("moderation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("moderation")

class ModerationCog(commands.Cog):
    """Gère les bans et leur limite mensuelle."""

    def __init__(self, bot):
        self.bot = bot
        self.db_path = "moderation.db"
        self.ban_role_id = 1234911574821568595  # ID du rôle de bannissement
        self.admin_channel_id = 1234853264416309310  # ID du salon d'admin
        
        # Initialisation de la base de données
        self._init_database()
        
        # Démarrer la tâche de vérification automatique
        self.auto_check_roles.start()

    def _init_database(self):
        """Initialise la base de données SQLite."""
        try:
            # Création du dossier data s'il n'existe pas
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # Connexion à la base de données
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Création des tables si elles n'existent pas
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS moderators (
                user_id INTEGER PRIMARY KEY,
                ban_limit INTEGER,
                initial_limit INTEGER,
                reset_date TEXT
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS ban_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                moderator_id INTEGER,
                banned_user_id INTEGER,
                banned_user_name TEXT,
                reason TEXT,
                timestamp TEXT,
                FOREIGN KEY (moderator_id) REFERENCES moderators (user_id)
            )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Base de données initialisée avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")

    def _get_moderator_data(self, user_id):
        """Récupère les données d'un modérateur depuis la base de données."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM moderators WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    "user_id": result[0],
                    "ban_limit": result[1],
                    "initial_limit": result[2],
                    "reset_date": result[3]
                }
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données du modérateur: {e}")
            return None

    def _get_all_moderators(self):
        """Récupère tous les modérateurs depuis la base de données."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM moderators")
            results = cursor.fetchall()
            conn.close()
            
            moderators = []
            for result in results:
                moderators.append({
                    "user_id": result[0],
                    "ban_limit": result[1],
                    "initial_limit": result[2],
                    "reset_date": result[3]
                })
            return moderators
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de tous les modérateurs: {e}")
            return []

    def _set_moderator_data(self, user_id, ban_limit, initial_limit, reset_date):
        """Définit ou met à jour les données d'un modérateur dans la base de données."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Vérifier si le modérateur existe déjà
            cursor.execute("SELECT * FROM moderators WHERE user_id = ?", (user_id,))
            if cursor.fetchone():
                # Mettre à jour les données existantes
                cursor.execute(
                    "UPDATE moderators SET ban_limit = ?, initial_limit = ?, reset_date = ? WHERE user_id = ?",
                    (ban_limit, initial_limit, reset_date, user_id)
                )
            else:
                # Insérer un nouveau modérateur
                cursor.execute(
                    "INSERT INTO moderators (user_id, ban_limit, initial_limit, reset_date) VALUES (?, ?, ?, ?)",
                    (user_id, ban_limit, initial_limit, reset_date)
                )
            
            conn.commit()
            conn.close()
            logger.info(f"Données du modérateur {user_id} mises à jour avec succès")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des données du modérateur: {e}")
            return False

    def _add_ban_history(self, moderator_id, banned_user_id, banned_user_name, reason):
        """Ajoute un enregistrement dans l'historique des bannissements."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = datetime.utcnow().isoformat()
            cursor.execute(
                "INSERT INTO ban_history (moderator_id, banned_user_id, banned_user_name, reason, timestamp) VALUES (?, ?, ?, ?, ?)",
                (moderator_id, banned_user_id, banned_user_name, reason, timestamp)
            )
            
            conn.commit()
            conn.close()
            logger.info(f"Bannissement de {banned_user_name} par {moderator_id} enregistré")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du bannissement: {e}")
            return False

    def _check_and_reset_limit(self, user_id):
        """Vérifie si la limite de bans doit être réinitialisée et le fait si nécessaire."""
        try:
            mod_data = self._get_moderator_data(user_id)
            if not mod_data:
                return False
            
            # Convertir les dates en objets datetime
            current_date = datetime.utcnow()
            reset_date = datetime.fromisoformat(mod_data["reset_date"])
            
            # Si la date de réinitialisation est dépassée
            if current_date >= reset_date:
                # Calculer la nouvelle date de réinitialisation (même intervalle que précédemment)
                days_interval = (reset_date - (reset_date - timedelta(days=30))).days
                new_reset_date = current_date + timedelta(days=days_interval)
                
                # Mettre à jour les données
                self._set_moderator_data(
                    user_id,
                    mod_data["initial_limit"],
                    mod_data["initial_limit"],
                    new_reset_date.isoformat()
                )
                logger.info(f"Limite de bans réinitialisée pour l'utilisateur {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la vérification/réinitialisation de la limite: {e}")
            return False

    @commands.command(name="setban")
    @commands.has_permissions(administrator=True)
    async def set_ban_limit(self, ctx, user: discord.Member, nombre: int, timeReset: int):
        """
        Définit la limite de bans pour un modérateur.
        Exemple: !setban @modérateur 10 30 (10 bans max, reset dans 30 jours)
        """
        try:
            # Calculer la date de réinitialisation
            reset_date = (datetime.utcnow() + timedelta(days=timeReset)).isoformat()
            
            # Mettre à jour les données du modérateur
            success = self._set_moderator_data(user.id, nombre, nombre, reset_date)
            
            if success:
                # Ajouter le rôle de bannissement si nécessaire
                ban_role = ctx.guild.get_role(self.ban_role_id)
                if ban_role and ban_role not in user.roles:
                    await user.add_roles(ban_role)
                    logger.info(f"Rôle de bannissement ajouté à {user.name}")
                
                formatted_date = datetime.fromisoformat(reset_date).strftime("%d/%m/%Y")
                await ctx.send(f"✅ **{user.name}** peut désormais faire `{nombre}` bans. La limite sera réinitialisée le `{formatted_date}`.")
            else:
                await ctx.send("❌ Une erreur est survenue lors de la définition de la limite de bans.")
        except Exception as e:
            logger.error(f"Erreur dans la commande setban: {e}")
            await ctx.send(f"❌ Une erreur est survenue: {str(e)}")

    @commands.command(name="banstats")
    @commands.has_permissions(administrator=True)
    async def ban_stats(self, ctx, member: discord.Member = None):
        """
        Affiche les bans restants.
        - !banstats → Montre tous les modérateurs avec leur limite de bans restante.
        - !banstats @Pseudo → Montre uniquement les bans restants de @Pseudo.
        """
        try:
            if member:
                # Si un membre est spécifié, on affiche uniquement ses infos
                mod_data = self._get_moderator_data(member.id)
                if not mod_data:
                    await ctx.send(f"❌ **{member.name}** n'a pas de limite de bans définie.")
                    return
                
                formatted_date = datetime.fromisoformat(mod_data["reset_date"]).strftime("%d/%m/%Y")
                await ctx.send(
                    f"📊 **{member.name}** peut encore faire `{mod_data['ban_limit']}` bans. (Reset: `{formatted_date}`)")
            else:
                # Si aucun membre n'est spécifié, on affiche la liste complète
                moderators = self._get_all_moderators()
                
                if not moderators:
                    await ctx.send("📊 Aucun modérateur n'a de limite de bans définie.")
                    return
                
                lines = ["📊 **Bannissements restants par modérateur :**"]
                for mod_data in moderators:
                    mod_user = self.bot.get_user(mod_data["user_id"])
                    formatted_date = datetime.fromisoformat(mod_data["reset_date"]).strftime("%d/%m/%Y")
                    
                    if mod_user:
                        lines.append(
                            f"- **{mod_user.name}** : `{mod_data['ban_limit']}` bans restants (Reset: `{formatted_date}`)")
                    else:
                        lines.append(
                            f"- <@{mod_data['user_id']}> : `{mod_data['ban_limit']}` bans restants (Reset: `{formatted_date}`)")
                
                stats_message = "\n".join(lines)
                await ctx.send(stats_message)
        except Exception as e:
            logger.error(f"Erreur dans la commande banstats: {e}")
            await ctx.send(f"❌ Une erreur est survenue: {str(e)}")

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban_member(self, ctx, member: discord.Member, *, reason=None):
        """Bannit un membre en respectant la limite définie et retire le rôle si la limite est atteinte."""
        try:
            # Vérifier si l'utilisateur a le rôle de bannissement
            ban_role = ctx.guild.get_role(self.ban_role_id)
            if ban_role not in ctx.author.roles:
                await ctx.send(f"⛔ {ctx.author.mention}, vous n'avez pas le rôle nécessaire pour bannir des membres.")
                return
            
            # Vérifier si la cible est un administrateur ou modérateur
            if member.guild_permissions.administrator or member.guild_permissions.ban_members:
                await ctx.send(f"⛔ {ctx.author.mention}, vous ne pouvez pas bannir un administrateur ou un modérateur.")
                return
            
            # Vérifier si le modérateur a une limite définie
            mod_data = self._get_moderator_data(ctx.author.id)
            if not mod_data:
                await ctx.send(
                    f"⛔ {ctx.author.mention}, vous n'avez pas de limite de bans définie. Demandez à un admin d'utiliser `!setban`.")
                return
            
            # Vérifier si la limite doit être réinitialisée
            self._check_and_reset_limit(ctx.author.id)
            
            # Récupérer les données mises à jour
            mod_data = self._get_moderator_data(ctx.author.id)
            ban_limit = mod_data["ban_limit"]
            
            # Vérifier si la limite est atteinte
            if ban_limit <= 0:
                await ctx.send(
                    f"⛔ {ctx.author.mention}, vous avez atteint votre limite de bans et votre rôle de bannissement va être retiré.")
                
                # Retirer le rôle de bannissement
                try:
                    await ctx.author.remove_roles(ban_role)
                    await ctx.send(f"🔴 {ctx.author.mention}, votre rôle de bannissement a été retiré.")
                    logger.info(f"Rôle de bannissement retiré à {ctx.author.name}")
                    
                    # Notifier les administrateurs
                    admin_channel = self.bot.get_channel(self.admin_channel_id)
                    if admin_channel:
                        await admin_channel.send(
                            f"⚠️ **{ctx.author.name}** a atteint sa limite de bans et son rôle a été retiré.")
                except discord.Forbidden:
                    await ctx.send("⚠️ Je n'ai pas la permission de retirer le rôle.")
                    logger.error(f"Permission insuffisante pour retirer le rôle à {ctx.author.name}")
                except Exception as e:
                    await ctx.send(f"⚠️ Erreur lors du retrait du rôle: {str(e)}")
                    logger.error(f"Erreur lors du retrait du rôle à {ctx.author.name}: {e}")
                
                return
            
            # Bannir l'utilisateur
            try:
                await member.ban(reason=reason or "Aucune raison spécifiée")
                
                # Enregistrer le bannissement dans l'historique
                self._add_ban_history(ctx.author.id, member.id, member.name, reason)
                
                # Décrémenter le nombre de bans restants
                new_limit = ban_limit - 1
                self._set_moderator_data(
                    ctx.author.id,
                    new_limit,
                    mod_data["initial_limit"],
                    mod_data["reset_date"]
                )
                
                # Formater la date pour l'affichage
                formatted_date = datetime.fromisoformat(mod_data["reset_date"]).strftime("%d/%m/%Y")
                
                await ctx.send(
                    f"✅ **{member.name}** a été banni par **{ctx.author.name}**. "
                    f"Il reste `{new_limit}` bans avant la réinitialisation du `{formatted_date}`.")
                
                logger.info(f"{member.name} a été banni par {ctx.author.name}. Raison: {reason}")
            except discord.Forbidden:
                await ctx.send("⚠️ Je n'ai pas la permission de bannir ce membre.")
                logger.error(f"Permission insuffisante pour bannir {member.name}")
            except Exception as e:
                await ctx.send(f"⚠️ Erreur lors du bannissement: {str(e)}")
                logger.error(f"Erreur lors du bannissement de {member.name}: {e}")
        except Exception as e:
            logger.error(f"Erreur dans la commande ban: {e}")
            await ctx.send(f"❌ Une erreur est survenue: {str(e)}")

    @commands.command(name="banhistory")
    @commands.has_permissions(administrator=True)
    async def ban_history(self, ctx, member: discord.Member = None):
        """
        Affiche l'historique des bannissements.
        - !banhistory → Montre les 10 derniers bannissements.
        - !banhistory @Pseudo → Montre les bannissements effectués par @Pseudo.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if member:
                # Historique d'un modérateur spécifique
                cursor.execute(
                    "SELECT * FROM ban_history WHERE moderator_id = ? ORDER BY timestamp DESC LIMIT 10",
                    (member.id,)
                )
                title = f"📜 Historique des bannissements de **{member.name}** (10 derniers)"
            else:
                # Historique global
                cursor.execute("SELECT * FROM ban_history ORDER BY timestamp DESC LIMIT 10")
                title = "📜 Historique global des bannissements (10 derniers)"
            
            results = cursor.fetchall()
            conn.close()
            
            if not results:
                await ctx.send("Aucun bannissement trouvé dans l'historique.")
                return
            
            lines = [title]
            for result in results:
                ban_id, mod_id, banned_id, banned_name, reason, timestamp = result
                mod_user = self.bot.get_user(mod_id)
                mod_name = mod_user.name if mod_user else f"<@{mod_id}>"
                
                ban_date = datetime.fromisoformat(timestamp).strftime("%d/%m/%Y %H:%M")
                reason_text = reason if reason else "Aucune raison spécifiée"
                
                lines.append(f"- **{banned_name}** banni par **{mod_name}** le `{ban_date}`")
                lines.append(f"  Raison: *{reason_text}*")
            
            history_message = "\n".join(lines)
            await ctx.send(history_message)
        except Exception as e:
            logger.error(f"Erreur dans la commande banhistory: {e}")
            await ctx.send(f"❌ Une erreur est survenue: {str(e)}")

    @commands.command(name="checkroles")
    @commands.has_permissions(administrator=True)
    async def check_roles(self, ctx):
        """Vérifie tous les modérateurs et retire le rôle à ceux qui ont atteint leur limite."""
        guild = ctx.guild
        ban_role = guild.get_role(self.ban_role_id)
        
        if not ban_role:
            await ctx.send("❌ Rôle de bannissement introuvable.")
            return
        
        try:
            # Récupérer tous les modérateurs depuis la base de données
            moderators = self._get_all_moderators()
            
            count = 0
            for mod_data in moderators:
                # Vérifier si la limite est à 0
                if mod_data["ban_limit"] <= 0:
                    # Récupérer le membre
                    member = guild.get_member(mod_data["user_id"])
                    if member and ban_role in member.roles:
                        try:
                            await member.remove_roles(ban_role)
                            count += 1
                            logger.info(f"Rôle de bannissement retiré à {member.name}")
                        except Exception as e:
                            logger.error(f"Erreur lors du retrait du rôle à {member.name}: {e}")
            
            await ctx.send(f"✅ Rôle de bannissement retiré à {count} membres qui avaient atteint leur limite.")
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des rôles: {e}")
            await ctx.send(f"❌ Une erreur est survenue: {str(e)}")

    @tasks.loop(hours=1)
    async def auto_check_roles(self):
        """Vérifie automatiquement les rôles toutes les heures."""
        try:
            logger.info("Vérification automatique des rôles...")
            
            # Attendre que le bot soit prêt
            await self.bot.wait_until_ready()
            
            # Récupérer tous les modérateurs
            moderators = self._get_all_moderators()
            
            count = 0
            permission_errors = []
            
            for mod_data in moderators:
                # Vérifier si la limite est à 0
                if mod_data["ban_limit"] <= 0:
                    for guild in self.bot.guilds:
                        ban_role = guild.get_role(self.ban_role_id)
                        if not ban_role:
                            continue
                        
                        # Récupérer le membre
                        member = guild.get_member(mod_data["user_id"])
                        if member and ban_role in member.roles:
                            try:
                                await member.remove_roles(ban_role)
                                count += 1
                                logger.info(f"Rôle de bannissement retiré automatiquement à {member.name}")
                            except discord.Forbidden:
                                # Erreur de permission
                                permission_errors.append(member.name)
                                logger.warning(f"Permission insuffisante pour retirer le rôle à {member.name}")
                            except Exception as e:
                                logger.error(f"Erreur lors du retrait automatique du rôle à {member.name}: {e}")
            
            if count > 0:
                logger.info(f"Vérification automatique terminée : {count} rôles retirés")
                
                # Notifier les administrateurs
                admin_channel = self.bot.get_channel(self.admin_channel_id)
                if admin_channel:
                    message = f"⚠️ Vérification automatique : rôle de bannissement retiré à {count} membres qui avaient atteint leur limite."
                    
                    if permission_errors:
                        message += f"\n⛔ Impossible de retirer le rôle à {len(permission_errors)} membres en raison de permissions insuffisantes : {', '.join(permission_errors)}"
                        message += "\nVeuillez vérifier que le rôle du bot est au-dessus du rôle de bannissement dans la hiérarchie."
                    
                    await admin_channel.send(message)
            
            if permission_errors:
                logger.warning(f"Problèmes de permission pour {len(permission_errors)} membres : {', '.join(permission_errors)}")
        except Exception as e:
            logger.error(f"Erreur lors de la vérification automatique des rôles: {e}")

    @commands.Cog.listener()
    async def on_ready(self):
        """Vérifie les permissions du bot au démarrage."""
        logger.info("Vérification des permissions du bot...")
        
        for guild in self.bot.guilds:
            # Vérifier si le bot peut gérer les rôles
            bot_member = guild.get_member(self.bot.user.id)
            if not bot_member.guild_permissions.manage_roles:
                logger.warning(f"Le bot n'a pas la permission 'Gérer les rôles' sur le serveur {guild.name}")
                
                # Notifier les administrateurs
                admin_channel = self.bot.get_channel(self.admin_channel_id)
                if admin_channel:
                    await admin_channel.send("⚠️ **ATTENTION** : Je n'ai pas la permission 'Gérer les rôles'. Certaines fonctionnalités ne fonctionneront pas correctement.")
            
            # Vérifier la hiérarchie des rôles
            ban_role = guild.get_role(self.ban_role_id)
            bot_role = bot_member.top_role
            
            if ban_role and bot_role.position <= ban_role.position:
                logger.warning(f"Le rôle du bot ({bot_role.name}) est en dessous ou au même niveau que le rôle de bannissement ({ban_role.name})")
                
                # Notifier les administrateurs
                admin_channel = self.bot.get_channel(self.admin_channel_id)
                if admin_channel:
                    await admin_channel.send(f"⚠️ **ATTENTION** : Mon rôle ({bot_role.mention}) est en dessous ou au même niveau que le rôle de bannissement ({ban_role.mention}). Je ne pourrai pas retirer ce rôle aux utilisateurs.")

async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
