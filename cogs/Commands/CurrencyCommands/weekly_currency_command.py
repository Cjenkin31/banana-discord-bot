from config.config import SERVERS
from data.Currency.weekly import try_collect_weekly
from discord.ext import commands
from discord import app_commands
import discord
from utils.emoji_helper import BANANA_COIN_EMOJI
from utils.gpt import generate_gpt_response

class WeeklyCurrencyCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def collect_weekly(self, user_id, user_mention):
        can_collect, result = await try_collect_weekly(user_id)
        
        if not can_collect:
            wait_time = result
            formatted_wait_time = f"{wait_time.days} days, {wait_time.seconds // 3600} hours, and {(wait_time.seconds // 60) % 60} minutes"
            return False, f"Please wait {formatted_wait_time} to collect your weekly bananas."
        else:
            bananas_collected = result
            model = "gpt-4o"
            story = (f"You are a narrator telling a short story about how {user_mention} came across some money. Use 1 or 2 lines in BASIC markdown. At the end of your story, say '{user_mention} found: Then put some type of object'. Never any currency numbers.")
            user_input = f"{user_mention} went on an adventure found their weekly currency."
            response_message = await generate_gpt_response(model, story, user_input)
            response_message += f"\n +{bananas_collected} {BANANA_COIN_EMOJI}"
            return True, response_message

    @app_commands.command(name="weekly", description="Collect your weekly bananas")
    @app_commands.guilds(*SERVERS)
    async def weekly_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = str(interaction.user.id)
        can_collect, response_message = await self.collect_weekly(user_id, interaction.user.mention)
        
        if can_collect:
            await interaction.followup.send(response_message)
        else:
            await interaction.followup.send(response_message)

    @commands.command(name="weekly", help="Collect your weekly bananas")
    async def weekly_text(self, ctx):
        async with ctx.typing():
            user_id = str(ctx.author.id)
            can_collect, response_message = await self.collect_weekly(user_id, ctx.author.mention)
        
        if can_collect:
            await ctx.send(response_message)
        else:
            await ctx.send(response_message)

async def setup(bot):
    await bot.add_cog(WeeklyCurrencyCommand(bot))
