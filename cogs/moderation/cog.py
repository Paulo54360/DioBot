import discord
from discord.ext import commands
from .database import ModerationDB
import logging
from datetime import datetime, timedelta
from .utils import check_and_reset_limit, format_date
import sqlite3

# Configuration du logging
logger = logging.getLogger("moderation")

class ModerationCog(commands.Cog):
    """Gère les bans et leur limite mensuelle."""

    def __init__(self, bot):
        self.bot = bot
        self.db = ModerationDB("moderation.db")
        self.ban_role_id = 1234911574821568595  # ID du rôle de bannissement
        self.admin_channel_id = 1234853264416309310  # ID du salon d'admin
        
        # Initialisation de la base de données
        logger.info(f"Tentative d'initialisation de la base de données: {self.db.db_path}")
        success = self.db.init_database()
        
        if success:
            logger.info("Base de données initialisée avec succès")
        else:
            logger.error("Échec de l'initialisation de la base de données")

    @commands.command(name="ban")
    async def ban_member(self, ctx, member: discord.Member, *, reason=None):
        """Bannit un membre en respectant la limite définie."""
        try:
            # Vérifier si l'utilisateur a le rôle de bannissement ou est administrateur
            ban_role = ctx.guild.get_role(self.ban_role_id)
            logger.info(f"Rôle de bannissement trouvé: {ban_role is not None}")
            if ban_role:
                logger.info(f"L'utilisateur {ctx.author.name} a le rôle: {ban_role in ctx.author.roles}")
            if not (ban_role in ctx.author.roles or ctx.author.guild_permissions.administrator):
                await ctx.send(f"⛔ {ctx.author.mention}, vous n'avez pas le rôle nécessaire pour bannir des membres.")
                return
            
            # Vérifier si la cible est un administrateur ou modérateur
            if member.guild_permissions.administrator or member.guild_permissions.ban_members:
                await ctx.send(f"⛔ {ctx.author.mention}, vous ne pouvez pas bannir un administrateur ou un modérateur.")
                return
            
            # Vérifier si le modérateur a une limite définie
            mod_data = self.db.get_moderator_data(ctx.author.id)
            if not mod_data:
                await ctx.send(
                    f"⛔ {ctx.author.mention}, vous n'avez pas de limite de bans définie. Demandez à un admin d'utiliser `!setban`.")
                return
            
            # Vérifier si la limite doit être réinitialisée
            check_and_reset_limit(self.db, ctx.author.id)
            
            # Récupérer les données mises à jour
            mod_data = self.db.get_moderator_data(ctx.author.id)
            ban_limit = mod_data["ban_limit"]
            
            # Vérifier si le modérateur a atteint sa limite
            if ban_limit <= 0:
                await ctx.send(
                    f"⛔ {ctx.author.mention}, vous avez atteint votre limite de bans. Attendez la réinitialisation ou demandez une augmentation.")
                return
            
            # Bannir l'utilisateur
            try:
                await member.ban(reason=reason or "Aucune raison spécifiée")
                
                # Enregistrer le bannissement dans l'historique
                self.db.add_ban_history(ctx.author.id, member.id, member.name, reason)
                
                # Décrémenter le nombre de bans restants
                new_limit = ban_limit - 1
                self.db.set_moderator_data(
                    ctx.author.id,
                    new_limit,
                    mod_data["initial_limit"],
                    mod_data["reset_date"]
                )
                
                # Formater la date pour l'affichage
                formatted_date = format_date(mod_data["reset_date"])
                
                await ctx.send(
                    f"✅ **{member.name}** a été banni par **{ctx.author.name}**. "
                    f"Il reste `{new_limit}` bans avant la réinitialisation du `{formatted_date}`.")
                
                logger.info(f"{member.name} a été banni par {ctx.author.name}. Raison: {reason}")
                
                # Vérifier si le modérateur a atteint sa limite après ce ban
                if new_limit <= 0:
                    try:
                        await ctx.author.remove_roles(ban_role)
                        await ctx.send(
                            f"⚠️ **{ctx.author.name}**, vous avez atteint votre limite de bans. Le rôle vous a été retiré.")
                        
                        # Notifier dans le canal d'administration
                        admin_channel = ctx.guild.get_channel(self.admin_channel_id)
                        if admin_channel:
                            await admin_channel.send(
                                f"⚠️ **{ctx.author.name}** a atteint sa limite de bans. "
                                f"Le rôle de bannissement lui a été retiré."
                            )
                    except Exception as e:
                        logger.error(f"Erreur lors du retrait du rôle à {ctx.author.name}: {e}")
            except discord.Forbidden:
                await ctx.send("⚠️ Je n'ai pas la permission de bannir ce membre.")
                logger.error(f"Permission insuffisante pour bannir {member.name}")
            except Exception as e:
                await ctx.send(f"⚠️ Erreur lors du bannissement: {str(e)}")
                logger.error(f"Erreur lors du bannissement de {member.name}: {e}")
        except Exception as e:
            logger.error(f"Erreur dans la commande ban: {e}")
            await ctx.send(f"❌ Une erreur est survenue: {str(e)}")

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
            success = self.db.set_moderator_data(user.id, nombre, nombre, reset_date)
            
            if success:
                # Ajouter le rôle de bannissement si nécessaire
                ban_role = ctx.guild.get_role(self.ban_role_id)
                if ban_role and ban_role not in user.roles:
                    await user.add_roles(ban_role)
                    logger.info(f"Rôle de bannissement ajouté à {user.name}")
                
                formatted_date = format_date(reset_date)
                await ctx.send(f"✅ **{user.name}** peut désormais faire `{nombre}` bans. La limite sera réinitialisée le `{formatted_date}`.")
                logger.info(f"Limite de bans définie pour {user.name}: {nombre} bans, reset dans {timeReset} jours")
            else:
                await ctx.send("❌ Une erreur est survenue lors de la définition de la limite de bans.")
                logger.error(f"Échec de la définition de la limite pour {user.name}")
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
                mod_data = self.db.get_moderator_data(member.id)
                if not mod_data:
                    await ctx.send(f"❌ **{member.name}** n'a pas de limite de bans définie.")
                    return
                
                formatted_date = format_date(mod_data["reset_date"])
                await ctx.send(
                    f"📊 **{member.name}** peut encore faire `{mod_data['ban_limit']}` bans. (Reset: `{formatted_date}`)")
            else:
                # Si aucun membre n'est spécifié, on affiche la liste complète
                moderators = self.db.get_all_moderators()
                
                if not moderators:
                    await ctx.send("📊 Aucun modérateur n'a de limite de bans définie.")
                    return
                
                lines = ["📊 **Bannissements restants par modérateur :**"]
                for mod_data in moderators:
                    mod_user = self.bot.get_user(mod_data["user_id"])
                    formatted_date = format_date(mod_data["reset_date"])
                    
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

    @commands.command(name="banhistory")
    @commands.has_permissions(administrator=True)
    async def ban_history(self, ctx, member: discord.Member = None):
        """
        Affiche l'historique des bannissements.
        - !banhistory → Montre les 10 derniers bannissements.
        - !banhistory @Pseudo → Montre les bannissements effectués par @Pseudo.
        """
        try:
            if member:
                # Historique d'un modérateur spécifique
                results = self.db.get_ban_history(member.id)
                title = f"📜 Historique des bannissements de **{member.name}** (10 derniers)"
            else:
                # Historique global
                results = self.db.get_ban_history()
                title = "📜 Historique global des bannissements (10 derniers)"
            
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

    @commands.command(name="dbstats")
    @commands.has_permissions(administrator=True)
    async def db_stats(self, ctx):
        """Affiche des statistiques sur la base de données."""
        try:
            # Statistiques des modérateurs
            moderators = self.db.get_all_moderators()
            mod_count = len(moderators)
            
            # Nombre total de bans
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM ban_history")
            ban_count = cursor.fetchone()[0]
            conn.close()
            
            embed = discord.Embed(
                title="Statistiques de la base de données",
                color=discord.Color.blue()
            )
            embed.add_field(name="Nombre de modérateurs", value=str(mod_count), inline=True)
            embed.add_field(name="Nombre total de bannissements", value=str(ban_count), inline=True)
            
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Erreur dans la commande dbstats: {e}")
            await ctx.send(f"❌ Une erreur est survenue: {str(e)}")

    @commands.command(name="checkroles")
    @commands.has_permissions(administrator=True)
    async def check_roles(self, ctx):
        """Vérifie tous les modérateurs et retire le rôle à ceux qui ont atteint leur limite."""
        try:
            guild = ctx.guild
            ban_role = guild.get_role(self.ban_role_id)
            
            if not ban_role:
                await ctx.send("❌ Rôle de bannissement introuvable.")
                return
            
            # Récupérer tous les modérateurs
            moderators = self.db.get_all_moderators()
            
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
            logger.error(f"Erreur dans la commande checkroles: {e}")
            await ctx.send(f"❌ Une erreur est survenue: {str(e)}")

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        """Détecte les bannissements, y compris ceux effectués manuellement."""
        try:
            # Récupérer les logs d'audit pour trouver qui a effectué le ban
            async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=1):
                if entry.target.id == user.id:
                    moderator = entry.user
                    reason = entry.reason or "Aucune raison spécifiée"
                    
                    # Vérifier si le modérateur est dans notre système
                    mod_data = self.db.get_moderator_data(moderator.id)
                    if mod_data and moderator.id != self.bot.user.id:  # Ignorer les bans effectués par le bot lui-même
                        # Vérifier si le modérateur a le rôle de bannissement
                        ban_role = guild.get_role(self.ban_role_id)
                        if ban_role in moderator.roles:
                            # Enregistrer le bannissement dans l'historique
                            self.db.add_ban_history(moderator.id, user.id, user.name, reason)
                            
                            # Décrémenter le nombre de bans restants
                            new_limit = mod_data["ban_limit"] - 1
                            self.db.set_moderator_data(
                                moderator.id,
                                new_limit,
                                mod_data["initial_limit"],
                                mod_data["reset_date"]
                            )
                            
                            # Notifier dans le canal d'administration
                            admin_channel = guild.get_channel(self.admin_channel_id)
                            if admin_channel:
                                await admin_channel.send(
                                    f"📝 **{moderator.name}** a banni **{user.name}** manuellement. "
                                    f"Ce ban a été comptabilisé. Il lui reste `{new_limit}` bans."
                                )
                            
                            # Vérifier si le modérateur a atteint sa limite
                            if new_limit <= 0:
                                # Retirer le rôle de bannissement
                                try:
                                    await moderator.remove_roles(ban_role)
                                    
                                    # Notifier dans le canal d'administration
                                    if admin_channel:
                                        await admin_channel.send(
                                            f"⚠️ **{moderator.name}** a atteint sa limite de bans. "
                                            f"Le rôle de bannissement lui a été retiré."
                                        )
                                except Exception as e:
                                    logger.error(f"Erreur lors du retrait du rôle à {moderator.name}: {e}")
                    
                    # On a trouvé l'entrée correspondante, on peut sortir de la boucle
                    break
        except Exception as e:
            logger.error(f"Erreur lors de la détection d'un bannissement: {e}")

async def setup(bot):
    """Fonction appelée par Discord.py pour charger le cog."""
    await bot.add_cog(ModerationCog(bot))
    logger.info("ModerationCog ajouté au bot")