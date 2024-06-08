import discord
from discord.ext import commands
from discord import app_commands
import os
from utils.audio_queue import AudioQueue

audio_queue = AudioQueue()

async def define_skip_youtube_audio_command(tree, servers):
    @tree.command(name="skip", description="Skips the current audio playback and starts the next one in the queue.", guilds=servers)
    async def skip(interaction: discord.Interaction):
        guild_id = interaction.guild_id
        voice_client = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild)

        if voice_client and voice_client.is_connected():
            if voice_client.is_playing():
                voice_client.stop()
                await play_next_audio(voice_client, guild_id, interaction)
                await interaction.response.send_message("Skipped to the next audio in the queue.")
            else:
                await interaction.response.send_message("No audio is currently playing.")
        else:
            await interaction.response.send_message("The bot is not connected to any voice channel.")

    async def play_next_audio(voice_client, guild_id, interaction):
        if not audio_queue.is_queue_empty(guild_id):
            track_info = audio_queue.next_track(guild_id)
            track = track_info["file"]
            track_url = track_info["url"]
            voice_client.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=track))
            await interaction.channel.send(f"Now playing: {track_url}")
        else:
            await interaction.channel.send("No more audios in the queue.")
