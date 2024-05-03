
from GPT_stories import getStoryByRole
import discord
from discord.ext import commands
from discord import app_commands

async def define_multiple_messages_command(tree, servers):
    @tree.command(name="multiple_messages", description="TEST COMMAND", guilds=servers)
    async def multiple_messages(interaction: discord.Interaction, user_input: str, role: str):
        await interaction.followup.send("test")
        await interaction.channel.send("test")
        await interaction.channel.send("test")
        await interaction.channel.send("test")