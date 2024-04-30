
from data.currency import add_bananas, remove_bananas
import discord
from discord.ext import commands
from discord.app_commands import command, describe
import random 

async def define_eat_banana_command(tree, servers):
    @tree.command(name="eat_banana", description="monkie eat", guilds=servers)
    async def eat_banana(self, interaction: discord.Interaction, amt: int = 1):
        banana_gif = "https://tenor.com/view/effy-gif-11375717773991506810"
        if random.randint(1, 10) == 1:
            await interaction.response.send_message(f"You decide to give {amt} banana(s) to the bot instead 🎁!\n{banana_gif}")
            add_bananas(1011022296741326910, amt)
            remove_bananas(interaction.user.id, amt)
        else:
            if amt == 1:
                message = f"You eat {amt} banana 🍌!"
            else:
                message = f"You eat {amt} bananas 🍌🍌!"
            remove_bananas(interaction.user.id, amt)
            await interaction.response.send_message(f"{message}\n{banana_gif}")

