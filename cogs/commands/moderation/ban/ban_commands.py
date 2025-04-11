import discord
from discord.ext import commands
from discord import app_commands, Interaction, Member
from datetime import datetime, timedelta
import os
import sqlite3
import logging

from cogs.database.database import ModerationDB

logger = logging.getLogger(__name__)

class BanCommands(commands.Cog):
    """Commandes liées au bannissement."""

    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    @app_commands.command(name="ban", description="Bannit un membre.")
    async def ban_member(self, interaction: Interaction, member: Member, *, reason: str = None):
        """Bannit un membre du serveur."""
        # Vérifier les droits du modérateur
        moderator_data = self.db.get_moderator_data(interaction.user.id)
        
        if not moderator_data:
            await interaction.response.send_message("❌ Vous n'avez pas les droits pour bannir des membres ou les données sont incomplètes.", ephemeral=True)
            return
        
        # Vérifier le nombre de bans restants
        ban_limit = moderator_data.get("ban_limit", 0)
        
        if ban_limit <= 0:
            await interaction.response.send_message("❌ Vous avez atteint votre limite de bans pour cette période.", ephemeral=True)
            return
            
        # Vérifier si le membre peut être banni
        try:
            # Vérifier les permissions avant de bannir
            if not interaction.guild.me.guild_permissions.ban_members:
                await interaction.response.send_message("❌ Je n'ai pas les permissions nécessaires pour bannir ce membre.", ephemeral=True)
                return
                
            # Effectuer le bannissement
            await interaction.guild.ban(member, reason=reason)
            
            # Mettre à jour le nombre de bans restants
            self.db.update_moderator_ban_limit(interaction.user.id, ban_limit - 1)
            
            # Enregistrer le bannissement dans l'historique
            self.db.add_ban_to_history(interaction.user.id, member.id, member.name, reason)
            
            await interaction.response.send_message(f"✅ {member.name} a été banni. Raison: {reason}")
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ Vous n'avez pas la permission de bannir ce membre.", ephemeral=True)
        except discord.HTTPException as e:
            logger.error(f"Erreur lors du bannissement: {e}")
            await interaction.response.send_message("❌ Une erreur est survenue lors du bannissement.", ephemeral=True)
        except Exception as e:
            logger.error(f"Erreur inattendue: {e}")
            if ban_limit <= 0:
                reset_date = datetime.fromisoformat(moderator_data["reset_date"])
                time_remaining = reset_date - datetime.utcnow()
                days_remaining = time_remaining.days
                await interaction.response.send_message(f"❌ Vous avez atteint votre limite de bans. Vous devez attendre encore {days_remaining} jours.", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Une erreur inattendue est survenue.", ephemeral=True)

    @app_commands.command(name="setban", description="Définit le nombre de bans et le timer de réinitialisation pour un utilisateur.")
    async def set_ban(self, interaction: Interaction, user: Member, initial_number_ban: int, timer_reset: int):
        """Définit le nombre de bans et le timer de réinitialisation pour un utilisateur."""
        admin_role_id = int(os.getenv('ADMIN_ROLE_ID', 0))

        if admin_role_id not in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message("❌ Vous n'avez pas la permission de définir des bans.", ephemeral=True)
            return

        reset_date = (datetime.utcnow() + timedelta(days=timer_reset)).isoformat()

        # Récupérez le pseudo du membre
        username = user.display_name  # Utilisez le nom d'affichage du membre

        success = self.db.set_moderator_data(user.id, initial_number_ban, initial_number_ban, reset_date, username)
        
        if success:
            await interaction.response.send_message(f"✅ Le nombre de bans pour {username} a été défini à {initial_number_ban} avec un timer de réinitialisation de {timer_reset} jours.")
        else:
            await interaction.response.send_message("❌ Échec de la mise à jour des données.", ephemeral=True)

    @app_commands.command(name="banhistory", description="Affiche l'historique des bans.")
    async def ban_history(self, interaction, user: Member = None):
        """Affiche l'historique des bans pour un utilisateur spécifique ou pour tous les utilisateurs."""
        ban_history_records = []  # Initialisation par défaut

        if user:
            ban_history_records = self.db.get_ban_history(moderator_id=user.id)
        else:
            ban_history_records = self.db.get_all_ban_history()

        if not ban_history_records:
            await interaction.response.send_message("❌ Aucun historique de bans trouvé.", ephemeral=True)
            return

        response = "Historique des bans :\n"
        for record in ban_history_records:
            if len(record) == 6:  # Vérifiez que vous avez 6 colonnes
                ban_id, moderator_id, banned_user_id, banned_user_name, reason, timestamp = record
                response += f"**Banni par** : <@{moderator_id}> | **Banni** : {banned_user_name} | **Raison** : {reason} | **Date** : {timestamp}\n"
            else:
                logger.warning(f"Enregistrement inattendu dans l'historique des bans: {record}")

        await interaction.response.send_message(response)

    @app_commands.command(name="banlimits", description="Affiche la liste des bans restants pour tous les modérateurs.")
    async def ban_limits(self, interaction: Interaction):
        """Affiche la liste des bans restants pour tous les modérateurs."""
        moderators = self.db.get_all_moderators_with_ban_limits()

        if not moderators:
            await interaction.response.send_message("❌ Aucun modérateur trouvé.", ephemeral=True)
            return

        response = "Liste des bans restants pour les modérateurs :\n"
        for username, ban_limit, reset_date in moderators:
            if reset_date:
                reset_datetime = datetime.fromisoformat(reset_date)
                time_remaining = reset_datetime - datetime.utcnow()
                days_remaining = time_remaining.days
                hours_remaining = time_remaining.seconds // 3600
                minutes_remaining = (time_remaining.seconds // 60) % 60
                time_left = f"{days_remaining} jours, {hours_remaining} heures, {minutes_remaining} minutes"
            else:
                time_left = "N/A"  # Si aucune date de réinitialisation n'est disponible

            response += f"**Modérateur** : {username} | **Bans restants** : {ban_limit} | **Temps restant avant réinitialisation** : {time_left}\n"

        await interaction.response.send_message(response)

async def setup(bot):
    """Ajoute les commandes de bannissement au bot."""
    db = ModerationDB("moderation.db")  # Chemin vers votre base de données
    db.init_database()  # Initialisez la base de données
    await bot.add_cog(BanCommands(bot, db))  # Ajoutez le cog de bannissement