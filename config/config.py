import os
import discord

# Server Ids
OVERBOTCHED_ID = discord.Object(id=1101665956314501180)
BONK_BRIGADE_ID = discord.Object(id=1210021401772429352)

# Discord Token + Intents
TOKEN = os.getenv('BOT_TOKEN')
INTENTS = discord.Intents.default()
INTENTS.messages = True
INTENTS.reactions = True
INTENTS.members = True

SERVERS = [OVERBOTCHED_ID, BONK_BRIGADE_ID]
