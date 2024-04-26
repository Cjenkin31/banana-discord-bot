import discord
from discord.ext import commands
from config.config import TOKEN, INTENTS, SERVERS
from events.setup_events import setup_events
from utils.error_handlers import setup_logging
from Commands.setup_commands import define_all_commands
bot = commands.Bot(command_prefix="!", intents=INTENTS)

setup_events(bot)
define_all_commands(bot, SERVERS)
setup_logging()

bot.run(TOKEN)