from .cog import setup
from cogs.database import ModerationDB

# Cette ligne est importante pour que Discord.py puisse charger le cog

async def setup(bot):
    from .cog import setup
    await setup(bot) 