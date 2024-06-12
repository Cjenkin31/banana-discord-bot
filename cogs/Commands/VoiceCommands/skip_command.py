from config.config import SERVERS
import discord
from discord import app_commands
from discord.ext import commands
from utils.audio_queue import AudioQueue

audio_queue = AudioQueue()

class SkipCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="skip", description="Skips the current audio playback and starts the next one in the queue.")
    @app_commands.guilds(SERVERS)
    async def skip(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)

        if voice_client and voice_client.is_connected():
            if voice_client.is_playing():
                voice_client.stop()
                await self.play_next_audio(voice_client, guild_id, interaction)
                await interaction.response.send_message("Skipped to the next audio in the queue.")
            else:
                await interaction.response.send_message("No audio is currently playing.")
        else:
            await interaction.response.send_message("The bot is not connected to any voice channel.")

    async def play_next_audio(self, voice_client, guild_id, interaction):
        if not await audio_queue.is_queue_empty(guild_id):
            track_info = await audio_queue.next_track(guild_id)
            if track_info:
                track = track_info["file"]
                track_url = track_info["url"]
                voice_client.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=track))
                await interaction.channel.send(f"Now playing: {track_url}")
        else:
            await interaction.channel.send("No more audios in the queue.")

def setup(bot):
    bot.add_cog(SkipCommand(bot))
