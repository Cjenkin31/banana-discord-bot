# Commands/ChatCommands/chat_cog.py
import discord
from discord.ext import commands
from discord import app_commands
from GPT_stories import getStoryByRole
from utils.gpt import generate_gpt_response
from utils.message_utils import send_message_in_chunks
from config.config import SERVERS

class FishingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def process_askbread(self, user_id, user_input, role):
        story = getStoryByRole(role, user_id)
        model = "gpt-4o"
        response_message = await generate_gpt_response(model, story, user_input)
        return response_message

    @app_commands.command(name="fishing", description="Fishing Game!")
    @app_commands.guilds(*SERVERS)
    async def askbread(self, interaction: discord.Interaction):
        await interaction.response.defer()
        response = await generate_gpt_response("gpt3.5-turbo", "You are a fisherman who only speaks in words of fish names. Please only send back 1 word.", "Give me a random fish")
        await interaction.followup.send(f"Fishing is WIP.....Pretend to have recieved a cool fish....Actually here is a gpt generated fish name. {response}")
        # await send_message_in_chunks(response_message, interaction)

async def setup(bot):
    await bot.add_cog(FishingCog(bot))
