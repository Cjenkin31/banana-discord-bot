from config.config import SERVERS
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
from data.items import add_item
from data.currency import get_bananas, remove_bananas
from data.stats import random_luck, set_luck
from utils.emoji_helper import BANANA_COIN_EMOJI

class RerollLuckCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="reroll_luck", description="Reroll your luck for currency!")
    @app_commands.guilds(*SERVERS)
    @app_commands.describe(amount="Amount of bananas to spend on rerolling luck")
    async def reroll_luck(self, interaction: discord.Interaction, amount: int):
        user_id = str(interaction.user.id)

        if amount <= 0:
            await interaction.response.send_message("You need to spend a positive number of bananas.", ephemeral=True)
            return

        user_bananas = await get_bananas(user_id)

        if user_bananas >= amount:
            await remove_bananas(user_id, amount)
            luck_to_add = await random_luck(user_id, amount)
            
            await set_luck(user_id, luck_to_add)

            await interaction.response.send_message(f"You have rerolled and set your luck to {luck_to_add} for {amount} {BANANA_COIN_EMOJI}!", ephemeral=False)
        else:
            await interaction.response.send_message(f"You need {amount} bananas to reroll your luck, but you only have {user_bananas}{BANANA_COIN_EMOJI}.", ephemeral=False)

async def setup(bot):
    await bot.add_cog(RerollLuckCommand(bot))
