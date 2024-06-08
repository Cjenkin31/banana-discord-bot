from data.firebase_voicechat import set_join_to_create_vc, get_join_to_create_vc
import discord
from discord.ext import commands
from discord import app_commands
from utils.users import UNBUTTERED_BAGEL_ID

async def define_set_join_to_create_vc(tree, servers):
    def is_owner():
        async def predicate(interaction: discord.Interaction):
            return interaction.user.id == UNBUTTERED_BAGEL_ID
        return app_commands.check(predicate)

    @tree.command(name="set_join_to_create_vc", description="Sets the voice channel for creating temporary VCs.", guilds=servers)
    @app_commands.describe(channel="The voice channel to be used for creating temporary VCs.")
    @is_owner()
    async def set_join_to_create_vc_command(interaction: discord.Interaction, channel: discord.VoiceChannel):
        existing_channel_id = await get_join_to_create_vc(interaction.guild.id)
        if existing_channel_id == channel.id:
            await interaction.response.send_message(f"The 'Join To Create VC' is already set to {channel.name}.", ephemeral=True)
            return

        await set_join_to_create_vc(interaction.guild.id, channel.id)
        await interaction.response.send_message(f"The 'Join To Create VC' has been set to {channel.name}.")
