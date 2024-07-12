from config.config import SERVERS
from discord.ext import commands
from discord import app_commands
import discord
from data.Currency.currency import get_leaderboard, get_debt_leaderboard
from utils.image_helpers import download_from_github
from utils.emoji_helper import BANANA_COIN_EMOJI

class LeaderboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="debt_leaderboard", help="Display the leaderboard of currency")
    async def debt_leaderboard(self, ctx):
        try:
            leaderboard_data = await get_debt_leaderboard()
            embed = discord.Embed(title="Top Users by Bananas", description="Here are the top banana earners:", color=0xf1c40f)
            for index, (user_id, amount) in enumerate(leaderboard_data[:10], start=1):
                try:
                    user = await ctx.guild.fetch_member(user_id)
                except discord.errors.NotFound:
                    user = "Unknown User"
                if isinstance(user, discord.Member):
                    embed.add_field(name=f"{index}. {BANANA_COIN_EMOJI} {user.display_name}", value=f"{amount}", inline=False)
                else:
                    embed.add_field(name=f"{index}. {BANANA_COIN_EMOJI} {user}", value=f"{amount}", inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Failed to display leaderboard: {str(e)}")

    @app_commands.guilds(*SERVERS)
    @app_commands.command(name="leaderboard", description="Display the leaderboard of currency")
    async def leaderboard(self, interaction: discord.Interaction):
        try:
            leaderboard_data = await get_leaderboard()
            thumbnail_file = await download_from_github("bananaleaderboard.png")
            embed = discord.Embed(title="Top Users by Bananas", description="Here are the top banana earners:", color=0xf1c40f)
            if thumbnail_file:
                embed.set_thumbnail(url="attachment://image.jpg")
            for index, (user_id, amount) in enumerate(leaderboard_data[:10], start=1):
                try:
                    user = await interaction.client.fetch_user(user_id)
                except discord.errors.NotFound:
                    user = "Unknown User"
                if isinstance(user, discord.User):
                    embed.add_field(name=f"{index}. {BANANA_COIN_EMOJI} {user.display_name}", value=f"{amount}", inline=False)
                else:
                    embed.add_field(name=f"{index}. {BANANA_COIN_EMOJI} {user}", value=f"{amount}", inline=False)
            if thumbnail_file:
                await interaction.response.send_message(embed=embed, file=thumbnail_file)
            else:
                await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Failed to display leaderboard: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(LeaderboardCog(bot))
