import logging
from discord.ext import commands

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Command not found!')
    else:
        logging.error(f"Unexpected error: {error}")
        await ctx.send('An unexpected error occurred. Please try again!')
