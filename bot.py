import discord
from discord.ext import commands
import logging
import os
import asyncio
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot")

# Récupérer le token depuis les variables d'environnement
TOKEN = os.getenv('DISCORD_TOKEN')

# Configuration des intents (permissions)
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Création du bot
bot = commands.Bot(command_prefix="/", intents=intents)

async def load_extensions():
    """Charge tous les cogs du bot."""
    try:
        await bot.load_extension("cogs.moderation")
        logger.info("Module de modération chargé.")
    except Exception as e:
        logger.error(f"Erreur lors du chargement du module de modération: {e}")

@bot.event
async def on_ready():
    logger.info(f"Bot connecté: {bot.user.name} (ID: {bot.user.id})")

    # Synchroniser les commandes slash
    try:
        synced = await bot.tree.sync()
        logger.info(f"Commandes synchronisées: {len(synced)}")

        # Afficher uniquement les détails des commandes synchronisées
        for command in synced:
            logger.info(f"Commande synchronisée: {command.name} - Description: {command.description}")

    except Exception as e:
        logger.error(f"Erreur lors de la synchronisation des commandes: {e}")

# Fonction principale asynchrone
async def main():
    await load_extensions()
    await bot.start(TOKEN)

# Lancement du bot
if __name__ == "__main__":
    asyncio.run(main())
