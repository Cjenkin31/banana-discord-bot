import uuid
from config.config import SERVERS
import discord
from discord.ext import commands
from discord import app_commands
import logging
from data.auth import get_auth_token, set_auth_token

class AuthTokenCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def dm_user(self, user, message):
        try:
            await user.send(message)
        except discord.Forbidden:
            logging.error("Failed to send DM: Check the user's privacy settings.")
            return False
        return True

    @app_commands.command(name="get_auth_token", description="Get your authentication token")
    @app_commands.guilds(*SERVERS)
    async def get_auth_token_command(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user_id = interaction.user.id
        token = await get_auth_token(user_id)

        if not token:
            new_token = str(uuid.uuid4()).replace('-', '')
            if not await set_auth_token(user_id, new_token):
                await interaction.followup.send("Failed to generate a token. Please try again later.", ephemeral=True)
                return
            token = new_token

        message = f"Here is your userID\n```{user_id}```\nHere is your authentication token (This is specific to banana bread activities):\n ```{token}```\nKeep it safe!"

        if not await self.dm_user(interaction.user, message):
            await interaction.followup.send("I couldn't send you a DM. Please check your privacy settings and try again.", ephemeral=True)
        else:
            await interaction.followup.send("I've sent you your authentication token via DM!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AuthTokenCog(bot))
