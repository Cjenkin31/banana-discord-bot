from discord.ext import commands
from discord import app_commands
import discord
from data.currency import get_leaderboard

async def define_leaderboard_command(tree, servers):
    @tree.command(name="leaderboard", description="Display the leaderboard of currency", guilds=servers)
    async def leaderboard(interaction: discord.Interaction):
        try:
            leaderboard_data = await get_leaderboard()
            message = "Top users by bananas:\n"
            for index, (user_id, amount) in enumerate(leaderboard_data[:10], start=1):  # Show top 10 users
                user = await interaction.client.fetch_user(user_id)  # Fetch user info from Discord
                message += f"{index}. `<@{user_id}>` {user.display_name}: {amount} bananas\n"
            await interaction.response.send_message(message)
        except Exception as e:
            await interaction.response.send_message(f"Failed to display leaderboard: {str(e)}")
