from discord.ext import commands
from discord import app_commands
import discord
from data.currency import get_leaderboard

async def define_leaderboard_command(tree, servers):
    @tree.command(name="leaderboard", description="Display the leaderboard of currency", guilds=servers)
    async def leaderboard(interaction: discord.Interaction):
        try:
            leaderboard_data = await get_leaderboard()
            embed = discord.Embed(title="Top Users by Bananas", description="Here are the top banana earners:", color=0xf1c40f)
            embed.set_thumbnail(url="https://github.com/Cjenkin31/banana-discord-bot/blob/main/images/bananaleaderboard.png")
            for index, (user_id, amount) in enumerate(leaderboard_data[:10], start=1):  # Show top 10 users
                user = await interaction.client.fetch_user(user_id)  # Fetch user info from Discord
                embed.add_field(name=f"{index}. {user.display_name}", value=f"{amount} bananas", inline=False)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Failed to display leaderboard: {str(e)}", ephemeral=True)
