from config.config import SERVERS
from discord.ext import commands
from discord import app_commands
import discord
from data.currency import remove_bananas
from utils.users import UNBUTTERED_BAGEL_ID

class AdminRemoveCurrencyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_owner():
        async def predicate(interaction: discord.Interaction):
            return interaction.user.id == UNBUTTERED_BAGEL_ID
        return predicate

    @app_commands.command(name="remove_currency", description="Remove currency from a user")
    @app_commands.check(is_owner())
    @app_commands.guilds(SERVERS)
    async def remove_currency(self, interaction: discord.Interaction, user: discord.User, amount: int):
        try:
            await remove_bananas(str(user.id), amount)
            await interaction.response.send_message(f"Removed {amount} bananas to <@{user.id}>'s account.")
        except Exception as e:
            await interaction.response.send_message(f"Failed to add currency: {str(e)}")

    @remove_currency.error
    async def remove_currency_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("You do not have permission for this command.", ephemeral=True)
        else:
            await interaction.response.send_message("An error occurred while processing your command.", ephemeral=True)

def setup(bot):
    bot.add_cog(AdminRemoveCurrencyCog(bot))