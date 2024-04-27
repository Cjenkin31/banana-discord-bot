from discord.ext import commands
from discord import app_commands
import discord
from data.currency import get_bananas

def define_get_currency_command(tree, servers):
    @tree.command(name="getcurrency", description="Get your currency amount", guilds=servers)
    @app_commands.checks.has_permissions(administrator=True)
    async def get_currency(interaction: discord.Interaction, user: discord.User, amount: int):
        try:
            await get_bananas(str(user.id))
            await interaction.response.send_message(f"You have {amount} bananas.")
        except Exception as e:
            await interaction.response.send_message(f"Failed to get currency: {str(e)}")
