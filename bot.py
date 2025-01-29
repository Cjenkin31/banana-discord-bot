import asyncio
import os
import discord
from discord.ext import commands
from config.config import SERVERS, TOKEN, setup_intents

bot = commands.Bot(command_prefix=".", intents=setup_intents())

async def load_cogs():
    loaded_cogs = 0
    total_cogs = 0
    for root, _, files in os.walk('cogs'):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                path = os.path.join(root, file).replace(os.sep, '.').rstrip('.py')
                total_cogs += 1
                try:
                    await bot.load_extension(path)
                    loaded_cogs += 1
                except Exception as e:
                    print(f"Failed to load cog {path}: {e}")
    print(f"Loaded {loaded_cogs} cogs")
    print(f"Failed to load {total_cogs - loaded_cogs} cogs")

@bot.event
async def on_ready():
    print('Bot is attempting to sync commands...')
    for server in SERVERS:
        print(f'Starting sync for {server.id}')
        await bot.tree.sync(guild=server)
        print(f'Finished sync for {server.id}')
    print(f'Bot is ready and has logged in as {bot.user}')

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
