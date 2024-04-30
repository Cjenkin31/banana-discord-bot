import os
from Commands.InventoryCommands.setup_inventory_commands import define_all_inventory_commands
import discord
from discord.ext import commands
from discord import app_commands
from openai import OpenAI
from Commands.GamblingCommands.setup_gambling_commands import define_all_gambling_commands
from Commands.ValorantCommands.setup_valorant_commands import define_all_valorant_commands
from Commands.OverwatchCommands.setup_overwatch_commands import define_all_overwatch_commands
from Commands.RandomCommands.setup_random_commands import define_all_random_commands
from Commands.VoiceCommands.setup_voice_commands import define_all_voice_commands
from Commands.ChatCommands.setup_chat_commands import define_all_chat_commands
from Commands.CurrencyCommands.setup_currency_commands import define_all_currency_commands
from Commands.ShopCommands.setup_shop_commands import define_all_shop_commands

gptkey = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=gptkey)
elevenlabskey = os.environ.get('xi-api-key')

async def define_all_commands(tree, servers):
    await define_all_valorant_commands(tree, servers)
    await define_all_overwatch_commands(tree, servers)
    await define_all_random_commands(tree, servers)
    await define_all_voice_commands(tree, servers, client, elevenlabskey)
    await define_all_chat_commands(tree, servers, client)
    await define_all_currency_commands(tree, servers)
    await define_all_gambling_commands(tree, servers)
    await define_all_shop_commands(tree, servers)
    await define_all_inventory_commands(tree, servers)
    print("Registered all commands.")