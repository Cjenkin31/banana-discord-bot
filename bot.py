import asyncio
import os
import discord
from discord.ext import commands
from config.config import SERVERS, TOKEN, INTENTS

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

async def load_cogs():
    for root, dirs, files in os.walk('cogs'):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                path = os.path.join(root, file).replace(os.sep, '.').rstrip('.py')
                try:
                    await bot.load_extension(path)
                    print(f"Loaded cog: {path}")
                except Exception as e:
                    print(f"Failed to load cog {path}: {e}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

async def main():
    try:
        await load_cogs()
        await bot.start(TOKEN)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
