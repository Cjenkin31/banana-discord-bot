from .coinflip_command import define_coinflip_command
import discord
from discord.ext import commands
from discord import app_commands

async def define_all_gambling_commands(tree, servers):
    define_coinflip_command(tree, servers)