import discord
from discord.ext import commands
from discord import app_commands
from Commands.ValorantCommands.valorant_matches_command import define_valorant_matches_command
from Commands.ValorantCommands.valorant_summary_command import define_valorant_summary_command
from Commands.ValorantCommands.valorant_account_command import define_valorant_account_command

async def define_all_valorant_commands(tree, servers):
    await define_valorant_account_command(tree, servers)
    await define_valorant_summary_command(tree, servers)
    await define_valorant_matches_command(tree, servers)
    print("Registered Valorant commands.")