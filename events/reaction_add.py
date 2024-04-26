from data.saved_messages import guild_to_channel, saved_messages
from utils.embed_utils import create_embed_message
import discord
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import Bot

async def setup_reaction_add(bot):
    @bot.event
    async def on_raw_reaction_add(payload):
        if payload.user_id == bot.user.id or payload.emoji.name not in ["🍞", "🍌"]:
            return
        if payload.emoji.name == "🍞" and payload.guild_id in guild_to_channel:
            channel = bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            if "🍌" in [reaction.emoji for reaction in message.reactions]:
                target_channel_id = guild_to_channel[payload.guild_id]
                target_channel = bot.get_channel(target_channel_id)
                if payload.message_id not in saved_messages:
                    embed = create_embed_message(message)
                    await target_channel.send(embed=embed)
                    saved_messages[payload.message_id] = True
