from config.config import ELEVEN_LABS_API_KEY, SERVERS
import discord
from discord.ext import commands
from discord import app_commands
from discord import FFmpegPCMAudio
import asyncio
from GPT_stories import getStoryByRole
import requests
from utils.gpt import generate_gpt_response

class SpeakCommand(commands.Cog, name="speak"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="speak", description="Speaks the response in voice chat (may fail on Heroku). Text response always provided.")
    @app_commands.guilds(*SERVERS)
    async def speak(self, interaction: discord.Interaction, user_input: str, speaker: str = "bread", role: str = "bread"):
        await interaction.response.defer()
        if interaction.user.voice is None or interaction.user.voice.channel is None:
            await interaction.followup.send("You are not in a voice channel. Please use the `askbread` command if you just want text responses.")
            return
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
        voice_id = speaker_voices.get(speaker.lower(), speaker_voices["bread"])  # Default to "bread" if speaker is not found
        story = getStoryByRole(role, interaction.user.id)
        model = "gpt-3.5-turbo"
        response_message = await generate_gpt_response(model, story, user_input)

        await interaction.followup.send(f"🗣️ **Banana Bread says:** \"{response_message}\"")

        # ElevenLabs API request to get the MP3 file
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVEN_LABS_API_KEY
        }
        data = {
            "text": response_message,
            "model_id": "eleven_multilingual_v2",
            "voice_id": voice_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style_exaggeration": 0.0,
                "speaker_boost": True
            }
        }
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        response = requests.post(url, json=data, headers=headers, timeout=10)

        file_path = f'{interaction.guild.id}_temp_response.mp3'
        with open(file_path, 'wb') as f:
            f.write(response.content)
        if interaction.user.voice:
            voice_channel = interaction.user.voice.channel
            vc = None
            try:
                # Check if already connected to this channel
                if interaction.guild.voice_client and interaction.guild.voice_client.channel == voice_channel:
                    vc = interaction.guild.voice_client
                else:
                    # Disconnect from any existing connection first
                    if interaction.guild.voice_client:
                        await interaction.guild.voice_client.disconnect(force=True)

                    # Connect with timeout
                    vc = await voice_channel.connect(timeout=15.0)

            except discord.Forbidden:
                await interaction.followup.send("I don't have permission to join that voice channel.")
                return
            except discord.ClientException as e:
                await interaction.followup.send(f"Voice client error: {e}")
                return
            except asyncio.TimeoutError:
                await interaction.followup.send("⚠️ Voice connection timed out. This is a known issue on Heroku. The text response has been sent above.")
                return
            except Exception as e:
                await interaction.followup.send(f"⚠️ Voice connection failed: {e}. The text response has been sent above.")
                return

            try:
                # Verify connection before playing
                if not vc or not vc.is_connected():
                    await interaction.followup.send("⚠️ Voice connection not established. This is a known limitation on Heroku hosting. The text response has been sent above.")
                    return

                audio_source = FFmpegPCMAudio(file_path)
                if not vc.is_playing():
                    vc.play(audio_source, after=lambda e: print('Finished playing', e) if e else None)

                    # Wait for playback to complete with timeout
                    timeout_counter = 0
                    while vc.is_playing() and timeout_counter < 30:  # 30 second timeout
                        await asyncio.sleep(1)
                        timeout_counter += 1

                    if timeout_counter >= 30:
                        vc.stop()
                        await interaction.followup.send("Audio playback timed out.")

                    await vc.disconnect()
                else:
                    await interaction.followup.send("I'm currently speaking. Please wait until I'm finished.")
                    await vc.disconnect()
            except Exception as e:
                await interaction.followup.send(f"🗣️ **Audio playback error:** \"{e}\"")
                if vc and vc.is_connected():
                    await vc.disconnect()
            finally:
                # Clean up the temporary file
                try:
                    import os
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception:
                    pass
        else:
            await interaction.followup.send("You are not in a voice channel.")

async def setup(bot):
    await bot.add_cog(SpeakCommand(bot))