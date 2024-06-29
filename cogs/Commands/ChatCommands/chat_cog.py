# Commands/ChatCommands/chat_cog.py
import discord
from discord.ext import commands
from discord import app_commands
from GPT_stories import getStoryByRole
from utils.gpt import generate_gpt_response
from utils.message_utils import send_message_in_chunks
from config.config import SERVERS

class ChatCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def process_askbread(self, user_id, user_input, role):
        story = getStoryByRole(role, user_id)
        model = "gpt-4o"
        response_message = await generate_gpt_response(model, story, user_input)
        return response_message

    @app_commands.command(name="askbread", description="...")
    @app_commands.guilds(*SERVERS)
    async def askbread(self, interaction: discord.Interaction, user_input: str, role: str):
        await interaction.response.defer()
        response_message = await self.process_askbread(interaction.user.id, user_input, role)
        await send_message_in_chunks(response_message, interaction)

async def setup(bot):
    await bot.add_cog(ChatCog(bot))
