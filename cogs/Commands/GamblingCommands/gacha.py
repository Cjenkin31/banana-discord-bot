from config.config import SERVERS
from discord.ext import commands
from discord import app_commands
import discord

class GachaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="gacha", help="Roll for some items")
    async def gacha_dot(self, ctx):
        await ctx.send("Gacha command is not implemented yet.")

    @app_commands.command(name="gacha", description="Roll for some items")
    @app_commands.guilds(*SERVERS)
    async def gacha_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.followup.send("Gacha command is not implemented yet.")

async def setup(bot):
    await bot.add_cog(GachaCog(bot))
