import re
import os
import discord
import logging
from discord.ext import commands
from discord import app_commands, FFmpegPCMAudio
import asyncio
import requests
from config.config import ELEVEN_LABS_API_KEY, SERVERS

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class SayLines(commands.Cog, name="say_lines"):
    def __init__(self, bot):
        self.bot = bot
        logger.info("SayLines cog initialized.")

    @app_commands.command(name="say_lines", description="Says the lines in the voice channel.")
    @app_commands.guilds(*SERVERS)
    async def speak(self, interaction: discord.Interaction, user_input: str):
        logger.info("Received speak command from %s", interaction.user)
        await interaction.response.defer()

        if not await self._check_user_in_voice_channel(interaction):
            logger.warning("User %s not in a voice channel.", interaction.user)
            return

        if not await self._check_bot_not_speaking(interaction):
            logger.warning("Bot is already speaking in guild %s", interaction.guild.id)
            return

        speaker_voices = self._get_speaker_voices()
        matches = self._parse_user_input(user_input)

        if not matches:
            logger.error("Invalid input format: %s", user_input)
            await interaction.followup.send("Invalid input format. Please use the format: [speaker] text.")
            return

        audio_files = await self._generate_audio_files(interaction, matches, speaker_voices)
        if not audio_files:
            logger.error("Audio file generation failed.")
            return

        concatenated_file = await self._concatenate_audio_files(interaction, audio_files)
        logger.info("Playing audio file: %s", concatenated_file)
        await self._play_audio(interaction, concatenated_file)

    async def _check_user_in_voice_channel(self, interaction):
        if interaction.user.voice is None or interaction.user.voice.channel is None:
            logger.warning("User %s is not in a voice channel.", interaction.user)
            await interaction.followup.send(
                "You are not in a voice channel. Please use the `askbread` command if you just want text responses."
            )
            return False
        return True

    async def _check_bot_not_speaking(self, interaction):
        if interaction.guild.voice_client is not None and interaction.guild.voice_client.is_playing():
            logger.warning("Bot is already speaking in guild %s", interaction.guild.id)
            await interaction.followup.send("I'm currently speaking. Please try again later.")
            return False
        return True

    def _get_speaker_voices(self):
        voices = {
            "bread": "saUfe5jyFdcsZbN5Yt1c",
            "jp": "uERblY4ce8BC2FzPBGxR",
            "obama": "XbDmFt8IDl7dQjpNVO1f",
            "chris": "H8uduO2F47eLZMUNZvUf",
            "mangohawk": "ZuAcH52R3qZnDMjlvT1w",
            "cowboy": "KTPVrSVAEUSJRClDzBw7",
        }
        logger.info("Loaded speaker voices: %s", voices)
        return voices

    def _parse_user_input(self, user_input):
        pattern = r'\[(.*?)\]\s*([^\[]+)'
        matches = re.findall(pattern, user_input)
        logger.info("Parsed user input into: %s", matches)
        return matches

    async def _generate_audio_files(self, interaction, matches, speaker_voices):
        audio_files = []
        for idx, (speaker, text) in enumerate(matches):
            speaker = speaker.strip().lower()
            text = text.strip()
            if speaker not in speaker_voices:
                logger.error("Unknown speaker: %s", speaker)
                await interaction.followup.send(
                    f"Unknown speaker '{speaker}'. Available speakers are: {', '.join(speaker_voices.keys())}"
                )
                return None

            voice_id = speaker_voices[speaker]
            logger.info("Generating speech for speaker: %s, voice_id: %s", speaker, voice_id)
            file_path = await self._generate_speech(interaction, text, voice_id, idx)
            if file_path:
                audio_files.append(file_path)
                logger.info("Generated audio file: %s", file_path)
            else:
                logger.error("Failed to generate speech for speaker: %s", speaker)
                return None
        return audio_files

    async def _generate_speech(self, interaction, text, voice_id, idx):
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
        try:
            response = requests.post(url, json=data, headers=headers, timeout=10)
        except Exception as e:
            logger.exception("Error sending request to ElevenLabs API: %s", e)
            await interaction.followup.send(f"Error generating speech for speaker '{voice_id}'.")
            return None

        if response.status_code != 200:
            logger.error("ElevenLabs API error: %s (status code %s)", response.content, response.status_code)
            await interaction.followup.send(f"Error generating speech for speaker '{voice_id}'.")
            return None

        file_path = f'{interaction.guild.id}_temp_response_{idx}.mp3'
        try:
            with open(file_path, 'wb') as f:
                f.write(response.content)
            logger.info("Saved speech to file: %s", file_path)
        except Exception as e:
            logger.exception("Error writing file %s: %s", file_path, e)
            await interaction.followup.send(f"Error saving audio for speaker '{voice_id}'.")
            return None
        return file_path

    async def _concatenate_audio_files(self, interaction, audio_files):
        concatenated_file = f'{interaction.guild.id}_final_response.mp3'
        concat_list = f'{interaction.guild.id}_concat_list.txt'

        try:
            with open(concat_list, 'w', encoding='utf-8') as f:
                for file in audio_files:
                    f.write(f"file '{os.path.abspath(file)}'\n")
            logger.info("Created concat list file: %s", concat_list)
        except Exception as e:
            logger.exception("Error creating concat list file: %s", e)
            await interaction.followup.send("Error preparing audio files.")
            return None

        ffmpeg_command = f"ffmpeg -y -f concat -safe 0 -i {concat_list} -c copy {concatenated_file}"
        logger.info("Running ffmpeg command: %s", ffmpeg_command)
        os.system(ffmpeg_command)

        for file in audio_files:
            try:
                os.remove(file)
                logger.info("Removed temporary file: %s", file)
            except Exception as e:
                logger.exception("Error removing file %s: %s", file, e)
        try:
            os.remove(concat_list)
            logger.info("Removed concat list file: %s", concat_list)
        except Exception as e:
            logger.exception("Error removing concat list file %s: %s", concat_list, e)

        logger.info("Concatenated file created: %s", concatenated_file)
        return concatenated_file

    async def _play_audio(self, interaction, concatenated_file):
        voice_channel = interaction.user.voice.channel
        try:
            vc = await voice_channel.connect()
            logger.info("Connected to voice channel: %s", voice_channel)
        except discord.ClientException:
            vc = interaction.guild.voice_client
            logger.info("Using existing voice client in channel: %s", vc.channel)
        except discord.Forbidden:
            logger.error("Permission denied for voice channel: %s", voice_channel)
            await interaction.followup.send("I don't have permission to join your voice channel.")
            return

        try:
            audio_source = FFmpegPCMAudio(
                concatenated_file,
                executable='/app/.heroku/activestorage-preview/bin/ffmpeg',
                options='-vn -ar 48000 -ac 2 -f s16le'
            )
            if not vc.is_playing():
                vc.play(audio_source)
                logger.info("Started playing audio.")
                while vc.is_playing():
                    await asyncio.sleep(1)
                logger.info("Finished playing audio, disconnecting.")
                await vc.disconnect()
            else:
                logger.warning("Voice client is already playing audio.")
                await interaction.followup.send("I'm currently speaking. Please wait until I'm finished.")
                await vc.disconnect()
        except Exception as e:
            logger.exception("Error during audio playback: %s", e)
            await interaction.followup.send(f"🗣️ **Error occurred:** \"{e}\"")
            await vc.disconnect()
        finally:
            if os.path.exists(concatenated_file):
                try:
                    os.remove(concatenated_file)
                    logger.info("Removed concatenated file: %s", concatenated_file)
                except Exception as e:
                    logger.exception("Error removing concatenated file %s: %s", concatenated_file, e)

async def setup(bot):
    await bot.add_cog(SayLines(bot))
