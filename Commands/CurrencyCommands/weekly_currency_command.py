from data.Currency.weekly import try_collect_weekly
from discord.ext import commands
from discord import app_commands
import discord
from utils.emoji_helper import BANANA_COIN_EMOJI
from utils.gpt import generate_gpt_response

async def define_weekly_command(tree, servers):
    @tree.command(name="weekly", description="Collect your weekly bananas", guilds=servers)
    async def weekly(interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        can_collect, result = await try_collect_weekly(user_id)
        
        if not can_collect:
            wait_time = result
            formatted_wait_time = f"{wait_time.days} days, {wait_time.seconds // 3600} hours, and {(wait_time.seconds // 60) % 60} minutes"
            await interaction.response.send_message(f"Please wait {formatted_wait_time} to collect your weekly bananas.")
        else:
            bananas_collected = result
            model = "gpt-4o"
            story = f"You are a narrator talking about how somebody came across money. You do this in 1 or 2 lines and always mention the user along with how many banana coins, you can also use the emoji {BANANA_COIN_EMOJI}"
            user_input = f"{interaction.user.mention} collected {bananas_collected} bananas."
            response_message = await generate_gpt_response(model, story, user_input)
            await interaction.followup.send(response_message)
