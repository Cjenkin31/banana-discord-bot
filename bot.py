from Commands.setup_commands import define_all_commands
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from config.config import SERVERS, TOKEN, INTENTS
from events.setup_events import setup_events
from utils.error_handlers import setup_logging

bot = commands.Bot(command_prefix="!", intents=INTENTS)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    await setup_events(bot)
    await define_all_commands(bot.tree, SERVERS, bot)
    for guild in SERVERS:
        try:
            await bot.tree.sync(guild=guild)
            print(f"Commands synced successfully with guild: {guild.id}")
        except Exception as e:
            print(f"Failed to sync commands with guild: {guild.id}, error: {e}")

if __name__ == "__main__":
    bot.run(TOKEN)
