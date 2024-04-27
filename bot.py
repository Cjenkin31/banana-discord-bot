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

async def main():
    await bot.wait_until_ready()
    await setup_ready(bot, bot.tree)
    await bot.tree.sync()

if __name__ == "__main__":
    bot.loop.run_until_complete(main())
    bot.run(TOKEN)
