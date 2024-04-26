import discord
from discord.ext import commands
from config import TOKEN, INTENTS, SERVERS
from events import setup_events
from .Commands.setup_commands import define_all_commands
from events import *
from events.message import setup_message
from events.reaction_add import setup_reaction_add
from events.ready import setup_ready
from events.voice_state_update import setup_voice_state_update
bot = commands.Bot(command_prefix="!", intents=INTENTS)

setup_ready(bot)
setup_message(bot)
setup_voice_state_update(bot)
setup_reaction_add(bot)
define_all_commands(bot, SERVERS)

bot.run(TOKEN)