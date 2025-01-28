from config.config import SERVERS
from data.firebase_voicechat import set_join_to_create_vc, get_join_to_create_vc
import discord
from discord.ext import commands
from discord import app_commands
from utils.users import UNBUTTERED_BAGEL_ID

class SetJoinToCreateVC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="set_join_to_create_vc", description="Sets the voice channel for creating temporary VCs.")
    @app_commands.describe(channel="The voice channel to be used for creating temporary VCs.")
    @app_commands.guilds(*SERVERS)
    @app_commands.check(lambda interaction: interaction.user.id == UNBUTTERED_BAGEL_ID)
    async def set_join_to_create_vc_command(self, interaction: discord.Interaction, channel: discord.VoiceChannel):
        existing_channel_id = await get_join_to_create_vc(interaction.guild.id)
        if existing_channel_id == channel.id:
            await interaction.response.send_message(f"The 'Join To Create VC' is already set to {channel.name}.", ephemeral=True)
            return

        await set_join_to_create_vc(interaction.guild.id, channel.id)
        await interaction.response.send_message(f"The 'Join To Create VC' has been set to {channel.name}.")

async def setup(bot):
    await bot.add_cog(SetJoinToCreateVC(bot))