import re
import os
import discord
from discord.ext import commands
from discord import app_commands, FFmpegPCMAudio
import asyncio
import requests
from config.config import ELEVEN_LABS_API_KEY, SERVERS

class SayLines(commands.Cog, name="say_lines"):
    def __init__(self, bot):
        self.bot = bot
        print("SayLines cog initialized.")

    @app_commands.command(name="say_lines", description="Says the lines in the voice channel.")
    @app_commands.guilds(*SERVERS)
    async def speak(self, interaction: discord.Interaction, user_input: str):
        await interaction.response.defer()
        print(f"Received speak command from {interaction.user}")

        if not await self._check_user_in_voice_channel(interaction):
            print(f"User {interaction.user} is not in a voice channel.")
            return

        if not await self._check_bot_not_speaking(interaction):
            print(f"Bot is already speaking in guild {interaction.guild.id}")
            return

        speaker_voices = self._get_speaker_voices()
        matches = self._parse_user_input(user_input)

        if not matches:
            print("Invalid input format:", user_input)
            await interaction.followup.send("Invalid input format. Please use the format: [speaker] text.")
            return

        audio_files = await self._generate_audio_files(interaction, matches, speaker_voices)
        if not audio_files:
            print("Audio file generation failed.")
            return

        concatenated_file = await self._concatenate_audio_files(interaction, audio_files)
        print("Playing audio file:", concatenated_file)
        await self._play_audio(interaction, concatenated_file)

    async def _check_user_in_voice_channel(self, interaction):
        if interaction.user.voice is None or interaction.user.voice.channel is None:
            print(f"User {interaction.user} is not connected to any voice channel.")
            await interaction.followup.send(
                "You are not in a voice channel. Please use the `askbread` command if you just want text responses."
            )
            return False
        return True

    async def _check_bot_not_speaking(self, interaction):
        if interaction.guild.voice_client is not None and interaction.guild.voice_client.is_playing():
            print(f"Bot is already speaking in guild {interaction.guild.id}")
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
        print("Loaded speaker voices:", voices)
        return voices

    def _parse_user_input(self, user_input):
        pattern = r'\[(.*?)\]\s*([^\[]+)'
        matches = re.findall(pattern, user_input)
        print("Parsed user input into:", matches)
        return matches

    async def _generate_audio_files(self, interaction, matches, speaker_voices):
        audio_files = []
        for idx, (speaker, text) in enumerate(matches):
            speaker = speaker.strip().lower()
            text = text.strip()
            if speaker not in speaker_voices:
                print("Unknown speaker:", speaker)
                await interaction.followup.send(
                    f"Unknown speaker '{speaker}'. Available speakers are: {', '.join(speaker_voices.keys())}"
                )
                return None

            voice_id = speaker_voices[speaker]
            print(f"Generating speech for speaker: {speaker}, voice_id: {voice_id}")
            file_path = await self._generate_speech(interaction, text, voice_id, idx)
            if file_path:
                audio_files.append(file_path)
                print("Generated audio file:", file_path)
            else:
                print("Failed to generate speech for speaker:", speaker)
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
            print("Error sending request to ElevenLabs API:", e)
            await interaction.followup.send(f"Error generating speech for speaker '{voice_id}'.")
            return None

        if response.status_code != 200:
            print("ElevenLabs API error:", response.content, "Status code:", response.status_code)
            await interaction.followup.send(f"Error generating speech for speaker '{voice_id}'.")
            return None

        file_path = f'{interaction.guild.id}_temp_response_{idx}.mp3'
        try:
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print("Saved speech to file:", file_path)
        except Exception as e:
            print(f"Error writing file {file_path}:", e)
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
            print("Created concat list file:", concat_list)
        except Exception as e:
            print("Error creating concat list file:", e)
            await interaction.followup.send("Error preparing audio files.")
            return None

        ffmpeg_command = f"ffmpeg -y -f concat -safe 0 -i {concat_list} -c copy {concatenated_file}"
        print("Running ffmpeg command:", ffmpeg_command)
        os.system(ffmpeg_command)

        for file in audio_files:
            try:
                os.remove(file)
                print("Removed temporary file:", file)
            except Exception as e:
                print(f"Error removing file {file}:", e)
        try:
            os.remove(concat_list)
            print("Removed concat list file:", concat_list)
        except Exception as e:
            print(f"Error removing concat list file {concat_list}:", e)

        print("Concatenated file created: ", concatenated_file)
        return concatenated_file

    async def _play_audio(self, interaction, concatenated_file):
        voice_channel = interaction.user.voice.channel
        try:
            vc = await voice_channel.connect()
            print("Connected to voice channel:", voice_channel)
        except discord.ClientException:
            vc = interaction.guild.voice_client
            print("Using existing voice client in channel:", vc.channel)
        except discord.Forbidden:
            print("Permission denied for voice channel:", voice_channel)
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
                print("Started playing audio.")
                while vc.is_playing():
                    await asyncio.sleep(1)
                print("Finished playing audio, disconnecting.")
                await interaction.followup.send("Finished speaking.")
                await vc.disconnect()
            else:
                print("Voice client is already playing audio.")
                await interaction.followup.send("I'm currently speaking. Please wait until I'm finished.")
                await vc.disconnect()
        except Exception as e:
            print("Error during audio playback:", e)
            await interaction.followup.send(f"🗣️ **Error occurred:** \"{e}\"")
            await vc.disconnect()
        finally:
            if os.path.exists(concatenated_file):
                try:
                    os.remove(concatenated_file)
                    print("Removed concatenated file:", concatenated_file)
                except Exception as e:
                    print(f"Error removing concatenated file {concatenated_file}:", e)

async def setup(bot):
    await bot.add_cog(SayLines(bot))
