from config.config import SERVERS
from data.Currency.steal import try_steal
from discord.ext import commands
from discord import app_commands
import discord

class StealCurrencyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(*SERVERS)
    @app_commands.command(name="steal_bananas", description="Attempt to steal bananas from another user")
    async def steal_bananas(self, interaction: discord.Interaction, user: discord.User):
        thief = interaction.user
        target = user

        if target == thief:
            await interaction.response.send_message("You cannot steal bananas from yourself!", ephemeral=True)
            return

        # Passing both user objects for better message formatting
        success, message = await try_steal(str(thief.id), str(target.id), thief, target)
        if success:
            await interaction.response.send_message(f"{message}", ephemeral=False)
        else:
            await interaction.response.send_message(f"{message}", ephemeral=False)

async def setup(bot):
    await bot.add_cog(StealCurrencyCog(bot))