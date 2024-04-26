import discord
from discord.ext import commands
from discord import app_commands
from Commands.ChatCommands.ask_bread_command import define_ask_bread_command

def define_all_chat_commands(tree, servers, client):
    define_ask_bread_command(tree, servers, client)