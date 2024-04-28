import random
from data.currency import add_bananas
from utils.embed_utils import create_embed_message
import discord
from discord.ext import commands
import os
from discord import app_commands
from discord.ext.commands import Bot
from utils.emoji_helper import BANANA_COIN_EMOJI
async def setup_message(bot):
    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return
        if message.content.startswith('ggez'):
            await message.channel.send(random.choice([
                "Well played. I salute you all.",
                "For glory and honor! Huzzah comrades!",
                "I'm wrestling with some insecurity issues in my life but thank you all for playing with me.",
                "It's past my bedtime. Please don't tell my mommy.",
                "Gee whiz! That was fun. Good playing!",
                "I feel very, very small... please hold me..."
            ]))
        if "🍞" in message.content:
            await message.add_reaction("🍞")
        if random.randint(1, 100) == 1:
            banana_amount = random.randint(1,100)
            await add_bananas(message.author.id, banana_amount)
            await message.channel.send(f"<@{message.author.id}> You just found {banana_amount} {BANANA_COIN_EMOJI}")