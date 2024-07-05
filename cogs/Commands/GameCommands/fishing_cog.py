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

    @app_commands.command(name="fishing", description="Fishing Game!")
    @app_commands.guilds(*SERVERS)
    async def askbread(self, interaction: discord.Interaction):
        await interaction.response.send_message("This is still under development.... Please be patient")

async def setup(bot):
    await bot.add_cog(FishingCog(bot))
