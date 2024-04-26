import discord
from discord.ext import commands
from discord import app_commands
from overwatch_player_details import define_overwatch_player_details_command

def define_all_overwatch_commands(tree, servers):
    define_overwatch_player_details_command(tree, servers)