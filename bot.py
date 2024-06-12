import os
import discord
from discord.ext import commands
from config.config import SERVERS, TOKEN, INTENTS
from events.setup_events import setup_events

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
    await setup_events(bot)
    print(f'Logged in as {bot.user}!')

if __name__ == "__main__":
    bot.loop.run_until_complete(load_cogs())
    bot.run(TOKEN)
