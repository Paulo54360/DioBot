import discord
from discord.ext import commands
import asyncio
import os
import logging
import json
import sqlite3
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# Récupérer le token depuis les variables d'environnement
TokenBotDiscord = os.getenv('DISCORD_TOKEN')

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("bot")

# Configuration des intents (permissions)
intents = discord.Intents.default()
intents.members = True  # Nécessaire pour accéder aux membres du serveur
intents.message_content = True  # Nécessaire pour lire le contenu des messages

# Création du bot
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logger.info(f"Bot connecté en tant que {bot.user.name}")
    logger.info(f"ID du bot: {bot.user.id}")
    logger.info(f"Discord.py version: {discord.__version__}")
    
    # Afficher les cogs chargés
    loaded_cogs = list(bot.cogs.keys())
    logger.info(f"Cogs chargés: {loaded_cogs}")
    
    # Afficher les commandes disponibles
    commands_list = [command.name for command in bot.commands]
    logger.info(f"Commandes disponibles: {commands_list}")
    
    logger.info("------")

async def load_extensions():
    """Charge tous les cogs du bot."""
    try:
        # Charger le module de modération
        logger.info("Tentative de chargement du module cogs.moderation...")
        await bot.load_extension("cogs.moderation")
        logger.info("Module de modération chargé avec succès")
        
        # Vérifier si le cog est bien chargé
        if "ModerationCog" in bot.cogs:
            logger.info("ModerationCog est bien présent dans les cogs")
            logger.info(f"Commandes du cog: {[c.name for c in bot.get_cog('ModerationCog').get_commands()]}")
        else:
            logger.error("ModerationCog n'est pas dans les cogs malgré le chargement réussi")
            logger.info(f"Cogs disponibles: {list(bot.cogs.keys())}")
    except Exception as e:
        logger.error(f"Erreur lors du chargement du module de modération: {e}")
        logger.error(f"Type d'erreur: {type(e).__name__}")
        import traceback
        logger.error(traceback.format_exc())

# Commande de test pour vérifier que le bot fonctionne
@bot.command(name="test")
async def test_command(ctx):
    """Commande de test."""
    await ctx.send("✅ La commande de test fonctionne !")

async def main():
    """Fonction principale qui démarre le bot."""
    # Get the Discord token from environment variable
    token = TokenBotDiscord
    if not token:
        logger.error("No Discord token found! Please set the DISCORD_TOKEN environment variable.")
        return
        
    async with bot:
        await load_extensions()
        await bot.start(token)

# Lancement du bot
if __name__ == "__main__":
    asyncio.run(main())
