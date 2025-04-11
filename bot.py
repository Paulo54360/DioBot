import discord
from discord.ext import commands
import logging
import os
import asyncio
from dotenv import load_dotenv
from keep_alive import keep_alive
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
        await bot.load_extension("cogs.listeners")
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
    keep_alive()
    await load_extensions()
    await bot.start(TOKEN)

# Lancement du bot
if __name__ == "__main__":
    try:
        # Lance la boucle d'événements asyncio avec la fonction main
        asyncio.run(main())
    except KeyboardInterrupt:
        # Gère l'arrêt manuel (Ctrl+C)
        logger.info("Arrêt du bot demandé par l'utilisateur (KeyboardInterrupt).")
    except discord.LoginFailure:
        logger.critical("ERREUR CRITIQUE: Échec de la connexion - Token Discord invalide.")
    except Exception as e:
        # Attrape toute autre erreur critique non gérée pendant l'exécution
        logger.critical(f"Erreur critique non gérée lors de l'exécution du bot:", exc_info=e)
