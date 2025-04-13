import discord
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

class MessageCreate(commands.Cog):
    """Cog pour gérer les événements de création de messages."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        """Événement déclenché lorsqu'un message est créé."""
        if message.author.bot:
            return  # Ignorer les messages des bots
        
        message.reply(f"Message reçu de {message.author}: {message.content}")

        logger.info(f"Message reçu de {message.author}: {message.content}")


async def setup(bot):
    """Ajoute le cog de gestion des messages au bot."""
    await bot.add_cog(MessageCreate(bot))
    logger.info("Loaded MessageCreate listener cog.")
    

