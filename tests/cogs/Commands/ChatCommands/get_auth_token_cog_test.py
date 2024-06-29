import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from discord.ext import commands
import discord
from cogs.Commands.ChatCommands.get_auth_token_cog import AuthTokenCog

@pytest.mark.asyncio
async def test_dm_user_correctly_dms_a_user_with_the_correct_message(setup_bot):
    bot, cog, interaction = await setup_bot(AuthTokenCog)
    
    dm_message = "This is a test message"
    response = await cog.dm_user(interaction.user, dm_message)

    assert response == True

@pytest.mark.asyncio
async def test_dm_user_catches_no_priv_error(setup_bot):
    bot, cog, interaction = await setup_bot(AuthTokenCog)

    dm_message = "This is a test message"
    
    mock_response = MagicMock()
    mock_response.status = 403
    
    forbidden_exception = discord.Forbidden(response=mock_response, message="Forbidden")

    with patch.object(interaction.user, 'send', side_effect=forbidden_exception):
        response = await cog.dm_user(interaction.user, dm_message)

    assert response == False

@pytest.mark.asyncio
async def test_generate_token_returns_a_new_token(setup_bot):
    bot, cog, interaction = await setup_bot(AuthTokenCog)

    with patch('cogs.Commands.ChatCommands.get_auth_token_cog.set_auth_token', return_value=True):
        new_token = await cog.generate_token(interaction.user.id)
        user_id = interaction.user.id
        new_token = await cog.generate_token(user_id)

        assert new_token != None

@pytest.mark.asyncio
async def test_generate_token_returns_a_error_if_auth_was_not_set(setup_bot):
    bot, cog, interaction = await setup_bot(AuthTokenCog)

    with patch('cogs.Commands.ChatCommands.get_auth_token_cog.set_auth_token', return_value=False):
        new_token = await cog.generate_token(interaction.user.id)
        user_id = interaction.user.id
        new_token = await cog.generate_token(user_id)

        assert new_token == None

@pytest.mark.asyncio
async def test_send_token_dm_correctly_sends_a_dm_with_the_correct_message(setup_bot):
    bot, cog, interaction = await setup_bot(AuthTokenCog)
    with patch.object(cog, 'dm_user', return_value=False):
        response = await cog.send_token_dm(interaction.user, interaction.user.id, "test_token")

        assert response == False

@pytest.mark.asyncio
async def test_send_token_dm_correctly_errors_when_sending_a_dm_fails(setup_bot):
    bot, cog, interaction = await setup_bot(AuthTokenCog)
    with patch.object(cog, 'dm_user', return_value=True):
        response = await cog.send_token_dm(interaction.user, interaction.user.id, "test_token")

        assert response == True