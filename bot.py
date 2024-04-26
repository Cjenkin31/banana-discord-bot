import discord
from discord.ext import commands
from config.config import TOKEN, INTENTS, SERVERS
from events.ready import setup_ready
from utils.error_handlers import setup_logging
from Commands.setup_commands import define_all_commands
bot = commands.Bot(command_prefix="!", intents=INTENTS)

setup_ready(bot)
setup_logging()

bot.run(TOKEN)