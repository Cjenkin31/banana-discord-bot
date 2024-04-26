import discord
from discord.ext import commands
from discord import app_commands
import random

async def define_pick_from_list_command(tree, servers):
    @tree.command(name = "pickfromlist", description = "input things to be chosen seperated by a ,. Ex. Overwatch,League", guilds=servers) 
    async def pickfromlist(interaction: discord.Interaction, items: str):
        await interaction.response.send_message(random.choice(items.split(',')))