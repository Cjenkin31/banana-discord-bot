from config.config import SERVERS
from discord.ext import commands
from discord import app_commands
import discord
from data.currency import get_leaderboard
from utils.image_helpers import download_from_github
from utils.emoji_helper import BANANA_COIN_EMOJI

class LeaderboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(SERVERS)
    @app_commands.command(name="leaderboard", description="Display the leaderboard of currency")
    async def leaderboard(self, interaction: discord.Interaction):
        try:
            leaderboard_data = await get_leaderboard()
            thumbnail_file = await download_from_github("bananaleaderboard.png")
            embed = discord.Embed(title="Top Users by Bananas", description="Here are the top banana earners:", color=0xf1c40f)
            if thumbnail_file:
                embed.set_thumbnail(url="attachment://image.jpg")
            
            for index, (user_id, amount) in enumerate(leaderboard_data[:10], start=1):
                user = await interaction.client.fetch_user(user_id)
                embed.add_field(name=f"{index}. {BANANA_COIN_EMOJI} {user.display_name}", value=f"{amount}", inline=False)
            if thumbnail_file:
                await interaction.response.send_message(embed=embed, file=thumbnail_file)
            else:
                await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Failed to display leaderboard: {str(e)}", ephemeral=True)

def setup(bot):
    bot.add_cog(LeaderboardCog(bot))
