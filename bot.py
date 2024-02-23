import discord
from discord.ext import commands
import os
from discord import app_commands
from discord.ext.commands import Bot
from datetime import datetime
from voicelines import GetVoiceLines
from commands import DefineAllCommands
import random

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True

client = discord.Client(intents=intents)

overwatchVoiceLines=GetVoiceLines()
bot = Bot("!",intents=intents)
tree = app_commands.CommandTree(client)
DefineAllCommands(tree)

def setEmbedVariables(embedCreater,message,valueString):
    embedCreater.add_field(name ="Link",value=valueString)
    embedCreater.set_author(name = message.author,icon_url=message.author.avatar.url)
    embedCreater.timestamp = message.created_at
    return embedCreater

def CreateEmbedMessage(message):
    link = str(message.jump_url)
    embedCreater = discord.Embed(description=message.content, color=0x00ff00)
    valueString = "[Go To Message]"+"("+link+")"
    embedCreater = setEmbedVariables(embedCreater,message,valueString)
    if len(message.attachments) > 0:
        embedCreater.set_image(url = message.attachments[0].url)
    return embedCreater

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await tree.sync(guild=discord.Object(id="222147212681936896"))
    await tree.sync(guild=discord.Object(id="1101665956314501180"))
    print("Ready!")


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('ggez'):
        await message.channel.send(random.choice(["Well played. I salute you all.","For glory and honor! Huzzah comrades!","I'm wrestling with some insecurity issues in my life but thank you all for playing with me.","It's past my bedtime. Please don't tell my mommy.","Gee whiz! That was fun. Good playing!","I feel very, very small... please hold me..."]))

saved_messages = {}

# This is for the banana bread saved messages
guild_to_channel = {
    222147212681936896: 1011728618604474428,
    1101665956314501180: 1101698839104192652,
}

@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if payload.user_id == client.user.id or payload.emoji.name not in ["🍞", "🍌"]:
        return
    guild_id = payload.guild_id
    if guild_id not in guild_to_channel:
        return

    if payload.emoji.name == "🍞":
        channel = client.get_channel(payload.channel_id)
        try:
            message = await channel.fetch_message(payload.message_id)
            banana_reaction = discord.utils.get(message.reactions, emoji="🍌")
            if banana_reaction and banana_reaction.count == 1:
                target_channel_id = guild_to_channel[guild_id]
                target_channel = client.get_channel(target_channel_id)
                if payload.message_id not in saved_messages:
                    await target_channel.send(embed=CreateEmbedMessage(message))
                    saved_messages[payload.message_id] = True
        except discord.NotFound:
            print(f"Message {payload.message_id}, Channel: {payload.channel_id}.")
            pass

token = os.environ.get('BOT_TOKEN')
client.run(token)