import os
import discord
from openai import OpenAI

# Server Ids
OVERBOTCHED_ID = discord.Object(id=1101665956314501180)
BONK_BRIGADE_ID = discord.Object(id=1210021401772429352)

# Discord Token + Intents
TOKEN = os.getenv('BOT_TOKEN')
INTENTS = discord.Intents.default()
INTENTS.messages = True
INTENTS.reactions = True
INTENTS.members = True
INTENTS.message_content = True
INTENTS.voice_states = True

SERVERS = [OVERBOTCHED_ID, BONK_BRIGADE_ID]

GPTKEY = os.environ.get('OPENAI_API_KEY')
CLIENT = OpenAI(api_key=GPTKEY)
ELEVEN_LABS_KEY = os.environ.get('xi-api-key')