import uuid
import discord
from discord.ext import commands
from discord import app_commands
import logging
from data.auth import get_auth_token, set_auth_token

async def dm_user(user, message):
    try:
        await user.send(message)
    except discord.Forbidden:
        logging.error("Failed to send DM: Check the user's privacy settings.")
        return False
    return True

async def define_auth_token_command(tree, servers):
    @tree.command(name="get_auth_token", description="Get your authentication token", guilds=servers)
    async def get_auth_token_command(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user_id = interaction.user.id
        token = await get_auth_token(user_id)
        
        if not token:
            new_token = str(uuid.uuid4()).replace('-', '')
            if not await set_auth_token(user_id, new_token):
                await interaction.followup.send("Failed to generate a token. Please try again later.", ephemeral=True)
                return
            token = new_token
        
        message = f"Here is your userID\n```{user_id}```\nHere is your authentication token( This is specific to banana bread activites ):\n ```{token}```\nKeep it safe!"
        
        if not await dm_user(interaction.user, message):
            await interaction.followup.send("I couldn't send you a DM. Please check your privacy settings and try again.", ephemeral=True)
        else:
            await interaction.followup.send("I've sent you your authentication token via DM!", ephemeral=True)
