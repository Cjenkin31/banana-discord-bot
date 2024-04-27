from .admin_add_currency_command import define_admin_add_currency_command
from .get_currency_command import define_get_currency_command
from .daily_currency_command import define_daily_command
import discord
from discord.ext import commands
from discord import app_commands

async def define_all_currency_commands(tree, servers):
    define_admin_add_currency_command(tree, servers)
    define_get_currency_command(tree, servers)
    define_daily_command(tree, servers)