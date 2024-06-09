import discord
from discord.ext import commands
from discord import app_commands
from .random_timeout_command import define_random_timeout_command
from .assassinate_command import define_assassinate_command
# from .shop_command import define_shop_command

async def define_all_shop_commands(tree, servers):
    await define_random_timeout_command(tree, servers)
    await define_assassinate_command(tree, servers)
    # await define_shop_command(tree, servers)