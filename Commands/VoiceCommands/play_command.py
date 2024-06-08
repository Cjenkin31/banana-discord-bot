import os
import discord
from discord.ext import commands
from discord import app_commands
from discord import FFmpegPCMAudio
import asyncio
from pytube import YouTube, Playlist
import uuid
from moviepy.editor import AudioFileClip
from utils.audio_queue import AudioQueue
from pytube.exceptions import VideoUnavailable, PytubeError

# TODO: Support for playlists
# TODO: New command for playing audio from links. Soundcloud, Spotify, etc.

audio_queue = AudioQueue()

async def define_play_youtube_audio_command(tree, servers):
    @tree.command(name="play_youtube_audio", description="Downloads and plays the audio from a YouTube video or playlist in a voice channel.", guilds=servers)
    @app_commands.describe(url="URL of the YouTube video or playlist")
    async def play_youtube_audio(interaction: discord.Interaction, url: str):
        guild_id = interaction.guild_id
        await interaction.response.defer()

        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.followup.send("You need to be in a voice channel to play audio.")
            return

        try:
            if ('youtube.com/playlist?list=' in url or 'youtube.com/watch?v=' in url or 'youtu.be/' in url):
                await process_url(url, guild_id, interaction)
            else:
                await interaction.followup.send("Invalid YouTube URL provided.")
                return

            voice_channel = interaction.user.voice.channel
            voice_client = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild)
            if voice_client is None:
                voice_client = await voice_channel.connect()
            
            if not voice_client.is_playing():
                await play_audio(voice_client, guild_id, interaction)

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            await interaction.followup.send("Something went wrong! Please try again later.")

    async def process_url(url, guild_id, interaction):
        if 'playlist?list=' in url:
            playlist = Playlist(url)
            for video in playlist.videos:
                downloaded_audio = await download_with_retry(video.watch_url, guild_id)
                await audio_queue.add_to_queue(guild_id, {"file": downloaded_audio, "url": video.watch_url})
        else:
            downloaded_audio = await download_with_retry(url, guild_id)
            await audio_queue.add_to_queue(guild_id, {"file": downloaded_audio, "url": url})
        
        await interaction.followup.send(f"Added to queue. Position: {await audio_queue.queue_length(guild_id)}")

    async def play_audio(voice_client, guild_id, interaction):
        while not await audio_queue.is_queue_empty(guild_id):
            track_info = await audio_queue.next_track(guild_id)
            if not track_info:
                break

            track = track_info["file"]
            track_url = track_info["url"]
            voice_client.play(FFmpegPCMAudio(executable="ffmpeg", source=track))
            await interaction.channel.send(f"Now playing: {track_url}")
            while voice_client.is_playing():
                await asyncio.sleep(1)
            remove_file_if_exists(track)
        
        await voice_client.disconnect()

    async def download_with_retry(url: str, guild_id: int, max_retries=3):
        for attempt in range(max_retries):
            try:
                return await download_youtube_audio(url, guild_id)
            except (VideoUnavailable, PytubeError, KeyError) as e:
                print(f"Error occurred: {e}")
                if 'streamingData' in str(e):
                    print("YouTube streaming data extraction failed.")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
            except Exception as e:
                print(f"An error occurred: {e}")
                raise

    async def download_youtube_audio(url: str, guild_id: int) -> str:
        try:
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
        except VideoUnavailable:
            print("The video is unavailable, possibly due to being private or deleted.")
            raise
        except PytubeError as e:
            print(f"An error occurred with PyTube: {e}")
            raise
        except KeyError as e:
            if 'streamingData' in str(e):
                print("YouTube streaming data extraction failed.")
            raise
        except Exception as e:
            print(f"An error occurred while downloading: {e}")
            raise

    def remove_file_if_exists(file_path: str):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"File removed: {file_path}")
        except Exception as e:
            print(f"Failed to remove file {file_path}: {e}")