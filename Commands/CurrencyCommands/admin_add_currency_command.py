from discord.ext import commands
from discord import app_commands
import discord
from data.currency import add_bananas

def define_admin_add_currency_command(tree, servers):
    @tree.command(name="addcurrency", description="Add currency to a user", guilds=servers)
    @app_commands.checks.has_permissions(administrator=True)
    async def add_currency(interaction: discord.Interaction, user: discord.User, amount: int):
        try:
            await add_bananas(str(user.id), amount)
            await interaction.response.send_message(f"Added {amount} bananas to {user.display_name}'s account.")
        except Exception as e:
            await interaction.response.send_message(f"Failed to add currency: {str(e)}")
