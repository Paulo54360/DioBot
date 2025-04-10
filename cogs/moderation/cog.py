import discord
from discord.ext import commands
import logging
from .commands.ban_commands import BanCommands
from .commands.utilities_commands import UtilitiesCommands
from .database import ModerationDB

logger = logging.getLogger("moderation")

class ModerationCog(commands.Cog):
    """Cog pour gérer les commandes de modération."""

    def __init__(self, bot):
        self.bot = bot

    async def setup(self):
        """Charge les commandes de bannissement et utilitaires."""
        db = ModerationDB("moderation.db")
        db.init_database()
        await self.bot.add_cog(BanCommands(self.bot, db))
        await self.bot.add_cog(UtilitiesCommands(self.bot))
        
        logger.info("ModerationCog ajouté au bot")

async def setup(bot):
    """Ajoute le cog de modération au bot."""
    db = ModerationDB("moderation.db")
    db.init_database()
    await bot.add_cog(ModerationCog(bot))
    await bot.add_cog(BanCommands(bot, db))
