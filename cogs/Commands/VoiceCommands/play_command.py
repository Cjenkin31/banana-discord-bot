import os
from config.config import SERVERS
import discord
from discord.ext import commands
from discord import app_commands
from discord import FFmpegPCMAudio
import asyncio
from pytube import Playlist
from utils.audio_queue import AudioQueue
from pytube.exceptions import VideoUnavailable, PytubeError
from typing import List
from utils.downloader import Downloader

MAX_DOWNLOAD_SONGS_AT_A_TIME = 2
audio_queue = AudioQueue()

@app_commands.guilds(*SERVERS)
class PlayCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.downloader = None

    @app_commands.command(
        name="play_youtube_audio",
        description="Downloads and plays the audio from a YouTube video or playlist in a voice channel."
    )
    @app_commands.describe(url="URL of the YouTube video or playlist")
    async def play_youtube_audio(self, interaction: discord.Interaction, url: str):
        guild_id = interaction.guild_id
        await interaction.response.defer()
        self.downloader = Downloader(guild_id)

        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.followup.send("You need to be in a voice channel to play audio.")
            return

        try:
            # Basic YouTube URL check
            if any(k in url for k in ["youtube.com/playlist?list=", "youtube.com/watch?v=", "youtu.be/"]):
                voice_channel = interaction.user.voice.channel
                voice_client = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild)
                if voice_client is None:
                    try:
                        voice_client = await voice_channel.connect()
                    except Exception as e:
                        await interaction.followup.send(f"Failed to join voice channel: {str(e)}")
                        return

                print("Starting process_task")
                process_task = asyncio.create_task(
                    self.process_url_and_play_first_song(url, guild_id, voice_client, interaction)
                )
                await process_task
            else:
                await interaction.followup.send("Invalid YouTube URL provided.")
                return

        except Exception as e:
            print(f"An error occurred in main play_youtube_audio: {str(e)}")
            await interaction.followup.send("Something went wrong! Please try again later.")

    async def process_url_and_play_first_song(self, url, guild_id, voice_client, interaction):
        try:
            songs = []
            if 'playlist?list=' in url:
                playlist = Playlist(url)
                if playlist is None:
                    return
                songs = list(playlist.video_urls)
                if not songs:
                    print("Playlist video_urls is None or empty")
                    return
                print(f"Playlist contains {len(songs)} videos")
            else:
                songs = [url]

            first_song = songs.pop(0)
            first_song_path = await self.downloader.download_song(first_song)
            play_task = None  # Initialize to avoid E0606

            if first_song_path:
                await audio_queue.add_to_queue(guild_id, {"file": first_song_path, "url": first_song})
                play_task = asyncio.create_task(self.play_audio(voice_client, guild_id, interaction))

            # Download the rest in groups
            await self.download_songs_in_groups(songs, guild_id, retry=False)

            # Only await if we actually created the play task
            if play_task:
                await play_task

        except Exception as e:
            print(f"An error occurred in process_url_and_play_first_song: {e}")

    async def download_songs_in_groups(self, songs: List[str], guild_id: int, retry: bool):
        """
        Download songs in small groups, storing tasks in (task, song) pairs
        so we know which 'song' corresponds to which task.
        """
        try:
            while songs:
                if not isinstance(songs, list):
                    print(f"Expected list of songs, got {type(songs)} instead. Exiting loop.")
                    break
                if len(songs) == 0:
                    print("Songs list is empty. Exiting loop.")
                    break

                songs_to_download = songs[:MAX_DOWNLOAD_SONGS_AT_A_TIME]
                print(f"Downloading {len(songs_to_download)} songs...")
                try:
                    songs = songs[MAX_DOWNLOAD_SONGS_AT_A_TIME:]
                except Exception as e:
                    print(f"Error while slicing songs: {e}")
                    break

                # Create a list of (task, song) pairs
                tasks_and_songs = []
                for s in songs_to_download:
                    if s is None:
                        print("Encountered a None URL in songs_to_download")
                        continue
                    if retry:
                        t = asyncio.create_task(self.download_with_retry(s, guild_id))
                    else:
                        t = asyncio.create_task(self.downloader.download_song(s))
                    tasks_and_songs.append((t, s))

                # Now await each task and queue the result
                for task, orig_song in tasks_and_songs:
                    try:
                        downloaded_audio = await task
                        if downloaded_audio:
                            await audio_queue.add_to_queue(
                                guild_id, {"file": downloaded_audio, "url": orig_song}
                            )
                    except Exception as e:
                        print(f"An error occurred while downloading a song: {e}")

        except Exception as e:
            print(f"An error occurred in download_songs_in_groups: {e}")

    async def play_audio(self, voice_client, guild_id, interaction):
        """
        Keep playing from the queue until empty, then disconnect.
        """
        try:
            while True:
                try:
                    track_info = await audio_queue.next_track(guild_id)
                    if track_info is None:
                        # Possibly the queue is empty, check again
                        if await audio_queue.is_queue_empty(guild_id):
                            print("Queue is empty, disconnecting...")
                            break
                        await asyncio.sleep(1)
                        continue

                    if voice_client and voice_client.is_connected():
                        track = track_info["file"]
                        track_url = track_info["url"]
                        print(f"Now playing: {track_url}, track file: {track}")
                        voice_client.play(FFmpegPCMAudio(executable="ffmpeg", source=track))
                        await interaction.channel.send(f"Now playing: {track_url}")

                        while voice_client.is_playing():
                            await asyncio.sleep(1)

                        self.remove_file_if_exists(track)
                    else:
                        print("Voice client not connected or is None")
                        break
                except Exception as e:
                    print(f"An error occurred in play_audio loop: {e}")
                    break
        except Exception as e:
            print(f"An error occurred in play_audio: {e}")
        finally:
            if voice_client:
                await voice_client.disconnect()

    async def download_with_retry(self, url: str, _: int, max_retries=3):
        """
        Attempt to download a song multiple times. If it fails, raise.
        """
        for attempt in range(max_retries):
            try:
                return await self.downloader.download_song(url)
            except (VideoUnavailable, PytubeError, KeyError) as e:
                print(f"Error occurred: {e}")
                if 'streamingData' in str(e):
                    print("YouTube streaming data extraction failed.")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise
            except Exception as e:
                print(f"An error occurred in download_with_retry: {e}")
                raise

    def remove_file_if_exists(self, file_path: str):
        """Delete the file if it still exists."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"File removed: {file_path}")
        except Exception as e:
            print(f"Failed to remove file {file_path}: {e}")

async def setup(bot):
    await bot.add_cog(PlayCommand(bot))
