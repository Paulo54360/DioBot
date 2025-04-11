import discord
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)


class MessageDelete(commands.Cog):
    """Cog pour gérer les événements de suppression de messages."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Événement déclenché lorsqu'un message est supprimé."""

        if message.author.bot:
            return  # Ignorer les messages des bots
        

        channel_id = message.channel.id
        channel = self.bot.get_channel(channel_id)

        

        await channel.send(f"Message supprimé: {message.content} de {message.author}")

        logger.info(f"Message supprimé: {message.content}")

async def setup(bot):
    """Ajoute le cog de gestion des messages au bot."""
    await bot.add_cog(MessageDelete(bot))
    logger.info("Loaded MessageDelete listener cog.")
    

