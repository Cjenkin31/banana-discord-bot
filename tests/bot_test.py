import asyncio
import pytest
from unittest.mock import MagicMock, PropertyMock, patch
import discord
from discord.ext import commands
import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bot import load_cogs, on_ready, bot

@pytest.fixture
def mock_bot():
    intents = discord.Intents.default()
    bot = commands.Bot(command_prefix="!", intents=intents)
    type(bot).user = PropertyMock(return_value=MagicMock(id=123456, name='TestBot'))
    type(bot).application_id = PropertyMock(return_value=123456789)

    mock_tree = MagicMock()
    type(bot).tree = PropertyMock(return_value=mock_tree)
    mock_tree.sync = MagicMock(return_value=asyncio.Future())
    mock_tree.sync.return_value.set_result(None)

    return bot

@pytest.mark.asyncio
async def test_load_cogs():
    with patch('os.walk') as mocked_walk, \
         patch.object(bot, 'load_extension') as mocked_load:
        mocked_walk.return_value = [
            ('/path/to/cogs', [], ['hello_cog.py', '__init__.py'])
        ]

        mocked_load.return_value = None  # Simulate successful loading
        await load_cogs()

        # Assertions, fixing the path
        expected_path = 'cogs.hello_cog'
        actual_call = mocked_load.call_args[0][0].replace('/path/to/', '')
        assert expected_path == actual_call, f"Expected {expected_path}, got {actual_call}"

@pytest.mark.asyncio
async def test_on_ready(mock_bot):
    with patch('bot.SERVERS', [MagicMock(id=123), MagicMock(id=456)]) as mocked_servers:
        await on_ready()

        # Assertions
        assert mock_bot.tree.sync.call_count == 2, "Sync should be called for each server"
        print("on_ready called with:", mock_bot.user.name)
