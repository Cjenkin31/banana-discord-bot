from config.config import SERVERS
from discord.ext import commands
from discord import app_commands
import discord
from data.Currency.currency import get_bananas
from utils.emoji_helper import BANANA_COIN_EMOJI

class GetCurrencyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

@commands.command(name="get_bananas", help="Get your banana coin amount", aliases=['bal','balance', 'cash', 'get_cash', 'get_currency'])
async def get_currency(self, ctx):
    try:
        amount = await get_bananas(str(ctx.author.id))
        await ctx.send(f"You have {amount} {BANANA_COIN_EMOJI}.")
    except Exception as e:
        await ctx.send(f"Failed to get currency: {str(e)}")

    @app_commands.guilds(*SERVERS)
    @app_commands.command(name="get_bananas", description="Get your banana coin amount")
    async def get_currency(self, interaction: discord.Interaction):
        try:
            amount = await get_bananas(str(interaction.user.id))
            await interaction.response.send_message(f"You have {amount} {BANANA_COIN_EMOJI}.")
        except Exception as e:
            await interaction.response.send_message(f"Failed to get currency: {str(e)}")

async def setup(bot):
    await bot.add_cog(GetCurrencyCog(bot))
