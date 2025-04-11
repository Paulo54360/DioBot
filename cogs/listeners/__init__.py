import logging

from .messages.messageCreate import MessageCreate
from .messages.messageDelete import MessageDelete


logger = logging.getLogger(__name__)

async def setup(bot):
    """Adds the listener cogs to the bot."""
    await bot.add_cog(MessageCreate(bot))
    await bot.add_cog(MessageDelete(bot))
    logger.info("Loaded MessageCreate listener cog.")


# Facultatif: si vous souhaitez exposer des choses pour l'importation directe du package plus tard
# __all__ = ["MessageCreate", "setup"]
