import unittest
from unittest.mock import AsyncMock, MagicMock
from discord import Member
from cogs.commands.moderation.ban.ban_commands import BanCommands

class TestBanCommands(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.bot = AsyncMock()
        self.db = MagicMock()
        self.ban_commands = BanCommands(self.bot, self.db)

    async def test_ban_member_success(self):
        interaction = AsyncMock()
        member = AsyncMock(spec=Member)
        member.id = 123
        member.name = "TestUser"
        interaction.user.id = 456
        interaction.guild.ban = AsyncMock()
        interaction.guild.me.guild_permissions.ban_members = True
        interaction.response.send_message = AsyncMock()

        self.db.get_moderator_data.return_value = {"ban_limit": 1, "reset_date": None}
        self.db.update_moderator_ban_limit = AsyncMock()
        self.db.add_ban_to_history = AsyncMock()

        await self.ban_commands.ban_member(interaction, member)

        interaction.guild.ban.assert_called_once_with(member, reason=None)
        self.db.update_moderator_ban_limit.assert_called_once_with(456, 0)
        self.db.add_ban_to_history.assert_called_once_with(456, 123, "TestUser", None)
        interaction.response.send_message.assert_called_once_with("✅ TestUser a été banni.")

    async def test_ban_member_no_permission(self):
        interaction = AsyncMock()
        member = AsyncMock(spec=Member)
        interaction.user.id = 456
        interaction.guild.me.guild_permissions.ban_members = False
        interaction.response.send_message = AsyncMock()

        await self.ban_commands.ban_member(interaction, member)

        interaction.response.send_message.assert_called_once_with("❌ Je n'ai pas les permissions nécessaires pour bannir ce membre.")

    async def test_ban_member_limit_reached(self):
        interaction = AsyncMock()
        member = AsyncMock(spec=Member)
        interaction.user.id = 456
        interaction.guild.ban = AsyncMock()
        interaction.guild.me.guild_permissions.ban_members = True
        interaction.response.send_message = AsyncMock()

        self.db.get_moderator_data.return_value = {"ban_limit": 0, "reset_date": None}

        await self.ban_commands.ban_member(interaction, member)

        interaction.response.send_message.assert_called_once_with("❌ Vous avez atteint votre limite de bans pour cette période.")

    async def test_set_ban_success(self):
        interaction = AsyncMock()
        user = AsyncMock(spec=Member)
        user.id = 123
        user.display_name = "TestUser"
        interaction.user.roles = [MagicMock(id=1)]  # Simulating admin role
        interaction.response.send_message = AsyncMock()

        self.db.set_moderator_data.return_value = True

        await self.ban_commands.set_ban(interaction, user, 5, 7)

        self.db.set_moderator_data.assert_called_once_with(123, 5, 5, Any, "TestUser")
        interaction.response.send_message.assert_called_once_with("✅ Le nombre de bans pour TestUser a été défini à 5 avec un timer de réinitialisation de 7 jours.")

    async def test_set_ban_no_permission(self):
        interaction = AsyncMock()
        user = AsyncMock(spec=Member)
        interaction.user.roles = []  # No admin role
        interaction.response.send_message = AsyncMock()

        await self.ban_commands.set_ban(interaction, user, 5, 7)

        interaction.response.send_message.assert_called_once_with("❌ Vous n'avez pas la permission de définir des bans.")

    async def test_ban_history(self):
        interaction = AsyncMock()
        interaction.user.id = 456
        interaction.response.send_message = AsyncMock()
        self.db.get_all_ban_history.return_value = [(1, 456, 123, "TestUser", "Violation", "2023-10-01")]

        await self.ban_commands.ban_history(interaction)

        interaction.response.send_message.assert_called_once()
        self.assertIn("Historique des bans :", interaction.response.send_message.call_args[0][0])

    async def test_ban_history_no_records(self):
        interaction = AsyncMock()
        interaction.user.id = 456
        interaction.response.send_message = AsyncMock()
        self.db.get_all_ban_history.return_value = []

        await self.ban_commands.ban_history(interaction)

        interaction.response.send_message.assert_called_once_with("❌ Aucun historique de bans trouvé.")

    async def test_ban_limits(self):
        interaction = AsyncMock()
        interaction.response.send_message = AsyncMock()
        self.db.get_all_moderators_with_ban_limits.return_value = [("TestUser", 5, "2023-10-01T00:00:00")]

        await self.ban_commands.ban_limits(interaction)

        interaction.response.send_message.assert_called_once()
        self.assertIn("Liste des bans restants pour les modérateurs :", interaction.response.send_message.call_args[0][0])

    async def test_ban_limits_no_moderators(self):
        interaction = AsyncMock()
        interaction.response.send_message = AsyncMock()
        self.db.get_all_moderators_with_ban_limits.return_value = []

        await self.ban_commands.ban_limits(interaction)

        interaction.response.send_message.assert_called_once_with("❌ Aucun modérateur trouvé.")

if __name__ == "__main__":
    unittest.main()