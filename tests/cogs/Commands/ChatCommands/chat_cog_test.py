import asyncio
import pytest
from unittest.mock import patch
from cogs.Commands.ChatCommands.chat_cog import ChatCog

@pytest.mark.asyncio
async def test_proccess_askbread_correctly_returns_the_response(setup_bot):
    _, cog, interaction = await setup_bot(ChatCog)

    user_input = "Why is banana bread funny?"
    role = "comedian"

    with patch("cogs.Commands.ChatCommands.chat_cog.generate_gpt_response", return_value=asyncio.Future()) as mock_gpt, \
         patch("cogs.Commands.ChatCommands.chat_cog.getStoryByRole", return_value="You are a discord bot assistant...") as mock_story:

        future = asyncio.Future()
        future.set_result("This is response.")
        mock_gpt.return_value = future
        expected_response = "This is response."
        response_message = await cog.process_askbread(interaction.user.id, user_input, role)

        mock_story.assert_called_once_with(role, interaction.user.id)
        mock_gpt.assert_called_once_with("gpt-4o", "You are a discord bot assistant...", user_input)
        assert response_message.result() == expected_response