from .admin_add_currency_command import define_admin_add_currency_command
from .get_currency_command import define_get_currency_command
from .daily_currency_command import define_daily_command
from .weekly_currency_command import define_weekly_command
from .leaderboard_command import define_leaderboard_command
from .send_bananas_command import define_send_bananas_command
import discord
from discord.ext import commands
from discord import app_commands

async def define_all_currency_commands(tree, servers):
    await define_admin_add_currency_command(tree, servers)
    await define_get_currency_command(tree, servers)
    await define_daily_command(tree, servers)
    await define_weekly_command(tree, servers)
    await define_leaderboard_command(tree, servers)
    await define_send_bananas_command(tree, servers)