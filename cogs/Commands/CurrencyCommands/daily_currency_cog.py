from config.config import SERVERS
from data.Currency.daily import try_collect_daily
from data.name import add_name_if_not_exist_to_database
from discord.ext import commands
from discord import app_commands
import discord
from utils.emoji_helper import BANANA_COIN_EMOJI
from utils.gpt import generate_gpt_response

GPT_MODEL = "gpt-4o"
STORY_TEMPLATE = (
    "You are a narrator telling a short story about how {user_display_name} came across some money. "
    "Use 1 or 2 lines in BASIC markdown. At the end of your story, say '{user_display_name} found: "
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
        story = STORY_TEMPLATE.format(user_display_name=user_display_name)
        user_input = f"{user_display_name} went on an adventure and found their daily currency."
        
        try:
            response_message = await generate_gpt_response(GPT_MODEL, story, user_input)
        except Exception as e:
            response_message = f"Response took too long or had an error: {e}. Sorry! Here is your daily currency."
        
        response_message += f"\n +{bananas_collected} {BANANA_COIN_EMOJI}"
        return True, response_message

    @commands.command(name="daily", help="Collect your daily bananas")
    async def daily_cmd(self, ctx: commands.Context):
        """Handle the daily command."""
        try:
            async with ctx.typing():
                user_id = str(ctx.author.id)
                user_display_name = ctx.author.display_name
                can_collect, response = await self.process_daily(user_id, user_display_name)
            
            if can_collect:
                await ctx.send(response)
            else:
                await ctx.send(f"Please wait {response} to collect your daily bananas.")
        except Exception as e:
            await ctx.send(f"An error occurred while processing your request: {e}")

    @app_commands.guilds(*SERVERS)
    @app_commands.command(name="daily", description="Collect your daily bananas")
    async def daily_app_cmd(self, interaction: discord.Interaction):
        """Handle the daily slash command."""
        try:
            user_id = str(interaction.user.id)
            user_display_name = interaction.user.display_name
            can_collect, response = await self.process_daily(user_id, user_display_name)
            
            if can_collect:
                await interaction.response.defer()
                await interaction.followup.send(response)
            else:
                await interaction.response.send_message(f"Please wait {response} to collect your daily bananas.")
        except Exception as e:
            await interaction.response.send_message(f"An error occurred while processing your request: {e}")

async def setup(bot: commands.Bot):
    """Set up the DailyCurrencyCog."""
    await bot.add_cog(DailyCurrencyCog(bot))