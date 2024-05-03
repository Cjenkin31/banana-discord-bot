from data.currency import add_bananas, get_bananas, remove_bananas
import discord
from discord.ext import commands
from discord import app_commands
import random

from utils.emoji_helper import BANANA_COIN_EMOJI 

async def define_eat_banana_command(tree, servers):
    @tree.command(name="eat_banana", description="Monkie eat", guilds=servers)
    async def eat_banana(interaction: discord.Interaction, amt: int = 1):
        banana_gif = "https://tenor.com/view/effy-gif-11375717773991506810"
        user_id = interaction.user.id
        user_banana = await get_bananas(user_id)
        response_message = ""  # Initialize response message string
        if user_banana < amt:
            response_message += f"YOU DON'T HAVE ENOUGH {BANANA_COIN_EMOJI} TO EAT\n"
            if interaction.response.is_done():
                await interaction.followup.send(response_message)
            else:
                await interaction.response.send_message(response_message)
            return
        if amt > 500:
            amt = 500
            response_message += "YOU HAVE BEEN LIMITED TO 500 BANANAS ( Thanks to <@407302203070742529> )\n"
        if random.randint(1, 10) == 1:
            response_message += f"You decide to give {amt} banana(s) to the bot instead 🎁!\n{banana_gif}\n"
            await add_bananas(1011022296741326910, amt)
            await remove_bananas(user_id, amt)
        else:
            banana_string = "🍌" * amt
            if amt == 1:
                response_message += f"You eat {amt} banana {banana_string}!\n"
            else:
                response_message += f"You eat {amt} bananas {banana_string}!\n"
            await remove_bananas(user_id, amt)

        response_message += banana_gif

        if interaction.response.is_done():
            await interaction.followup.send(response_message)
        else:
            await interaction.response.send_message(response_message)

