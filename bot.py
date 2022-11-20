import discord
from discord.ext import commands
import os
from discord import app_commands
from discord.ext.commands import Bot
from datetime import datetime
import random
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True

client = discord.Client(intents=intents)
overwatchHeroTankList = ["D.VA", "Doomfist", "Junkerqueen","Orisa","Reinhardt","Roadhod","Sigma","Winston","Wrecking Ball","Zarya"]
overwatchHeroDPSList = ["Ashe", "Bastion", "Cassidy","Echo","Genji","Hanzo","Junkrat","Mei","Pharah","Reaper","Sojourn","Soldier 76","Sombra(Please Dont)","Symmetra","Torbjorn","Tracer","Widowmaker"]
overwatchHeroSupportList = ["Ana", "Baptiste", "Brigitte","Kiriko","Lucio","Mercy","Moira","Zenyatta"]
overwatchRoleList = ["Tank", "DPS", "Support"]
overwatchGameModeList = ["Competitive", "Quick Play", "Custom Games", "Arcade"]
bot = Bot("!",intents=intents)
tree = app_commands.CommandTree(client)

@tree.command(name = "hello", description = "hello command", guild=discord.Object(id=222147212681936896))
async def first_command(interaction):
    await interaction.response.send_message("Hello!")

@tree.command(name = "randomtank", description = "rolls a random tank hero from overwatch", guild=discord.Object(id=222147212681936896))
async def first_command(interaction):
    tankHero=random.choice(overwatchHeroTankList)
    await interaction.response.send_message(tankHero)

@tree.command(name = "randomsupport", description = "rolls a random support hero from overwatch", guild=discord.Object(id=222147212681936896))
async def first_command(interaction):
    supportHero=random.choice(overwatchHeroSupportList)
    await interaction.response.send_message(supportHero)

@tree.command(name = "randomdps", description = "rolls a random support dps from overwatch", guild=discord.Object(id=222147212681936896)) 
async def first_command(interaction):
    dpsHero=random.choice(overwatchHeroDPSList)
    await interaction.response.send_message(dpsHero)

@tree.command(name = "randomroleow", description = "rolls a random role for overwatch", guild=discord.Object(id=222147212681936896)) 
async def first_command(interaction):
    overwatchRole=random.choice(overwatchRoleList)
    await interaction.response.send_message(overwatchRole)

@tree.command(name = "randomgamemodeow", description = "rolls a random game mode for overwatch", guild=discord.Object(id=222147212681936896)) 
async def first_command(interaction):
    overwatchGamemode=random.choice(overwatchGameModeList)
    await interaction.response.send_message(overwatchGamemode)

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
    await tree.sync(guild=discord.Object(id=222147212681936896))
    print("Ready!")

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
            if str(reaction) == "🍌" and reaction.count==1:
                await client.get_channel(1011728618604474428).send(embed=CreateEmbedMessage(message))
        
token = os.environ.get('BOT_TOKEN')
client.run(token)

