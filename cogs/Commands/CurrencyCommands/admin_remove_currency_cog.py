from config.config import SERVERS
from discord.ext import commands
from discord import app_commands
import discord
from data.Currency.currency import remove_bananas
from utils.users import UNBUTTERED_BAGEL_ID

class AdminRemoveCurrencyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_owner(self):
        async def predicate(interaction: discord.Interaction):
            return interaction.user.id == UNBUTTERED_BAGEL_ID
        return app_commands.check(predicate)

    @app_commands.command(name="remove_currency", description="Remove currency from a user")
    @app_commands.guilds(*SERVERS)
    async def remove_currency(self, interaction: discord.Interaction, user: discord.User, amount: int):
        if not await self.is_owner().predicate(interaction):
            await interaction.response.send_message("You do not have permission for this command.", ephemeral=True)
            return
        try:
            await remove_bananas(str(user.id), amount)
            await interaction.response.send_message(f"Removed {amount} bananas from <@{user.id}>'s account.")
        except Exception as e:
            await interaction.response.send_message(f"Failed to remove currency: {str(e)}")

    @remove_currency.error
    async def remove_currency_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("You do not have permission for this command.", ephemeral=True)
        else:
            await interaction.response.send_message("An error occurred while processing your command.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdminRemoveCurrencyCog(bot))