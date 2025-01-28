from datetime import timedelta
from config.config import SERVERS
from discord.ext import commands
from discord import app_commands
import discord
import random
from data.Currency.currency import get_bananas, remove_bananas
from utils.emoji_helper import BANANA_COIN_EMOJI

class RandomTimeoutCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="randomtimeout", description="Timeout a random user for 60 seconds (including yourself) : 1000 coins")
    @app_commands.guilds(*SERVERS)
    async def random_timeout(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        current_bananas = await get_bananas(user_id)
        timeout_cost = 1000
        if current_bananas < timeout_cost:
            await interaction.response.send_message(f"You don't have enough {BANANA_COIN_EMOJI}!")
            return

        guild = interaction.guild

        moderator_role = discord.utils.get(guild.roles, name="A")
        possible_targets = [member for member in guild.members if not member.bot and moderator_role not in member.roles]

        if not possible_targets:
            await interaction.response.send_message("No available members to timeout.")
            return

        selected_member = random.choice(possible_targets)

        duration = discord.utils.utcnow() + timedelta(seconds=60)
        try:
            await selected_member.edit(timed_out_until=duration)
            await remove_bananas(user_id, timeout_cost)
            await interaction.response.send_message(f"{selected_member.display_name} has been timed out for 60 seconds!")
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to timeout this user.")
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}")

async def setup(bot):
    await bot.add_cog(RandomTimeoutCommand(bot))
