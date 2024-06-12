from config.config import SERVERS
import discord
from discord import app_commands
from discord import commands
import os
from utils.audio_queue import AudioQueue

audio_queue = AudioQueue()

@app_commands.guilds(SERVERS)
class StopYouTubeAudioCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="stop_youtube_audio", description="Stops the audio playback, clears the queue, and disconnects the bot from the voice channel.")
    async def stop_youtube_audio(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        if voice_client and voice_client.is_connected():
            if voice_client.is_playing():
                voice_client.stop()

            await voice_client.disconnect()

            await audio_queue.clear_queue(guild_id)
            await interaction.response.send_message("Disconnected and stopped playback. The queue has been cleared.")
        else:
            await interaction.response.send_message("The bot is not connected to any voice channel.")

    def remove_file_if_exists(self, file_path: str):
        if os.path.exists(file_path):
            os.remove(file_path)

def setup(bot):
    bot.add_cog(StopYouTubeAudioCommand(bot))
