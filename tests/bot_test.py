import pytest
from unittest.mock import MagicMock, patch
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bot import load_cogs, on_ready, bot

@pytest.mark.asyncio
async def test_load_cogs():
    with patch('os.walk') as mocked_walk, \
         patch.object(bot, 'load_extension') as mocked_load:
        mocked_walk.return_value = [
            ('/path/to/cogs', [], ['hello_cog.py', '__init__.py'])
        ]

        mocked_load.return_value = None  # Simulate successful loading
        await load_cogs()

        # Assertions
        expected_path = 'cogs.hello_cog'
        actual_call = mocked_load.call_args[0][0].replace('/path/to/', '')
        assert expected_path == actual_call, f"Expected {expected_path}, got {actual_call}"

@pytest.mark.asyncio
async def test_on_ready(mock_bot):
    await on_ready()

    # Assertions
    assert mock_bot.tree.sync.call_count == 2, "Sync should be called for each server"
    print("on_ready called with:", mock_bot.user.name)