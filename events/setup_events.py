import discord
from discord.ext import commands
import os
from discord import app_commands
from discord.ext.commands import Bot

from .message import setup_message
from .reaction_add import setup_reaction_add
from .ready import setup_ready
from .voice_state_update import setup_voice_state_update

async def setup_events(bot):
    await setup_ready(bot)
    await setup_message(bot)
    await setup_voice_state_update(bot)
    await setup_reaction_add(bot)
