import unittest
from unittest.mock import MagicMock
import discord
from discord.ext import commands
from cogs.moderation.cog import ModerationCog  # Assurez-vous que le chemin est correct

class TestModerationCommands(unittest.IsolatedAsyncioTestCase):
    """Tests pour les commandes de modération."""

    def setUp(self):
        """Configurer les mocks et l'environnement de test."""
        self.bot = MagicMock(spec=commands.Bot)
        self.cog = ModerationCog(self.bot)  # Instanciez votre classe de commandes
        self.mock_db = MagicMock()  # Simuler la base de données
        self.cog.db = self.mock_db  # Assurez-vous que votre cog utilise le mock de la base de données

    async def test_ban_member_by_admin(self):
        """Test que la commande ban_member peut être utilisée par un administrateur."""
        # Créer un mock pour ctx et member
        ctx = MagicMock(spec=commands.Context)
        member = MagicMock(spec=discord.Member)
        admin_role = MagicMock(spec=discord.Role)
        
        # Configurer les mocks
        ctx.author = MagicMock(spec=discord.Member)
        ctx.author.roles = [admin_role]
        admin_role.permissions.administrator = True
        
        # Simuler le comportement de la base de données
        self.mock_db.get_moderator_data.return_value = {
            "user_id": ctx.author.id,
            "ban_limit": 5,
            "initial_limit": 10,
            "reset_date": "2023-12-31T23:59:59"
        }
        
        # Exécuter la commande
        await self.cog.ban_member(ctx, member, reason="Test reason")
        
        # Vérifier que le ban a été effectué
        member.ban.assert_called_once()
        self.mock_db.add_ban_history.assert_called_once()
        self.mock_db.set_moderator_data.assert_called_once()

    async def test_ban_count_increments(self):
        """Test que le compteur de bans s'incrémente correctement."""
        ctx = MagicMock(spec=commands.Context)
        member = MagicMock(spec=discord.Member)
        admin_role = MagicMock(spec=discord.Role)
        
        # Configurer les mocks
        ctx.author = MagicMock(spec=discord.Member)
        ctx.author.roles = [admin_role]
        admin_role.permissions.administrator = True
        
        # Simuler le comportement de la base de données
        self.mock_db.get_moderator_data.return_value = {
            "user_id": ctx.author.id,
            "ban_limit": 5,
            "initial_limit": 10,
            "reset_date": "2023-12-31T23:59:59"
        }
        
        # Exécuter la commande de ban
        await self.cog.ban_member(ctx, member, reason="Test reason")
        
        # Vérifier que le compteur de bans a été incrémenté
        self.mock_db.set_moderator_data.assert_called_once_with(ctx.author.id, {
            "ban_limit": 4,  # S'assurer que le compteur a été décrémenté
            "initial_limit": 10,
            "reset_date": "2023-12-31T23:59:59"
        })

    async def test_ban_count_reload(self):
        """Test que le rechargement du nombre de bans fonctionne."""
        ctx = MagicMock(spec=commands.Context)
        member = MagicMock(spec=discord.Member)
        admin_role = MagicMock(spec=discord.Role)
        
        # Configurer les mocks
        ctx.author = MagicMock(spec=discord.Member)
        ctx.author.roles = [admin_role]
        admin_role.permissions.administrator = True
        
        # Simuler le comportement de la base de données
        self.mock_db.get_moderator_data.return_value = {
            "user_id": ctx.author.id,
            "ban_limit": 5,
            "initial_limit": 10,
            "reset_date": "2023-12-31T23:59:59"
        }
        
        # Exécuter la commande de rechargement
        await self.cog.set_ban_limit(ctx, ctx.author, 10, 30)
        
        # Vérifier que le compteur de bans a été réinitialisé
        self.mock_db.set_moderator_data.assert_called_once_with(ctx.author.id, {
            "ban_limit": 10,  # S'assurer que le compteur a été réinitialisé
            "initial_limit": 10,
            "reset_date": "2023-12-31T23:59:59"
        })

if __name__ == '__main__':
    unittest.main()
