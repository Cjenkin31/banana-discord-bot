
from data.currency import add_bananas, remove_bananas
import discord
from discord.ext import commands
from discord import app_commands
import random 

async def define_eat_banana_command(tree, servers):
    @tree.command(name="eat_banana", description="monkie eat", guilds=servers)
    async def eat_banana(interaction: discord.Interaction, amt: int = 1):
        banana_gif = "https://tenor.com/view/effy-gif-11375717773991506810"
        if random.randint(1, 10) == 1:
            await interaction.response.send_message(f"You decide to give {amt} banana(s) to the bot instead 🎁!\n{banana_gif}")
            await add_bananas(1011022296741326910, amt)
            await remove_bananas(interaction.user.id, amt)
        else:
            emoji_banana_amount = 0 
            banana_string = ""
            while emoji_banana_amount < amt:
                banana_string+="🍌"
                emoji_banana_amount+=1
            if amt == 1:
                message = f"You eat {amt} banana {banana_string}!"
            else:
                message = f"You eat {amt} bananas {banana_string}!"
            await remove_bananas(interaction.user.id, amt)
            await interaction.response.send_message(f"{message}\n{banana_gif}")

