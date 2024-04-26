import discord
from discord.ext import commands
import os
from discord import app_commands
from discord.ext.commands import Bot
from Commands.setup_commands import define_all_commands
from config.config import SERVERS

async def setup_ready(bot):
    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user}!')
        await define_all_commands(bot, SERVERS)
        for guild in SERVERS:
            await bot.tree.sync(guild=guild)
