from discord.ext import commands
from discord import app_commands
import discord
from data.currency import get_bananas
from utils.emoji_helper import BANANA_COIN_EMOJI

async def define_get_currency_command(tree, servers):
    @tree.command(name="get_bananas", description="Get your banana coin amount", guilds=servers)
    async def get_currency(interaction: discord.Interaction):
        try:
            amount = await get_bananas(str(interaction.user.id))
            await interaction.response.send_message(f"You have {amount} {BANANA_COIN_EMOJI}.")
        except Exception as e:
            await interaction.response.send_message(f"Failed to get currency: {str(e)}")
