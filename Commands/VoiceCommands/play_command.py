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
from typing import List

# TODO: Support for playlists
# TODO: New command for playing audio from links. Soundcloud, Spotify, etc.

audio_queue = AudioQueue()
MAX_DOWNLOAD_SONGS_AT_A_TIME = 3  # Define the maximum number of simultaneous downloads

class Downloader:
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
        print("Received play_youtube_audio command")
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.followup.send("You need to be in a voice channel to play audio.")
            print("User not in voice channel")
            return
        try:
            if 'youtube.com/playlist?list=' in url or 'youtube.com/watch?v=' in url or 'youtu.be/' in url:
                print(f"Processing YouTube URL: {url}")
                voice_channel = interaction.user.voice.channel
                print(f"User is in voice channel: {voice_channel.name}")
                voice_client = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild)
                print(f"Voice client: {voice_client}")
                if voice_client is None:
                    try:
                        voice_client = await voice_channel.connect()
                        print(f"Joined voice channel: {voice_channel.name}")
                    except Exception as e:
                        await interaction.followup.send(f"Failed to join voice channel: {str(e)}")
                        return

                # Start processing the URL and playing audio concurrently
                print("Starting process_task")
                process_task = asyncio.create_task(process_url(url, guild_id))
                print("Starting play_task")
                play_task = asyncio.create_task(play_audio(voice_client, guild_id, interaction, process_task))
                print("Waiting for process_task and play_task to complete")
                await asyncio.gather(process_task, play_task)
            else:
                await interaction.followup.send("Invalid YouTube URL provided.")
                return

        except Exception as e:
            print(f"An error occurred in main play_youtube_audio: {str(e)}")
            await interaction.followup.send("Something went wrong! Please try again later.")
    async def process_url(url, guild_id):
        try:
            if 'playlist?list=' in url:
                playlist = Playlist(url)
                if playlist is None:
                    print("Playlist is None")
                    return
                songs = list(playlist.video_urls)  # Convert DeferredGeneratorList to a regular list
                if songs is None:
                    print("Playlist video_urls is None")
                    return
                else:
                    print(f"Playlist contains {len(songs)} videos")
                await download_songs_in_lots(songs, guild_id, retry=False)
            else:
                await download_songs_in_lots([url], guild_id, retry=True)
        except Exception as e:
            print(f"An error occurred in process_url: {e}")

    async def download_songs_in_lots(songs: List[str], guild_id: int, retry: bool):
        try:
            while songs:
                print(f"Starting loop with {len(songs)} songs...")
                
                # Check if songs is a list and contains valid elements
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

                if songs is None:
                    print("Songs became None after slicing. Exiting loop.")
                    break

                print(f"Remaining songs: {len(songs)}")

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
                    try:
                        downloaded_audio = await task
                        if downloaded_audio:
                            await audio_queue.add_to_queue(guild_id, {"file": downloaded_audio, "url": song})
                    except Exception as e:
                        print(f"An error occurred while downloading a song: {e}")

        except Exception as e:
            print(f"An error occurred in download_songs_in_lots: {e}")

async def play_audio(voice_client, guild_id, interaction, process_task):
    try:
        while True:
            try:
                track_info = await audio_queue.next_track(guild_id)
                if track_info is None:
                    queue_empty = await audio_queue.is_queue_empty(guild_id)
                    print(f"Queue empty: {queue_empty}")
                    if process_task.done() and queue_empty:
                        print("Process completed and queue is empty, disconnecting...")
                        break
                    await asyncio.sleep(1)  # Wait a bit before checking the queue again
                    continue

                if voice_client and voice_client.is_connected():
                    track = track_info["file"]
                    track_url = track_info["url"]
                    print(f"Now playing: {track_url}, track file: {track}")
                    voice_client.play(FFmpegPCMAudio(executable="ffmpeg", source=track))
                    await interaction.channel.send(f"Now playing: {track_url}")

                    while voice_client.is_playing():
                        await asyncio.sleep(1)
                    
                    remove_file_if_exists(track)
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