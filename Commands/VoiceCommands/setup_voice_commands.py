from openai import OpenAI
import os
from Commands.VoiceCommands.speak_command import define_speak_command
from Commands.VoiceCommands.cleanup_vc_command import define_cleanup_vc_command
import discord
from discord.ext import commands
from discord import app_commands

async def define_all_voice_commands(tree, servers, client, elevenlabskey):
    await define_speak_command(tree, servers, client, elevenlabskey)
    await define_cleanup_vc_command(tree, servers)