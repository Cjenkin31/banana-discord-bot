import discord
from discord.ext import commands
from discord import app_commands
from .random_timeout_command import define_random_timeout_command

async def define_all_shop_commands(tree, servers):
    await define_random_timeout_command(tree, servers)