import discord
from discord import app_commands
from discord.ext import commands

class UtilitiesCommands(commands.Cog):
    """Commandes utilitaires générales."""

    def __init__(self, bot):
        self.bot = bot
        # Enregistrer la commande slash dans l'arbre des commandes
        self.bot.tree.add_command(self.list_commands)

    @app_commands.command(name="list_commands", description="Liste toutes les commandes disponibles avec leurs descriptions.")
    async def list_commands(self, interaction: discord.Interaction):
        """Affiche toutes les commandes chargées avec leurs descriptions."""
        commands_list = [f"{command.name}: {command.description}" for command in self.bot.tree.get_commands()]
        if commands_list:
            await interaction.response.send_message("Voici les commandes disponibles :\n" + "\n".join(commands_list))
        else:
            await interaction.response.send_message("Aucune commande disponible.")

# Fonction pour ajouter le cog
async def setup(bot):
    await bot.add_cog(UtilitiesCommands(bot))