from .coinflip_command import define_coinflip_command
from .blackjack_command import define_blackjack_command
from .slots_command import define_slots_command
import discord
from discord.ext import commands
from discord import app_commands

async def define_all_gambling_commands(tree, servers, bot):
    define_coinflip_command(tree, servers)
    define_blackjack_command(tree, servers, bot)
    define_slots_command(tree, servers)