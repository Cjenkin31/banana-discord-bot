# This example requires the 'message_content' intent.

import discord

import os
token = os.environ.get('BOT_TOKEN')

load_dotenv()  # take environment variables from 
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if payload.user_id == client.user.id:
        return

    if payload.emoji.name == "🍞":
        channel = client.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        reactions = message.reactions
        for reaction in reactions:
            if str(reaction) == "🍌":
                link = str(message.jump_url)
                embedVar = discord.Embed(description=message.content, color=0x00ff00)
                valueString = "[Go To Message]"+"("+link+")"
                embedVar.add_field(name ="Link",value=valueString)
                embedVar.set_author(name= message.author,icon_url=message.author.avatar.url)
                embedVar.timestamp = message.created_at
                if len(message.attachments) > 0:
                    embedVar.set_image(url = message.attachments[0].url)
                await client.get_channel(1011448137002528839).send(embed=embedVar)
        
    
client.run(token)
