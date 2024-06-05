import os
import youtube_dl
import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import asyncio

async def define_play_youtube_audio_command(tree, servers):
    @tree.slash_command(name="play_youtube_audio", description="Downloads and plays the audio from a YouTube video in a voice channel.", guilds=servers)
    async def play_youtube_audio(ctx: discord.app_commands.SlashCommand, url: str):
        try:
            # Check if URL is valid
            if not ('youtube.com/watch?v=' in url or 'youtu.be/' in url):
                await ctx.send("Invalid YouTube URL provided.")
                return

            # Download audio
            downloaded_audio = await download_youtube_audio(url)

            # Connect to voice channel
            voice_channel = ctx.author.voice.channel
            voice_client = await voice_channel.connect()

            # Play audio
            voice_client.play(FFmpegPCMAudio(executable="ffmpeg", source=downloaded_audio))

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
            await ctx.send(f"Something went wrong! Please try again later.")

    async def download_youtube_audio(url: str) -> str:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': 'downloaded_audio.mp3',
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return 'downloaded_audio.mp3'

    def remove_file_if_exists(file_path: str):
        if os.path.exists(file_path):
            os.remove(file_path)
