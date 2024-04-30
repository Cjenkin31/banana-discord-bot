
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

        if amt > 500:
            amt = 500
            await interaction.response.send_message("YOU HAVE BEEN LIMITED TO 500 BANANAS ( Thanks to <@407302203070742529> )")
        elif user_banana < amt:
            if interaction.response.is_done():
                await interaction.followup.send(f"YOU DON'T HAVE ENOUGH {BANANA_COIN_EMOJI} TO EAT")
            else:
                await interaction.response.send_message(f"YOU DON'T HAVE ENOUGH {BANANA_COIN_EMOJI} TO EAT")
            return
        elif random.randint(1, 10) == 1:
            await interaction.followup.send(f"You decide to give {amt} banana(s) to the bot instead 🎁!\n{banana_gif}")
            await add_bananas(1011022296741326910, amt)
            await remove_bananas(user_id, amt)
            return
        else:
            emoji_banana_amount = 0 
            banana_string = ""
            while emoji_banana_amount < amt:
                banana_string += "🍌"
                emoji_banana_amount += 1
            if amt == 1:
                message = f"You eat {amt} banana {banana_string}!"
            else:
                message = f"You eat {amt} bananas {banana_string}!"
            await remove_bananas(user_id, amt)
            if interaction.response.is_done():
                await interaction.followup.send(f"{message}\n{banana_gif}")
            else:
                await interaction.response.send_message(f"{message}\n{banana_gif}")


