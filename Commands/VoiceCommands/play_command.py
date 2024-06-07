import os
import time
import discord
from discord.ext import commands
from discord import app_commands
from discord import FFmpegPCMAudio
import asyncio
from pytube import YouTube
import uuid
from moviepy.editor import AudioFileClip
from utils.audio_queue import AudioQueue
# TODO: Add a audio queue
# TODO: Check to see if the bot can play in multiple servers at once, should append serverID to end of temp file to avid conflicts.
# TODO: Improve Error Handling
# TODO: Add skipping audio.
# TODO: New command for playing audio from links. Soundcloud, Spotify, etc.

audio_queue = AudioQueue()

async def define_play_youtube_audio_command(tree, servers):
    @tree.command(name="play_youtube_audio", description="Downloads and plays the audio from a YouTube video in a voice channel.", guilds=servers)
    @app_commands.describe(url="URL of the YouTube video")
    async def play_youtube_audio(interaction: discord.Interaction, url: str):
        guild_id = interaction.guild_id
        await interaction.response.defer()

        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.followup.send("You need to be in a voice channel to play audio.")
            return

        try:
            if not ('youtube.com/watch?v=' in url or 'youtu.be/' in url):
                await interaction.followup.send("Invalid YouTube URL provided.")
                return

            downloaded_audio = await download_youtube_audio(url, guild_id)
            audio_queue.add_to_queue(guild_id, downloaded_audio)
            await interaction.followup.send(f"Added to queue. Position: {len(audio_queue.get_queue(guild_id))}")

            voice_channel = interaction.user.voice.channel
            if voice_channel:
                voice_client = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild)
                if voice_client is None:
                    voice_client = await voice_channel.connect()
                if not voice_client.is_playing():
                    await play_audio(voice_client, guild_id)

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            await interaction.followup.send("Something went wrong! Please try again later.")

    async def play_audio(voice_client, guild_id):
        while audio_queue.get_queue(guild_id):
            track = audio_queue.next_track(guild_id)
            voice_client.play(FFmpegPCMAudio(executable="ffmpeg", source=track))
            while voice_client.is_playing():
                await asyncio.sleep(1)
            remove_file_if_exists(track)
        await voice_client.disconnect()

    async def download_youtube_audio(url: str, guild_id: int) -> str:
        yt = YouTube(url)
        stream = yt.streams.filter(only_audio=True).first()
        unique_id = uuid.uuid4()
        output_path = stream.download(filename=f'{guild_id}_downloaded_audio_{unique_id}.mp4')
        audio_clip = AudioFileClip(output_path)
        mp3_path = f'{guild_id}_downloaded_audio_{unique_id}.mp3'
        audio_clip.write_audiofile(mp3_path)
        audio_clip.close()
        remove_file_if_exists(output_path)
        return mp3_path

    def remove_file_if_exists(file_path: str):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"File removed: {file_path}")
        except Exception as e:
            print(f"Failed to remove file {file_path}: {e}")
