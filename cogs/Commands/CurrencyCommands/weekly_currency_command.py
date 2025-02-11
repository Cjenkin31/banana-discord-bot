from GPT_stories import getStoryByRole
from config.config import SERVERS
from data.Currency.weekly import try_collect_weekly
from discord.ext import commands
from discord import app_commands
import discord
from utils.emoji_helper import BANANA_COIN_EMOJI
from utils.gpt import generate_gpt_response

GPT_MODEL = "gpt-4o"
STORY_TEMPLATE = (
    "You are a narrator telling a short story about how {user_display_name} came across some money. "
    "Use 1 or 2 sentences in BASIC markdown. At the end of your story, say '{user_display_name} found: "
    "Then put some type of object'. Never any currency numbers."
)

class WeeklyCurrencyCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def process_weekly(self, user_id: str, user_display_name: str) -> tuple[bool, str]:
        """Process the weekly currency collection and return the response message."""
        try:
            can_collect, result = await try_collect_weekly(user_id)
        except Exception as e:
            return False, f"Failed to process weekly collection: {e}"
        if not can_collect:
            wait_time = result
            formatted_wait_time = (
                f"{wait_time.days} days, "
                f"{wait_time.seconds // 3600} hours, and "
                f"{(wait_time.seconds // 60) % 60} minutes"
            )
            return False, formatted_wait_time
        bananas_collected = result
        story = getStoryByRole("bread", user_id) + STORY_TEMPLATE.format(user_display_name=user_display_name)
        user_input = f"{user_display_name} went on an adventure and found their weekly currency."

        try:
            response_message = await generate_gpt_response(GPT_MODEL, story, user_input)
        except Exception as e:
            response_message = f"Response took too long or had an error: {e}. Sorry! Here is your weekly currency."
        response_message += f"\n +{bananas_collected} {BANANA_COIN_EMOJI}"
        return True, response_message

    async def handle_weekly(self, user_id: str, user_display_name: str):
        """Handle the weekly collection process and send the response."""
        try:
            can_collect, response = await self.process_weekly(user_id, user_display_name)
            if can_collect:
                return response
            return f"Please wait {response} to collect your weekly bananas."
        except Exception as e:
            return f"An error occurred while processing your request: {e}"

    @commands.command(name="weekly", help="Collect your weekly bananas")
    async def weekly_cmd(self, ctx: commands.Context):
        """Handle the weekly command."""
        async with ctx.typing():
            user_id = str(ctx.author.id)
            user_display_name = ctx.author.display_name
            response_message = await self.handle_weekly(user_id, user_display_name)
            await ctx.send(response_message)

    @app_commands.guilds(*SERVERS)
    @app_commands.command(name="weekly", description="Collect your weekly bananas")
    async def weekly_app_cmd(self, interaction: discord.Interaction):
        """Handle the weekly slash command."""
        await interaction.response.defer(thinking=True)

        user_id = str(interaction.user.id)
        user_display_name = interaction.user.display_name
        response_message = await self.handle_weekly(user_id, user_display_name)
        await interaction.followup.send(response_message)

async def setup(bot: commands.Bot):
    """Set up the WeeklyCurrencyCommand."""
    await bot.add_cog(WeeklyCurrencyCommand(bot))