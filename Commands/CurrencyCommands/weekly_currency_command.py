from data.Currency.weekly import try_collect_weekly
from discord.ext import commands
from discord import app_commands
import discord
from utils.emoji_helper import BANANA_COIN_EMOJI
from utils.gpt import generate_gpt_response

async def define_weekly_command(tree, servers):
    @tree.command(name="weekly", description="Collect your weekly bananas", guilds=servers)
    async def weekly(interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = str(interaction.user.id)
        can_collect, result = await try_collect_weekly(user_id)
        
        if not can_collect:
            wait_time = result
            formatted_wait_time = f"{wait_time.days} days, {wait_time.seconds // 3600} hours, and {(wait_time.seconds // 60) % 60} minutes"
            await interaction.followup.send(f"Please wait {formatted_wait_time} to collect your weekly bananas.")
        else:
            bananas_collected = result
            model = "gpt-4o"
            story = (f"You are a narrator telling a short story about how {interaction.user.mention} came across some money. Use 1 or 2 lines in BASIC markdown. At the end of your story, say '{interaction.user.mention} found: Then put some type of object'. Never any currency numbers. ")
            user_input = f"{interaction.user.mention} went on an adventure found their daily currency."
            response_message = await generate_gpt_response(model, story, user_input)
            response_message += f"\n +{bananas_collected} {BANANA_COIN_EMOJI}"

            await interaction.followup.send(response_message)
