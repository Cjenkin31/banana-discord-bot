import discord
from discord.ext import commands
from discord import app_commands
from youtube_transcript_api import YouTubeTranscriptApi
from utils.gpt import generate_gpt_response

async def download_transcript(self, video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = ' '.join([item['text'] for item in transcript])
        return transcript_text
    except Exception as e:
        return str(e)
async def define_summarize_youtube_video_command(tree):
    @tree.command(name="summarize_youtube", description="Summarizes a YouTube video based on its transcript.")
    async def summarize_youtube(self, interaction: discord.Interaction, youtube_url: str):
        await interaction.response.defer()

        video_id = youtube_url.split('v=')[1].split('&')[0]

        transcript = await self.download_transcript(video_id)
        if len(transcript) > 1024:
            transcript = transcript[:1024] + '...'

        role = "youtube"
        response_message = await generate_gpt_response("gpt-3.5-turbo", role, transcript)

        # Send the response to the user.
        await interaction.followup.send(response_message)