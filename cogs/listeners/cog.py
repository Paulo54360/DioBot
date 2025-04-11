import discord
from discord.ext import commands
import logging
from .messages import MessageCreate, MessageDelete



logger = logging.getLogger("listeners")

class ListenersCog(commands.Cog):
    """Cog pour gérer les événements."""

    def __init__(self, bot):
        self.bot = bot

    async def setup(self):
        """Charge les listeners."""
        await self.bot.add_cog(MessageCreate(self.bot))
        await self.bot.add_cog(MessageDelete(self.bot))
        logger.info("ListenersCog ajouté au bot")

async def setup(bot):
    """Ajoute le cog de listeners au bot."""
    await bot.add_cog(ListenersCog(bot))
    await bot.add_cog(MessageCreate(bot))
    await bot.add_cog(MessageDelete(bot))
    logger.info("ListenersCog ajouté au bot")
    
