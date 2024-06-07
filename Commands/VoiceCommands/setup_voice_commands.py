from Commands.VoiceCommands.stop_command import define_stop_youtube_audio_command
from openai import OpenAI
import os
from Commands.VoiceCommands.play_command import define_play_youtube_audio_command
from Commands.VoiceCommands.speak_command import define_speak_command
from Commands.VoiceCommands.cleanup_vc_command import define_cleanup_vc_command
import discord
from discord.ext import commands
from discord import app_commands

async def define_all_voice_commands(tree, servers, elevenlabskey):
    await define_speak_command(tree, servers, elevenlabskey)
    await define_cleanup_vc_command(tree, servers)
    await define_play_youtube_audio_command(tree, servers)
    await define_stop_youtube_audio_command(tree, servers)