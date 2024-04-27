import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from config.config import TOKEN, INTENTS
from events.ready import setup_ready
from utils.error_handlers import setup_logging

bot = commands.Bot(command_prefix="!", intents=INTENTS)

async def main():
    tree = app_commands.CommandTree(bot)

    await setup_ready(bot, tree)
    setup_logging()

    await tree.sync()
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
