import discord
from discord.ext import commands
from discord import app_commands
from Commands.StatCommands.get_luck_command import define_get_luck_command
from Commands.StatCommands.reroll_luck_command import define_reroll_luck_command

async def define_all_stat_commands(tree, servers):
    await define_reroll_luck_command(tree, servers)
    await define_get_luck_command(tree, servers)