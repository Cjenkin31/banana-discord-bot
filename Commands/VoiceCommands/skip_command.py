import discord
from discord.ext import commands
from discord import app_commands
import os
from utils.audio_queue import AudioQueue

audio_queue = AudioQueue()

async def define_skip_command(tree, servers):
    @tree.command(name="skip", description="Skips the current audio playback and starts the next one in the queue.", guilds=servers)
    async def skip(interaction: discord.Interaction):
        guild_id = interaction.guild_id
        voice_client = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild)

        if voice_client and voice_client.is_connected():
            if voice_client.is_playing():
                voice_client.stop()
                next_audio = audio_queue.get_next_audio(guild_id)
                if next_audio:
                    voice_client.play(next_audio)
                    await interaction.response.send_message("Skipped to the next audio in the queue.")
                else:
                    await interaction.response.send_message("No more audios in the queue.")
            else:
                await interaction.response.send_message("No audio is currently playing.")
        else:
            await interaction.response.send_message("The bot is not connected to any voice channel.")