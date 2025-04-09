import os
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import logging
from cogs.moderation.utils import format_date, check_and_reset_limit
from dotenv import load_dotenv

load_dotenv()
BAN_ROLE_ID = os.getenv("BAN_ROLE_ID")
ADMIN_ROLE_ID = os.getenv("ADMIN_ROLE_ID")

logger = logging.getLogger("moderation")


class BanCommands(commands.Cog):
    """Commandes liées au bannissement."""

    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    def get_ban_role(self, guild):
        """Récupère le rôle de bannissement."""
        return guild.get_role(int(BAN_ROLE_ID))

    def get_admin_role(self, guild):
        """Récupère le rôle d'administrateur."""
        return guild.get_role(int(ADMIN_ROLE_ID))

    @app_commands.command(name="ban", description="Bannit un membre en respectant la limite définie.")
    async def ban_member(self, interaction: discord.Interaction, member: discord.Member, *, reason: str = None):
        """
        Bannit un membre si le modérateur a des permissions et une limite de bans.
        - !ban @Utilisateur [raison] → Bannit l'utilisateur avec la raison spécifiée
        """
        
        try:
            ban_role = self.get_ban_role(interaction.guild)
            if not ban_role:
                return await interaction.response.send_message("❌ Rôle de bannissement introuvable. Veuillez vérifier la configuration.")

            # Vérifie si l'utilisateur a le rôle de bannissement
            if ban_role not in interaction.user.roles:
                return await interaction.response.send_message("⛔ Tu n'as pas les permissions pour effectuer cette action.")

            # Vérifie si la cible est un administrateur ou modérateur
            if member.guild_permissions.administrator or member.guild_permissions.ban_members:
                return await interaction.response.send_message("⛔ Tu n'as pas les permissions pour bannir un administrateur.")

            # Vérifie la limite de bans du modérateur
            mod_data = self.db.get_moderator_data(interaction.user.id)
            if not mod_data or mod_data["ban_limit"] <= 0:
                return await interaction.response.send_message("⛔ Limite de bans atteinte ou non définie.")

            # Bannit l'utilisateur et met à jour l'historique
            await member.ban(reason=reason or "Aucune raison spécifiée")
            self.db.add_ban_history(interaction.user.id, member.id, member.name, reason)
            new_limit = mod_data["ban_limit"] - 1
            self.db.set_moderator_data(interaction.user.id, new_limit, mod_data["initial_limit"], mod_data["reset_date"])
            formatted_date = format_date(mod_data["reset_date"])
            await interaction.response.send_message(f"✅ **{member.name}** banni par **{interaction.user.name}**. Restant: `{new_limit}` bans avant réinitialisation le `{formatted_date}`.")
            
            # Retire le rôle si la limite est atteinte
            if new_limit <= 0:
                await interaction.user.remove_roles(ban_role)
                await interaction.response.send_message(f"⚠️ **{interaction.user.name}**, rôle retiré, limite de bans atteinte.")

            # Check and reset limit
            check_and_reset_limit(self.db, interaction.user.id)
        except discord.Forbidden:
            await interaction.response.send_message("⚠️ Permission insuffisante pour bannir ce membre.")
        except Exception as e:
            await interaction.response.send_message(f"⚠️ Erreur lors du bannissement: {str(e)}")

    @app_commands.command(name="setban", description="Définit la limite de bans pour un modérateur.")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_ban_limit(self, interaction: discord.Interaction, user: discord.Member, nombre: int, time_reset: int):
        """
        Définit la limite de bans pour un modérateur.
        - !setban @Utilisateur nombre jours → Définit la limite de bans et la date de réinitialisation
        """
        try:
            admin_role = self.get_admin_role(interaction.guild)
            
            # Vérifiez si l'utilisateur a le rôle d'administrateur
            if admin_role not in interaction.user.roles:
                return await interaction.response.send_message("⛔ Tu n'as pas les permissions pour effectuer cette action.")
            
            ban_role = self.get_ban_role(interaction.guild)
            if not ban_role:
                return await interaction.response.send_message("❌ Rôle de bannissement introuvable. Veuillez vérifier la configuration.")

            # Calculer la date de réinitialisation
            reset_date = (datetime.utcnow() + timedelta(days=time_reset)).isoformat()
            
            # Mettre à jour les données du modérateur
            success = self.db.set_moderator_data(
                moderator_id=user.id, 
                new_ban_limit=nombre, 
                initial_ban_limit=nombre, 
                ban_reset_date=reset_date
            )
            
            if not success:
                await interaction.response.send_message("❌ Une erreur est survenue lors de la définition de la limite de bans.")
                logger.error(f"Échec de la définition de la limite pour {user.name}")
                return

            # Ajouter le rôle de bannissement si nécessaire
            if ban_role and ban_role not in user.roles:
                await user.add_roles(ban_role)
                logger.info(f"Rôle de bannissement ajouté à {user.name}")

            formatted_date = format_date(reset_date)
            await interaction.response.send_message(f"✅ **{user.name}** peut désormais faire `{nombre}` bans. La limite sera réinitialisée le `{formatted_date}`.")
            logger.info(f"Limite de bans définie pour {user.name}: {nombre} bans, reset dans {time_reset} jours")
        except Exception as e:
            logger.error(f"Erreur dans la commande setban: {e}")
            await interaction.response.send_message(f"❌ Une erreur est survenue: {str(e)}")

    @app_commands.command(name="banstats", description="Affiche les bans restants pour les modérateurs.")
    async def ban_stats(self, interaction: discord.Interaction, member: discord.Member = None):
        """
        Affiche les bans restants pour un modérateur ou tous les modérateurs.
        - !banstats → Affiche les statistiques de tous les modérateurs
        - !banstats @Utilisateur → Affiche les statistiques d'un modérateur spécifique
        """
        try:
            ban_role = self.get_ban_role(interaction.guild)
            if not ban_role:
                return await interaction.response.send_message("❌ Rôle de bannissement introuvable. Veuillez vérifier la configuration.")

            # Vérification des permissions de l'utilisateur
            if not interaction.user.guild_permissions.administrator:
                return await interaction.response.send_message("⛔ Tu n'as pas les permissions pour effectuer cette action.")

            # Si aucun membre n'est spécifié, on affiche la liste complète des modérateurs
            moderators = self.db.get_all_moderators()
            logger.info(f"Modérateurs récupérés: {moderators}")
            if not moderators:
                return await interaction.response.send_message("📊 Aucun modérateur n'a de limite de bans définie.")
            
            lines = ["📊 **Bannissements restants par modérateur :**"]
            for mod_data in moderators:
                mod_user = self.bot.get_user(mod_data["user_id"])
                formatted_date = format_date(mod_data["reset_date"])
                user_name = mod_user.name if mod_user else f"<@{mod_data['user_id']}>"
                lines.append(
                    f"- **{user_name}** : `{mod_data['ban_limit']}` bans restants (Reset: `{formatted_date}`)"
                )
            
            stats_message = "\n".join(lines)
            await interaction.response.send_message(stats_message)

            # Si un membre est spécifié, on affiche uniquement ses infos
            if member:
                mod_data = self.db.get_moderator_data(member.id)
                if not mod_data:
                    return await interaction.response.send_message(f"❌ **{member.name}** n'a pas de limite de bans définie.")
                
                formatted_date = format_date(mod_data["reset_date"])
                return await interaction.response.send_message(
                    f"📊 **{member.name}** peut encore faire `{mod_data['ban_limit']}` bans. (Reset: `{formatted_date}`)"
                )
        except Exception as e:
            logger.error(f"Erreur dans la commande banstats: {e}")
            await interaction.response.send_message(f"❌ Une erreur est survenue: {str(e)}")

    @app_commands.command(name="banhistory", description="Affiche l'historique des bannissements.")
    async def ban_history(self, interaction: discord.Interaction, member: discord.Member = None):
        """Affiche l'historique des bannissements."""
        try:
            ban_role = self.get_ban_role(interaction.guild)
            if not ban_role:
                return await interaction.response.send_message("❌ Rôle de bannissement introuvable. Veuillez vérifier la configuration.")

            # Historique global
            results = self.db.get_ban_history()
            if not results:
                return await interaction.response.send_message("Aucun bannissement trouvé dans l'historique.")
            
            lines = ["📜 Historique global des bannissements (10 derniers)"]
            for result in results:
                ban_id, mod_id, banned_id, banned_name, reason, timestamp = result
                mod_user = self.bot.get_user(mod_id)
                mod_name = mod_user.name if mod_user else f"<@{mod_id}>"
                
                ban_date = datetime.fromisoformat(timestamp).strftime("%d/%m/%Y %H:%M")
                reason_text = reason if reason else "Aucune raison spécifiée"
                
                lines.append(f"- **{banned_name}** banni par **{mod_name}** le `{ban_date}`")
                lines.append(f"  Raison: *{reason_text}*")
            
            await interaction.response.send_message("\n".join(lines))

            # Historique d'un modérateur spécifique
            if member:
                results = self.db.get_ban_history(member.id)
                title = f"📜 Historique des bannissements de **{member.name}** (10 derniers)"
                if not results:
                    return await interaction.response.send_message(f"Aucun bannissement trouvé pour {member.name}.")
                
                lines = [title]
                for result in results:
                    ban_id, mod_id, banned_id, banned_name, reason, timestamp = result
                    mod_user = self.bot.get_user(mod_id)
                    mod_name = mod_user.name if mod_user else f"<@{mod_id}>"
                    
                    ban_date = datetime.fromisoformat(timestamp).strftime("%d/%m/%Y %H:%M")
                    reason_text = reason if reason else "Aucune raison spécifiée"
                    
                    lines.append(f"- **{banned_name}** banni par **{mod_name}** le `{ban_date}`")
                    lines.append(f"  Raison: *{reason_text}*")
                
                return await interaction.response.send_message("\n".join(lines))
        except discord.app_commands.errors.MissingPermissions:
            await interaction.response.send_message("⛔ Tu n'as pas les permissions pour effectuer cette action.")
        except Exception as e:
            logger.error(f"Erreur dans la commande banhistory: {e}")
            await interaction.response.send_message(f"❌ Une erreur est survenue: {str(e)}")

    @app_commands.command(name="checkroles", description="Vérifie et retire les rôles des modérateurs ayant atteint leur limite.")
    async def check_roles(self, interaction: discord.Interaction):
        """Vérifie tous les modérateurs et retire le rôle à ceux qui ont atteint leur limite."""
        try:
            guild = interaction.guild
            ban_role = guild.get_role(BAN_ROLE_ID)
            
            # Vérification si le rôle de bannissement existe
            if not ban_role:
                return await interaction.response.send_message("❌ Rôle de bannissement introuvable. Veuillez vérifier la configuration.")
            
            # Vérification des permissions de l'utilisateur
            if not interaction.user.guild_permissions.administrator:
                return await interaction.response.send_message("⛔ Tu n'as pas les permissions pour effectuer cette action.")
            
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
            
            await interaction.response.send_message(f"✅ Rôle de bannissement retiré à {count} membres qui avaient atteint leur limite.")
        except Exception as e:
            logger.error(f"Erreur dans la commande checkroles: {e}")
            await interaction.response.send_message(f"❌ Une erreur est survenue: {str(e)}")

async def setup(bot):
    """Ajoute les commandes de bannissement au bot."""
    await bot.add_cog(BanCommands(bot))

