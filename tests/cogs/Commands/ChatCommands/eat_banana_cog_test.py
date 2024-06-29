import asyncio
import pytest
from unittest.mock import AsyncMock, patch
from discord.ext import commands
from cogs.Commands.ChatCommands.eat_banana_cog import EatBananaCog

@pytest.mark.asyncio
async def test_process_eating_correctly_handles_1_banana_when_user_has_enough_currency(setup_bot):
    bot, cog, interaction = await setup_bot(EatBananaCog)

    with patch("cogs.Commands.ChatCommands.eat_banana_cog.get_bananas", return_value=1), \
         patch("cogs.Commands.ChatCommands.eat_banana_cog.add_bananas", return_value="You are a discord bot assistant...") as mock_add, \
         patch("cogs.Commands.ChatCommands.eat_banana_cog.remove_bananas", return_value="You are a discord bot assistant...") as mock_remove, \
         patch("cogs.Commands.ChatCommands.eat_banana_cog.random.randint", return_value=2) as mock_random:

        mock_add_future = asyncio.Future()
        mock_add.return_value = mock_add_future

        mock_remove_future = asyncio.Future()
        mock_remove.return_value = mock_remove_future

        expected_response = "You eat 1 banana 🍌!\nhttps://tenor.com/view/effy-gif-11375717773991506810"

        amount_eaten = 1
        response_message = await cog.process_eating(interaction, amount_eaten)

        assert response_message == expected_response

@pytest.mark.asyncio
async def test_process_eating_correctly_gives_it_to_bananabreadbot_if_random_is_1(setup_bot):
    bot, cog, interaction = await setup_bot(EatBananaCog)

    with patch("cogs.Commands.ChatCommands.eat_banana_cog.get_bananas", return_value=1), \
         patch("cogs.Commands.ChatCommands.eat_banana_cog.add_bananas", return_value="You are a discord bot assistant...") as mock_add, \
         patch("cogs.Commands.ChatCommands.eat_banana_cog.remove_bananas", return_value="You are a discord bot assistant...") as mock_remove, \
         patch("cogs.Commands.ChatCommands.eat_banana_cog.random.randint", return_value=1) as mock_random:

        mock_add_future = asyncio.Future()
        mock_add.return_value = mock_add_future

        mock_remove_future = asyncio.Future()
        mock_remove.return_value = mock_remove_future

        expected_response = "You decide to give 1 banana(s) to the bot instead 🎁!\nhttps://tenor.com/view/effy-gif-11375717773991506810"

        amount_eaten = 1
        response_message = await cog.process_eating(interaction, amount_eaten)

        assert response_message == expected_response

@pytest.mark.asyncio
async def test_process_eating_correctly_eats_more_bananas(setup_bot):
    bot, cog, interaction = await setup_bot(EatBananaCog)

    with patch("cogs.Commands.ChatCommands.eat_banana_cog.get_bananas", return_value=10), \
         patch("cogs.Commands.ChatCommands.eat_banana_cog.add_bananas", return_value="You are a discord bot assistant...") as mock_add, \
         patch("cogs.Commands.ChatCommands.eat_banana_cog.remove_bananas", return_value="You are a discord bot assistant...") as mock_remove, \
         patch("cogs.Commands.ChatCommands.eat_banana_cog.random.randint", return_value=2) as mock_random:

        mock_add_future = asyncio.Future()
        mock_add.return_value = mock_add_future

        mock_remove_future = asyncio.Future()
        mock_remove.return_value = mock_remove_future

        expected_response = "You eat 10 bananas 🍌🍌🍌🍌🍌🍌🍌🍌🍌🍌!\nhttps://tenor.com/view/effy-gif-11375717773991506810"

        amount_eaten = 10
        response_message = await cog.process_eating(interaction, amount_eaten)

        assert response_message == expected_response

@pytest.mark.asyncio
async def test_process_eating_correctly_handles_1_banana_when_user_does_not_have_enough_currency(setup_bot):
    bot, cog, interaction = await setup_bot(EatBananaCog)

    with patch("cogs.Commands.ChatCommands.eat_banana_cog.get_bananas", return_value=0), \
         patch("cogs.Commands.ChatCommands.eat_banana_cog.add_bananas", return_value="You are a discord bot assistant...") as mock_add, \
         patch("cogs.Commands.ChatCommands.eat_banana_cog.remove_bananas", return_value="You are a discord bot assistant...") as mock_remove, \
         patch("cogs.Commands.ChatCommands.eat_banana_cog.random.randint", return_value=2) as mock_random:

        mock_add_future = asyncio.Future()
        mock_add.return_value = mock_add_future

        mock_remove_future = asyncio.Future()
        mock_remove.return_value = mock_remove_future

        expected_response = "YOU DON'T HAVE ENOUGH <:bananacoin:1234155554167849131> TO EAT\n"

        amount_eaten = 1
        response_message = await cog.process_eating(interaction, amount_eaten)

        assert response_message == expected_response

@pytest.mark.asyncio
async def test_process_eating_does_not_give_the_bot_bananas_if_user_does_not_have_enough(setup_bot):
    bot, cog, interaction = await setup_bot(EatBananaCog)

    with patch("cogs.Commands.ChatCommands.eat_banana_cog.get_bananas", return_value=0), \
         patch("cogs.Commands.ChatCommands.eat_banana_cog.add_bananas", return_value="You are a discord bot assistant...") as mock_add, \
         patch("cogs.Commands.ChatCommands.eat_banana_cog.remove_bananas", return_value="You are a discord bot assistant...") as mock_remove, \
         patch("cogs.Commands.ChatCommands.eat_banana_cog.random.randint", return_value=1) as mock_random:

        mock_add_future = asyncio.Future()
        mock_add.return_value = mock_add_future

        mock_remove_future = asyncio.Future()
        mock_remove.return_value = mock_remove_future

        expected_response = "YOU DON'T HAVE ENOUGH <:bananacoin:1234155554167849131> TO EAT\n"

        amount_eaten = 100
        response_message = await cog.process_eating(interaction, amount_eaten)

        assert response_message == expected_response
