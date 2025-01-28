from config.config import SERVERS
import discord
from discord.ext import commands
from discord import app_commands
from data.stats import get_luck

class GetLuckCommand(commands.Cog, name="get_luck"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="get_luck", description="Get your current Luck stat")
    @app_commands.guilds(*SERVERS)
    async def get_luck_command(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        current_luck = await get_luck(str(user_id))
        await interaction.response.send_message(f"Your current luck is: {current_luck}!", ephemeral=False)

async def setup(bot):
    await bot.add_cog(GetLuckCommand(bot))
