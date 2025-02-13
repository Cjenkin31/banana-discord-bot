from config.config import SERVERS
from discord.ext import commands
from discord import app_commands
from game.gacha.gacha_service import GachaService
class Gacha(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @app_commands.guilds(*SERVERS)
    @app_commands.command(name="gacha_spin", description="Roll for a random ingredient")
    async def gacha_spin(self, interaction, amount: int = 1):
        user_id = str(interaction.user.id)
        ingredient, message = await GachaService.roll_ingredient(user_id, interaction, amount)
        if not ingredient:
            await interaction.response.send_message(message)
        else:
            await interaction.response.send_message(message)

async def setup(bot):
    await bot.add_cog(Gacha(bot))
