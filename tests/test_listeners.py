import unittest
from unittest.mock import AsyncMock, MagicMock
from discord import Message, Member
from cogs.listeners.messages.messageCreate import MessageCreate
from cogs.listeners.messages.messageDelete import MessageDelete

class TestMessageCreateListener(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.bot = AsyncMock()
        self.message_create = MessageCreate(self.bot)

    async def test_on_message_not_bot(self):
        interaction = AsyncMock()
        message = AsyncMock(spec=Message)
        message.author = AsyncMock(spec=Member)
        message.author.bot = False
        message.author.name = "TestUser"
        message.content = "Test message"
        message.reply = AsyncMock()

        await self.message_create.on_message(message)
        message.reply.assert_called_once()

    async def test_on_message_is_bot(self):
        interaction = AsyncMock()
        message = AsyncMock(spec=Message)
        message.author.bot = True
        message.reply = AsyncMock()

        await self.message_create.on_message(message)
        message.reply.assert_not_called()

class TestMessageDeleteListener(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.bot = AsyncMock()
        self.message_delete = MessageDelete(self.bot)

    async def test_on_message_delete_not_bot(self):
        interaction = AsyncMock()
        message = AsyncMock(spec=Message)
        message.author = AsyncMock(spec=Member)
        message.author.bot = False
        message.author.name = "TestUser"
        message.content = "Test message"
        message.channel.id = 123456789
        message.id = 987654321
        message.channel.name = "test-channel"
        message.author.display_avatar.url = "http://example.com/avatar.png"
        self.bot.get_channel.return_value = AsyncMock()
        log_channel = AsyncMock()
        log_channel.send = AsyncMock()
        self.bot.get_channel.return_value = log_channel

        await self.message_delete.on_message_delete(message)
        log_channel.send.assert_called_once()

if __name__ == "__main__":
    unittest.main()
