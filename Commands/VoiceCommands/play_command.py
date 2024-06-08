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
from typing import List, Union
from concurrent.futures import ThreadPoolExecutor
from yt_dlp import YoutubeDL

audio_queue = AudioQueue()
MAX_DOWNLOAD_SONGS_AT_A_TIME = 3  # Define the maximum number of simultaneous downloads

class Downloader:
    __YDL_OPTIONS = {'format': 'bestaudio/best',
                     'default_search': 'auto',
                     'playliststart': 0,
                     'extract_flat': False,
                     'quiet': True,
                     'ignore_no_formats_error': True
                     }
    __YDL_OPTIONS_EXTRACT = {'format': 'bestaudio/best',
                             'default_search': 'auto',
                             'playliststart': 0,
                             'extract_flat': True,
                             'quiet': True,
                             'ignore_no_formats_error': True
                             }
    __YDL_OPTIONS_FORCE_EXTRACT = {'format': 'bestaudio/best',
                                   'default_search': 'auto',
                                   'playliststart': 0,
                                   'extract_flat': False,
                                   'quiet': True,
                                   'ignore_no_formats_error': True
                                   }
    __BASE_URL = 'https://www.youtube.com/watch?v={}'

    def __init__(self) -> None:
        self.__music_keys_only = ['resolution', 'fps', 'quality']
        self.__not_extracted_keys_only = ['ie_key']
        self.__not_extracted_not_keys = ['entries']
        self.__playlist_keys = ['entries']

    def finish_one_song(self, song: str) -> dict:
        try:
            if song is None:
                return None

            if self.is_url(song):
                song_info = self.__download_url(song)
            else:
                song_info = self.__download_title(song)

            return song_info
        except Exception as e:
            print(f"Error downloading song: {e}")
            raise

    @staticmethod
    def is_url(url: str) -> bool:
        return url.startswith("http")

    def __get_forced_extracted_info(self, url: str) -> dict:
        options = Downloader.__YDL_OPTIONS_FORCE_EXTRACT
        with YoutubeDL(options) as ydl:
            try:
                extracted_info = ydl.extract_info(url, download=False)
                return extracted_info
            except Exception as e:
                print(f'Error forcing extract: {e}')
                return {}

    def __download_url(self, url) -> dict:
        options = Downloader.__YDL_OPTIONS
        with YoutubeDL(options) as ydl:
            try:
                result = ydl.extract_info(url, download=False)
                return result
            except Exception as e:
                print(f'Error downloading URL: {e}')
                return {}

    def __download_title(self, title: str) -> dict:
        options = Downloader.__YDL_OPTIONS
        with YoutubeDL(options) as ydl:
            try:
                search = f'ytsearch:{title}'
                extracted_info = ydl.extract_info(search, download=False)

                if self.__failed_to_extract(extracted_info):
                    extracted_info = self.__get_forced_extracted_info(title)

                if extracted_info is None:
                    return {}

                if self.__is_multiple_musics(extracted_info):
                    if len(extracted_info['entries']) == 0:
                        return {}
                    return extracted_info['entries'][0]
                else:
                    print(f'Failed to extract title: {title}')
                    return {}
            except Exception as e:
                print(f'Error downloading title: {e}')
                return {}

    def __is_multiple_musics(self, extracted_info: dict) -> bool:
        for key in self.__playlist_keys:
            if key not in extracted_info.keys():
                return False
        return True

    def __failed_to_extract(self, extracted_info: dict) -> bool:
        if type(extracted_info) is not dict:
            return False

        for key in self.__not_extracted_keys_only:
            if key not in extracted_info.keys():
                return False
        for key in self.__not_extracted_not_keys:
            if key in extracted_info.keys():
                return False
        return True

    async def download_song(self, url: str, guild_id: int) -> str:
        try:
            yt = YouTube(url)
            stream = yt.streams.filter(only_audio=True).first()
            if stream is None:
                print(f"No audio stream found for URL: {url}")
                return None

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
            print(f"An error occurred in download_youtube_audio: {e}")
            raise

downloader = Downloader()

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
            if 'youtube.com/playlist?list=' in url or 'youtube.com/watch?v=' in url or 'youtu.be/' in url:
                voice_channel = interaction.user.voice.channel
                voice_client = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild)
                if voice_client is None:
                    try:
                        voice_client = await voice_channel.connect()
                    except Exception as e:
                        await interaction.followup.send(f"Failed to join voice channel: {str(e)}")
                        return

                # Start processing the URL and playing audio concurrently
                process_task = asyncio.create_task(process_url(url, guild_id))
                play_task = asyncio.create_task(play_audio(voice_client, guild_id, interaction, process_task))
                await asyncio.gather(process_task, play_task)
            else:
                await interaction.followup.send("Invalid YouTube URL provided.")
                return

        except Exception as e:
            print(f"An error occurred in main play_youtube_audio: {str(e)}")
            await interaction.followup.send("Something went wrong! Please try again later.")

    async def process_url(url, guild_id):
        if 'playlist?list=' in url:
            playlist = Playlist(url)
            songs = playlist.video_urls
            if songs is None:
                print("Playlist video_urls is None")
            else:
                print(f"Playlist contains {len(songs)} videos")
            await download_songs_in_lots(songs, guild_id, retry=False)
        else:
            await download_songs_in_lots([url], guild_id, retry=True)

    async def download_songs_in_lots(songs: List[str], guild_id: int, retry: bool):
        while songs:
            # Limit the number of concurrent downloads
            songs_to_download = songs[:MAX_DOWNLOAD_SONGS_AT_A_TIME]
            songs = songs[MAX_DOWNLOAD_SONGS_AT_A_TIME:]

            tasks = []
            for song in songs_to_download:
                if song is None:
                    print("Encountered a None URL in songs_to_download")
                    continue
                if retry:
                    task = asyncio.create_task(download_with_retry(song, guild_id))
                else:
                    task = asyncio.create_task(downloader.download_song(song, guild_id))
                tasks.append(task)

            for task in tasks:
                downloaded_audio = await task
                if downloaded_audio:
                    await audio_queue.add_to_queue(guild_id, {"file": downloaded_audio, "url": song})

    async def play_audio(voice_client, guild_id, interaction, process_task):
        while True:
            track_info = await audio_queue.next_track(guild_id)
            if not track_info:
                if process_task.done() and await audio_queue.is_queue_empty(guild_id):
                    break
                await asyncio.sleep(1)  # Wait a bit before checking the queue again
                continue

            track = track_info["file"]
            track_url = track_info["url"]
            print(f"Now playing: {track_url}")
            voice_client.play(FFmpegPCMAudio(executable="ffmpeg", source=track))
            await interaction.channel.send(f"Now playing: {track_url}")
            while voice_client.is_playing():
                await asyncio.sleep(1)
            remove_file_if_exists(track)
        
        await voice_client.disconnect()

    async def download_with_retry(url: str, guild_id: int, max_retries=3):
        for attempt in range(max_retries):
            try:
                return await downloader.download_song(url, guild_id)
            except (VideoUnavailable, PytubeError, KeyError) as e:
                print(f"Error occurred: {e}")
                if 'streamingData' in str(e):
                    print("YouTube streaming data extraction failed.")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
            except Exception as e:
                print(f"An error occurred in download_with_retry: {e}")
                raise

    def remove_file_if_exists(file_path: str):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"File removed: {file_path}")
        except Exception as e:
            print(f"Failed to remove file {file_path}: {e}")