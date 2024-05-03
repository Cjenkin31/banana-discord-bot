import discord
from discord import app_commands
from discord.ui import View, Button
from data.items import add_item
from data.currency import get_bananas, remove_bananas
from data.stats import random_luck, set_luck, get_luck
from utils.emoji_helper import BANANA_COIN_EMOJI

async def define_get_luck_command(tree, servers):
    @tree.command(name="get_luck", description="Get your current Luck stat", guilds=servers)
    async def get_luck(interaction: discord.Interaction):
        user_id = interaction.user.id
        current_luck = await get_luck(str(user_id))
        await interaction.response.send_message(f"Your current luck is: {current_luck}!", ephemeral=True)
