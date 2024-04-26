import discord
from discord.ext import commands
from discord import app_commands
from Commands.OverwatchCommands.overwatch_player_details import define_overwatch_player_details_command

async def define_all_overwatch_commands(tree, servers):
    await define_overwatch_player_details_command(tree, servers)