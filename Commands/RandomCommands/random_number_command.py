import discord
from discord.ext import commands
from discord import app_commands
import random

def define_random_number_command(tree, servers):
    @tree.command(name = "randomnumber", description = "Choose a random number between 2 inputs ex: 1,100", guilds=servers) 
    async def self(interaction: discord.Interaction, items: str):
        try:
            numbers = items.split(',')
            await interaction.response.send_message(random.randint(int(numbers[0]),int(numbers[1])))
        except:
            await interaction.response.send_message("Either you messed up or I did. But It was prob you")