from .roulette_command import define_roulette_command
from .coinflip_command import define_coinflip_command
from .blackjack_command import define_blackjack_command
from .slots_command import define_slots_command
import discord
from discord.ext import commands
from discord import app_commands

async def define_all_gambling_commands(tree, servers, bot):
    await define_coinflip_command(tree, servers)
    await define_blackjack_command(tree, servers, bot)
    await define_slots_command(tree, servers)
    await define_roulette_command(tree, servers)