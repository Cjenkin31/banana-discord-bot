from GPT_stories import getStoryByRole
import discord
from discord.ext import commands
from discord import app_commands
from utils.gpt import generate_gpt_response
from utils.message_utils import send_message_in_chunks
from utils.users import UNBUTTERED_BAGEL_ID
from data.nickname import set_nickname as nn
async def define_set_nickname_command(tree, servers):
    @tree.command(name="set_nickname", description="Sets your nickname for all banana bread related activities", guilds=servers)
    async def set_nickname(interaction: discord.Interaction, user_input: str):
        new_nickname = await nn(interaction.user.id, user_input)
        await interaction.response.send_message(f"Your nickname has been set to {new_nickname}.")