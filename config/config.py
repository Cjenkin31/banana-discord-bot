import os
import discord
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

# Server Ids
OVERBOTCHED_ID = discord.Object(id=1101665956314501180)
BONK_BRIGADE_ID = discord.Object(id=1210021401772429352)
TEST_SERVER_ID = discord.Object(id=844017098022715402)

environment = os.getenv('ENV', 'DEVELOPMENT')
if environment == "PRODUCTION":
    TOKEN = os.getenv('BOT_TOKEN')
    SERVERS = [OVERBOTCHED_ID, BONK_BRIGADE_ID]
    debug_mode = False
else:
    TOKEN = os.getenv('DEVELOPMENT_BOT_TOKEN')
    SERVERS = [TEST_SERVER_ID]
    debug_mode = True

INTENTS = discord.Intents.default()
INTENTS.messages = True
INTENTS.reactions = True
INTENTS.members = True
INTENTS.message_content = True
INTENTS.voice_states = True

ELEVEN_LABS_API_KEY = os.getenv('xi-api-key')
FIREBASE_SERVICE_ACCOUNT = os.getenv('FIREBASE_SERVICE_ACCOUNT')
GPTKEY = os.getenv('OPENAI_API_KEY')
CLIENT = OpenAI(api_key=GPTKEY)

DEEPSEEK_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_CLIENT = OpenAI(api_key=DEEPSEEK_KEY, base_url="https://api.deepseek.com")