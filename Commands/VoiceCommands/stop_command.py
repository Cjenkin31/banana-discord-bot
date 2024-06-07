import discord
from discord.ext import commands
from discord import app_commands
import os
from utils.audio_queue import AudioQueue

audio_queue = AudioQueue()

async def define_stop_youtube_audio_command(tree, servers):
    @tree.command(name="stop_youtube_audio", description="Stops the audio playback, clears the queue, and disconnects the bot from the voice channel.", guilds=servers)
    async def stop_youtube_audio(interaction: discord.Interaction):
        guild_id = interaction.guild_id
        voice_client = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild)
        if voice_client and voice_client.is_connected():
            if voice_client.is_playing():
                voice_client.stop()

            await voice_client.disconnect()

            audio_queue.clear_queue(guild_id)
            await interaction.response.send_message("Disconnected and stopped playback. The queue has been cleared.")
        else:
            await interaction.response.send_message("The bot is not connected to any voice channel.")

    def remove_file_if_exists(file_path: str):
        if os.path.exists(file_path):
            os.remove(file_path)
