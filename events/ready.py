import discord
from discord.ext import commands
import os
from discord import app_commands
from discord.ext.commands import Bot
async def setup_ready(bot):
    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user}!')
        for guild_id in bot.servers.values():
            await bot.tree.sync(guild=discord.Object(id=guild_id))
