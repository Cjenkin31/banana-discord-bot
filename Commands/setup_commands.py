import os
import discord
from discord.ext import commands
from discord import app_commands
from openai import OpenAI
from Commands.ValorantCommands.setup_valorant_commands import define_all_valorant_commands
from Commands.OverwatchCommands.setup_overwatch_commands import define_all_overwatch_commands
from Commands.RandomCommands.setup_random_commands import define_all_random_commands
from Commands.VoiceCommands.setup_voice_commands import define_all_voice_commands
from Commands.ChatCommands.setup_chat_commands import define_all_chat_commands

gptkey = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=gptkey)
elevenlabskey = os.environ.get('xi-api-key')

async def define_all_commands(tree, servers):
    await define_all_valorant_commands(tree, servers)
    await define_all_overwatch_commands(tree, servers)
    await define_all_random_commands(tree, servers)
    await define_all_voice_commands(tree, servers, client, elevenlabskey)
    await define_all_chat_commands(tree, servers, client)
    print("Registered all commands.")