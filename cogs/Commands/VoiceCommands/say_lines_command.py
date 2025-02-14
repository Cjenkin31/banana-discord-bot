import re
import os
import discord
from discord.ext import commands
from discord import app_commands
from discord import FFmpegPCMAudio
import asyncio
import requests
from config.config import ELEVEN_LABS_API_KEY, SERVERS
from utils.gpt import generate_gpt_response

class SayLines(commands.Cog, name="say_lines"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="say_lines", description="Says the lines in the voice channel.")
    @app_commands.guilds(*SERVERS)
    async def speak(self, interaction: discord.Interaction, user_input: str):
        await interaction.response.defer()

        # Check if user is in a voice channel
        if interaction.user.voice is None or interaction.user.voice.channel is None:
            await interaction.followup.send(
                "You are not in a voice channel. Please use the `askbread` command if you just want text responses."
            )
            return

        # Check if the bot is already speaking
        if interaction.guild.voice_client is not None and interaction.guild.voice_client.is_playing():
            await interaction.followup.send("I'm currently speaking. Please try again later.")
            return

        speaker_voices = {
            "bread": "saUfe5jyFdcsZbN5Yt1c",
            "jp": "uERblY4ce8BC2FzPBGxR",
            "obama": "XbDmFt8IDl7dQjpNVO1f",
            "chris": "H8uduO2F47eLZMUNZvUf",
            "mangohawk": "ZuAcH52R3qZnDMjlvT1w",
            "cowboy": "KTPVrSVAEUSJRClDzBw7",
        }

        pattern = r'\[(.*?)\]\s*([^\[]+)'
        matches = re.findall(pattern, user_input)

        if not matches:
            await interaction.followup.send(
                "Invalid input format. Please use the format: [speaker] text."
            )
            return

        audio_files = []

        for idx, (speaker, text) in enumerate(matches):
            speaker = speaker.strip().lower()
            text = text.strip()
            if speaker not in speaker_voices:
                await interaction.followup.send(
                    f"Unknown speaker '{speaker}'. Available speakers are: {', '.join(speaker_voices.keys())}"
                )
                return

            voice_id = speaker_voices[speaker]

            # Prepare ElevenLabs API request
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": ELEVEN_LABS_API_KEY
            }
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style_exaggeration": 0.0,
                    "speaker_boost": True
                }
            }
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            response = requests.post(url, json=data, headers=headers)

            if response.status_code != 200:
                await interaction.followup.send(
                    f"Error generating speech for speaker '{speaker}'."
                )
                return

            file_path = f'{interaction.guild.id}_temp_response_{idx}.mp3'
            with open(file_path, 'wb') as f:
                f.write(response.content)
            audio_files.append(file_path)

        concatenated_file = f'{interaction.guild.id}_final_response.mp3'
        concat_list = f'{interaction.guild.id}_concat_list.txt'

        with open(concat_list, 'w') as f:
            for file in audio_files:
                f.write(f"file '{os.path.abspath(file)}'\n")

        # Run FFmpeg command to concatenate audio files
        ffmpeg_command = f"ffmpeg -y -f concat -safe 0 -i {concat_list} -c copy {concatenated_file}"
        os.system(ffmpeg_command)

        # Clean up individual audio files and list
        for file in audio_files:
            os.remove(file)
        os.remove(concat_list)

        # Play the concatenated audio
        voice_channel = interaction.user.voice.channel
        try:
            vc = await voice_channel.connect()
        except discord.ClientException:
            vc = interaction.guild.voice_client
        except discord.Forbidden:
            await interaction.followup.send("I don't have permission to join your voice channel.")
            return

        try:
            audio_source = FFmpegPCMAudio(concatenated_file)
            if not vc.is_playing():
                vc.play(audio_source)

                while vc.is_playing():
                    await asyncio.sleep(1)
                await vc.disconnect()
            else:
                await interaction.followup.send(
                    "I'm currently speaking. Please wait until I'm finished."
                )
                await vc.disconnect()
        except Exception as e:
            await interaction.followup.send(f"🗣️ **Error occurred:** \"{e}\"")
            await vc.disconnect()
        finally:
            # Remove the concatenated audio file
            if os.path.exists(concatenated_file):
                os.remove(concatenated_file)

async def setup(bot):
    await bot.add_cog(SayLines(bot))