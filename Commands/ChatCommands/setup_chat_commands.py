import discord
from discord.ext import commands
from discord import app_commands
from Commands.ChatCommands.ask_bread_command import define_ask_bread_command
from Commands.ChatCommands.eat_banana_command import define_eat_banana_command
from Commands.ChatCommands.summarize_youtube import define_summarize_youtube_video_command
from Commands.ChatCommands.nickname_command import define_set_nickname_command
from Commands.ChatCommands.remove_nickname_command import define_remove_nickname_command
async def define_all_chat_commands(tree, servers):
    await define_ask_bread_command(tree, servers)
    await define_eat_banana_command(tree, servers)
    await define_summarize_youtube_video_command(tree, servers)
    await define_set_nickname_command(tree, servers)
    await define_remove_nickname_command(tree, servers)