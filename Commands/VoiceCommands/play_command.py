import os
import time
import discord
from discord.ext import commands
from discord import app_commands
from discord import FFmpegPCMAudio
import asyncio
from pytube import YouTube
from moviepy.editor import AudioFileClip

# TODO: Add a audio queue
# TODO: Check to see if the bot can play in multiple servers at once, should append serverID to end of temp file to avid conflicts.
# TODO: Improve Error Handling
# TODO: Add skipping audio.
# TODO: New command for playing audio from links. Soundcloud, Spotify, etc.

async def define_play_youtube_audio_command(tree, servers):
    @tree.command(name="play_youtube_audio", description="Downloads and plays the audio from a YouTube video in a voice channel.", guilds=servers)
    @app_commands.describe(url="URL of the YouTube video")
    async def play_youtube_audio(interaction: discord.Interaction, url: str):
        await interaction.response.defer()
        try:
            # Check if URL is valid
            if not ('youtube.com/watch?v=' in url or 'youtu.be/' in url):
                await interaction.followup.send("Invalid YouTube URL provided.")
                return

            # Download audio
            downloaded_audio = await download_youtube_audio(url)

            # Connect to voice channel
            voice_channel = interaction.user.voice.channel
            voice_client = await voice_channel.connect()

            # Play audio
            voice_client.play(FFmpegPCMAudio(executable="ffmpeg", source=downloaded_audio))
            await interaction.followup.send(f"Playing audio from {url} in {voice_channel.name}.")

            # Wait for audio to finish playing, then disconnect and remove file
            while voice_client.is_playing() and voice_channel.members:
                await asyncio.sleep(1)

            if not voice_channel.members:
                voice_client.stop()
                await voice_client.disconnect()
                remove_file_if_exists(downloaded_audio)
                return

            if 'youtube.com/watch?v=' in url or 'youtu.be/' in url:
                voice_client.stop()
                remove_file_if_exists(downloaded_audio)
                downloaded_audio = await download_youtube_audio(url)
                voice_client.play(FFmpegPCMAudio(executable="ffmpeg", source=downloaded_audio))

            await voice_client.disconnect()
            remove_file_if_exists(downloaded_audio)

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            await interaction.followup.send(f"Something went wrong! Please try again later.")

    async def download_youtube_audio(url: str) -> str:
        try:
            yt = YouTube(url)
            stream = yt.streams.filter(only_audio=True).first()
            output_path = stream.download(filename='downloaded_audio.mp4')

            # Convert mp4 to mp3
            audio_clip = AudioFileClip(output_path)
            audio_clip.write_audiofile('downloaded_audio.mp3')
            audio_clip.close()
            os.remove(output_path)

            return 'downloaded_audio.mp3'

        except Exception as e:
            print(f"Error downloading audio: {e}")
            raise

    def remove_file_if_exists(file_path: str):
        if os.path.exists(file_path):
            os.remove(file_path)