from datetime import datetime
from config.config import SERVERS
from data.Currency.daily import try_collect_daily
from data.name import add_name_if_not_exist_to_database
from discord.ext import commands
from discord import app_commands
import discord
import logging
from utils.emoji_helper import BANANA_COIN_EMOJI
from GPT_stories import getStoryByRole
from utils.gpt import generate_gpt_response
from utils.holidays import HOLIDAYS

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Or adjust to INFO/ERROR depending on verbosity desired

GPT_MODEL = "gpt-4o"
STORY_TEMPLATE = (
    "You are a narrator telling a short story about how {user_display_name} came across some money. "
    "Use 1 or 2 sentences in BASIC markdown. At the end of your story, say '{user_display_name} found: "
    "Then put some type of object'. Never any currency numbers."
)

class DailyCurrencyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def process_daily(self, user_id: str, user_display_name: str) -> tuple[bool, str]:
        """Process the daily currency collection and return the response message."""
        try:
            await add_name_if_not_exist_to_database(user_id, user_display_name)
            can_collect, result = await try_collect_daily(user_id)
        except Exception as e:
            return False, f"Failed to process daily collection: {e}"
        if not can_collect:
            wait_time = result
            formatted_wait_time = (
                f"{wait_time.seconds // 3600} hours, "
                f"{(wait_time.seconds // 60) % 60} minutes, and "
                f"{wait_time.seconds % 60} seconds"
            )
            return False, formatted_wait_time
        bananas_collected = result
        story = getStoryByRole("bread", user_id) + STORY_TEMPLATE.format(user_display_name=user_display_name)
        user_input = f"{user_display_name} went on an adventure and found their daily currency."
        # If the current date is a holiday, add the holiday to the story.
        if (datetime.utcnow().month, datetime.utcnow().day) in HOLIDAYS:
            story += f" Today is {HOLIDAYS[(datetime.utcnow().month, datetime.utcnow().day)]['name']}! Please include this in your story."

        try:
            response_message = await generate_gpt_response(GPT_MODEL, story, user_input)
        except Exception as e:
            response_message = f"Response took too long or had an error: {e}. Sorry! Here is your daily currency."
        response_message += f"\n +{bananas_collected} {BANANA_COIN_EMOJI}"
        return True, response_message

    async def handle_daily(self, user_id: str, user_display_name: str):
        """Handle the daily collection process and send the response."""
        try:
            can_collect, response = await self.process_daily(user_id, user_display_name)
            if can_collect:
                return response
            return f"Please wait {response} to collect your daily bananas."
        except Exception as e:
            return f"An error occurred while processing your request: {e}"

    @commands.command(name="daily", help="Collect your daily bananas")
    async def daily_cmd(self, ctx: commands.Context):
        """Handle the daily command."""
        async with ctx.typing():
            user_id = str(ctx.author.id)
            user_display_name = ctx.author.display_name
            resposne_message = await self.handle_daily(user_id, user_display_name)
            await ctx.send(resposne_message)

    @app_commands.guilds(*SERVERS)
    @app_commands.command(name="daily", description="Collect your daily bananas")
    async def daily_app_cmd(self, interaction: discord.Interaction):
        """Handle the daily slash command."""
        await interaction.response.defer(thinking=True)

        user_id = str(interaction.user.id)
        user_display_name = interaction.user.display_name
        response_message = await self.handle_daily(user_id, user_display_name)
        await interaction.followup.send(response_message)

async def setup(bot: commands.Bot):
    """Set up the DailyCurrencyCog."""
    await bot.add_cog(DailyCurrencyCog(bot))