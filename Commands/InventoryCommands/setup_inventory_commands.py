from openai import OpenAI
import os
from .view_inventory_command import define_view_inventory_command
import discord
from discord.ext import commands
from discord import app_commands

async def define_all_inventory_commands(tree, servers):
    await define_view_inventory_command(tree, servers)