import os
import uuid
from moviepy.editor import AudioFileClip
from pytube import YouTube, Playlist
from pytube.exceptions import VideoUnavailable, PytubeError
MAX_DOWNLOAD_SONGS_AT_A_TIME = 2
class Downloader:
    def __init__(self, guild_id):
        self.guild_id = guild_id

    async def download_song(self, url: str) -> str:
        try:
            yt = YouTube(url)
            stream = yt.streams.filter(only_audio=True).first()
            if not stream:
                return None

            unique_id = uuid.uuid4()
            output_path = stream.download(filename=f'{self.guild_id}_downloaded_audio_{unique_id}.mp4')
            return self._convert_to_mp3(output_path)
        except VideoUnavailable:
            raise RuntimeError("The video is unavailable.")
        except PytubeError as e:
            raise RuntimeError(f"PyTube error: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error: {e}")

    def _convert_to_mp3(self, path: str) -> str:
        audio_clip = AudioFileClip(path)
        mp3_path = path.replace('.mp4', '.mp3')
        audio_clip.write_audiofile(mp3_path)
        audio_clip.close()
        os.remove(path)
        return mp3_path

def remove_file_if_exists(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)
