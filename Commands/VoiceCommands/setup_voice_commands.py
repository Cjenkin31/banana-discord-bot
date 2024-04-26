from openai import OpenAI
import os
from speak_command import define_speak_command
from cleanup_vc_command import define_cleanup_vc_command
import discord
from discord.ext import commands
from discord import app_commands

def define_all_voice_commands(tree, servers, client, elevenlabskey):
    define_speak_command(tree, servers, client, elevenlabskey)
    define_cleanup_vc_command(tree, servers)