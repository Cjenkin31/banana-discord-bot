
from GPT_stories import getStoryByRole
import discord
from discord.ext import commands
from discord import app_commands

async def define_multiple_messages_command(tree, servers):
    @tree.command(name="multiple_messages", description="TEST COMMAND", guilds=servers)
    async def multiple_messages(interaction: discord.Interaction):
        await interaction.response.send_message("Test.1")
        await interaction.followup.send("Test.2")
        await interaction.channel.send("Test.3")
        await interaction.channel.send("Test.4")
        await interaction.channel.send("Test.5")
