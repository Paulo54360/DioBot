import unittest
from unittest.mock import MagicMock, patch
import discord
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio
from cogs.moderation.cog import ModerationCog

class TestModerationCommands(unittest.TestCase):
    """Tests pour les commandes de modération."""
    
    def setUp(self):
        """Initialisation avant chaque test."""
        # Créer un bot mock
        self.bot = MagicMock(spec=commands.Bot)
        
        # Patcher la classe ModerationDB
        self.db_patcher = patch('cogs.moderation.database.ModerationDB')
        self.mock_db_class = self.db_patcher.start()
        self.mock_db = self.mock_db_class.return_value
        
        # Configurer le mock de la base de données
        self.mock_db.init_database.return_value = True
        
        # Créer le cog avec le bot mock
        self.cog = ModerationCog(self.bot)
        
        # Remplacer la base de données du cog par notre mock
        self.cog.db = self.mock_db
    
    def tearDown(self):
        """Nettoyage après chaque test."""
        self.db_patcher.stop()
    
    def test_ban_member_success(self):
        """Test de la commande ban_member avec succès."""
        # Créer des mocks pour ctx, member, etc.
        ctx = MagicMock(spec=commands.Context)
        member = MagicMock(spec=discord.Member)
        guild = MagicMock(spec=discord.Guild)
        author = MagicMock(spec=discord.Member)
        ban_role = MagicMock(spec=discord.Role)
        
        # Configurer les mocks
        ctx.guild = guild
        ctx.author = author
        guild.get_role.return_value = ban_role
        
        # Corriger cette ligne
        author.roles = [ban_role]  # Maintenant ban_role est dans la liste des rôles de l'auteur
        
        author.guild_permissions.administrator = False
        member.guild_permissions.administrator = False
        member.guild_permissions.ban_members = False
        
        # Configurer le mock de la base de données
        reset_date = (datetime.utcnow() + timedelta(days=30)).isoformat()
        self.mock_db.get_moderator_data.return_value = {
            "user_id": author.id,
            "ban_limit": 5,
            "initial_limit": 10,
            "reset_date": reset_date
        }
        
        # Configurer le mock de member.ban pour qu'il retourne une coroutine résolue
        async def mock_ban(*args, **kwargs):
            return None
        member.ban = MagicMock(side_effect=mock_ban)
        
        # Configurer le mock de ctx.send pour qu'il retourne une coroutine résolue
        async def mock_send(*args, **kwargs):
            return None
        ctx.send = MagicMock(side_effect=mock_send)
        
        # Exécuter la coroutine ban_member
        # Nous devons accéder à la méthode callback directement, pas à la commande
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.cog.ban_member.callback(self.cog, ctx, member, reason="Test reason"))
        
        # Vérifier que les méthodes attendues ont été appelées
        member.ban.assert_called_once()
        self.mock_db.add_ban_history.assert_called_once()
        self.mock_db.set_moderator_data.assert_called_once()
        ctx.send.assert_called_once()
    
    # Ajoutez d'autres tests pour les commandes restantes...

if __name__ == "__main__":
    unittest.main() 