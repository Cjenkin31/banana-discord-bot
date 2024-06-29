import pytest
from unittest.mock import AsyncMock, MagicMock, PropertyMock
import discord
from discord.ext import commands
import asyncio

def create_bot(intents=None, command_prefix="!"):
    if intents is None:
        intents = discord.Intents.default()
    bot = commands.Bot(command_prefix=command_prefix, intents=intents)
    type(bot).user = PropertyMock(return_value=MagicMock(id=123456, name='TestBot'))
    type(bot).application_id = PropertyMock(return_value=123456789)

    mock_tree = MagicMock()
    type(bot).tree = PropertyMock(return_value=mock_tree)
    mock_tree.sync = MagicMock(return_value=asyncio.Future())
    mock_tree.sync.return_value.set_result(None)

    return bot

@pytest.fixture
def setup_bot():
    async def _setup_bot(cog_class):
        bot = create_bot()
        cog = cog_class(bot)
        await bot.add_cog(cog)
        interaction = AsyncMock()
        interaction.response.defer = AsyncMock()
        interaction.user.id = 123456789
        return bot, cog, interaction
    return _setup_bot

@pytest.fixture(scope="session")
def mock_bot():
    return create_bot()
