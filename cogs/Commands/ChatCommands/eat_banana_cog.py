from config.config import SERVERS
from data.Currency.currency import add_bananas, get_bananas, remove_bananas
import discord
from discord.ext import commands
from discord import app_commands
import random
from utils.emoji_helper import BANANA_COIN_EMOJI 
from utils.message_utils import send_message_in_chunks

class EatBananaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="eat_banana", description="Monkie eat")
    @app_commands.guilds(*SERVERS)
    async def eat_banana(self, interaction: discord.Interaction, amt: int = 1):
        await interaction.response.defer()
        response_message = await self.process_eating(interaction, amt)
        await send_message_in_chunks(response_message, interaction)

    async def process_eating(self, interaction: discord.Interaction, amt: int):
        banana_gif = "https://tenor.com/view/effy-gif-11375717773991506810"
        user_id = interaction.user.id
        user_banana = await get_bananas(user_id)
        response_message = ""
        if user_banana < amt:
            response_message += f"YOU DON'T HAVE ENOUGH {BANANA_COIN_EMOJI} TO EAT\n"
            return
        if random.randint(1, 10) == 1:
            response_message += f"You decide to give {amt} banana(s) to the bot instead 🎁!\n{banana_gif}\n"
            await add_bananas(1011022296741326910, amt)
            await remove_bananas(user_id, amt)
        else:
            banana_string = "🍌" * amt
            response_message += f"You eat {amt} banana{'s' if amt > 1 else ''} {banana_string}!\n"
            await remove_bananas(user_id, amt)

        response_message += banana_gif
        return response_message

async def setup(bot):
    await bot.add_cog(EatBananaCog(bot))
