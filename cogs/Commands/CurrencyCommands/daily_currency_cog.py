from config.config import SERVERS
from data.Currency.daily import try_collect_daily
from data.name import add_name_if_not_exist_to_database
from discord.ext import commands
from discord import app_commands
import discord
from utils.emoji_helper import BANANA_COIN_EMOJI
from utils.gpt import generate_gpt_response

class DailyCurrencyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(*SERVERS)
    @app_commands.command(name="daily", description="Collect your daily bananas")
    async def daily(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        await add_name_if_not_exist_to_database(user_id, interaction.user.display_name)
        can_collect, result = await try_collect_daily(user_id)
        if not can_collect:
            wait_time = result
            formatted_wait_time = f"{wait_time.seconds // 3600} hours and {(wait_time.seconds // 60) % 60} minutes"
            await interaction.response.send_message(f"Please wait {formatted_wait_time} to collect your daily bananas.")
        else:
            await interaction.response.defer()
            bananas_collected = result
            model = "gpt-4o"
            story = (f"You are a narrator telling a short story about how {interaction.user.mention} came across some money. Use 1 or 2 lines in BASIC markdown. At the end of your story, say '{interaction.user.mention} found: Then put some type of object'. Never any currency numbers. ")
            user_input = f"{interaction.user.mention} went on an adventure found their daily currency."
            response_message = await generate_gpt_response(model, story, user_input)
            response_message += f"\n +{bananas_collected} {BANANA_COIN_EMOJI}"

            await interaction.followup.send(response_message)

async def setup(bot):
    await bot.add_cog(DailyCurrencyCog(bot))