import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from config.config import SERVERS, TOKEN, INTENTS
from events.ready import setup_ready
from utils.error_handlers import setup_logging

bot = commands.Bot(command_prefix="!", intents=INTENTS)

async def main():
    tree = app_commands.CommandTree(bot)

    await setup_ready(bot, tree)
    setup_logging()

    for guild in SERVERS:
        try:
            await tree.sync(guild=guild)
            print(f"Commands synced successfully with guild: {guild.id}")
        except Exception as e:
            print(f"Failed to sync commands with guild: {guild.id}, error: {e}")
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
