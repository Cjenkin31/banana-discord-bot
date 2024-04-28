from data.daily import try_collect_daily
from discord.ext import commands
from discord import app_commands
import discord
from utils.emoji_helper import BANANA_COIN_EMOJI

async def define_daily_command(tree, servers):
    @tree.command(name="daily", description="Collect your daily bananas", guilds=servers)
    async def daily(interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        can_collect, result = await try_collect_daily(user_id)
        
        if not can_collect:
            wait_time = result
            formatted_wait_time = f"{wait_time.seconds // 3600} hours and {(wait_time.seconds // 60) % 60} minutes"
            await interaction.response.send_message(f"Please wait {formatted_wait_time} to collect your daily bananas.")
        else:
            bananas_collected = result
            await interaction.response.send_message(f"You collected {bananas_collected} {BANANA_COIN_EMOJI}! Come back in 24 hours for more.")
