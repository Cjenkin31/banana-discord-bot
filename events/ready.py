import discord
from discord.ext import commands
from Commands.setup_commands import define_all_commands
from config.config import SERVERS
from events.setup_events import setup_events
async def setup_ready(bot, tree):
    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user}!')
        await setup_events(bot)
        await define_all_commands(tree, SERVERS)