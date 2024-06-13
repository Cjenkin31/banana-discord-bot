from GPT_stories import getStoryByRole
import discord
from discord.ext import commands
from discord import app_commands
from utils.gpt import generate_gpt_response
from utils.message_utils import send_message_in_chunks
from utils.users import UNBUTTERED_BAGEL_ID
from data.nickname import remove_nickname as nn

async def define_remove_nickname_command(tree, servers):
    @tree.command(name="remove_nickname", description="Sets your nickname deafult", guilds=servers)
    async def remove_nickname(interaction: discord.Interaction):
        await nn(interaction.user.id)
        await interaction.response.send_message(f"Your nickname has been defaulted.")