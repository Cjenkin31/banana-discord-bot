from Commands.setup_commands import define_all_commands
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from config.config import SERVERS, TOKEN, INTENTS
from events.ready import setup_ready
from events.setup_events import setup_events
from utils.error_handlers import setup_logging

bot = commands.Bot(command_prefix="!", intents=INTENTS)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    await setup_events(bot)
    await define_all_commands(bot.tree, SERVERS)

if __name__ == "__main__":
    bot.run(TOKEN)
