import random
import discord
from discord.ext import commands
from discord import app_commands

def define_rhythm_roll_command(tree, servers):
    @tree.command(name="rhythmroll", description="rolls number 1-100", guilds=servers) 
    async def first_command(interaction):
        await interaction.response.send_message(random.randint(0,100))