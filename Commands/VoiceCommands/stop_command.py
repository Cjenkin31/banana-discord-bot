import discord
from discord.ext import commands
from discord import app_commands
import os

async def define_stop_youtube_audio_command(tree, servers):
    @tree.command(name="stop_youtube_audio", description="Stops the audio playback and disconnects the bot from the voice channel.", guilds=servers)
    async def stop_youtube_audio(interaction: discord.Interaction):
        voice_client = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild)
        try:
            remove_file_if_exists("downloaded_audio.mp3")
        except Exception as e:
            print(f"Error removing file: {e}")
        if voice_client and voice_client.is_connected():
            if voice_client.is_playing():
                voice_client.stop()

            await voice_client.disconnect()
            await interaction.response.send_message("Disconnected and stopped playback.")
        else:
            await interaction.response.send_message("The bot is not connected to any voice channel.")

    def remove_file_if_exists(file_path: str):
        if os.path.exists(file_path):
            os.remove(file_path)