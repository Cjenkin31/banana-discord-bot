import asyncio
import os
from discord.ext import commands
from config.config import SERVERS, TOKEN, setup_intents
from utils.users import FREAK_ID, UNBUTTERED_BAGEL_ID
import discord
import logging

bot = commands.Bot(command_prefix=".", intents=setup_intents())

async def dm_user(user_id, message):
    try:
        user = await bot.fetch_user(user_id)
        await user.send(message)
    except discord.Forbidden:
        logging.error("Failed to send DM: Check the user's privacy settings.")
        return False
    except discord.HTTPException as e:
        logging.error("Failed to send DM: %s", e)
        return False
    return True

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
    await dm_user(UNBUTTERED_BAGEL_ID, f'Bot is ready and has logged in as {bot.user}')
    # if os.getenv('ENV', 'DEVELOPMENT') == 'PRODUCTION':
        # await dm_user(FREAK_ID, f'Bot is ready and has logged in as {bot.user}')
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