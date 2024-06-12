import discord
from discord.ext import commands
from discord import app_commands
from youtube_transcript_api import YouTubeTranscriptApi
from GPT_stories import getStoryByRole
from utils.gpt import generate_gpt_response
from utils.message_utils import send_message_in_chunks

MAX_TOKENS = 4096
CHUNK_SIZE = 2000

class SummarizeYouTubeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def download_transcript(self, video_id):
        try:
            print(video_id)
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            try:
                transcript = transcript_list.find_transcript(['en'])
            except:
                transcript = transcript_list.find_generated_transcript(['en'])
            print("Fetching Transcript...")
            transcript_fetch = transcript.fetch()
            print("Fetched!")
            transcript_text = ' '.join([item['text'] for item in transcript_fetch])
            return transcript_text
        except Exception as e:
            return f"Failed to download transcript: {e}"

    async def split_and_summarize(self, transcript, role_story):
        chunks = [transcript[i:i+CHUNK_SIZE] for i in range(0, len(transcript), CHUNK_SIZE)]
        summaries = []
        for chunk in chunks:
            response_message = await generate_gpt_response("gpt-3.5-turbo", role_story, chunk)
            summaries.append(response_message)
        final_summary = "\n".join(summaries)
        return final_summary

    @app_commands.command(name="summarize_youtube", description="Summarizes a YouTube video based on its transcript.")
    async def summarize_youtube(self, interaction: discord.Interaction, youtube_url: str):
        await interaction.response.defer()

        video_id = ''
        if 'youtube.com/watch?v=' in youtube_url:
            video_id = youtube_url.split('v=')[1].split('&')[0]
        elif 'youtu.be/' in youtube_url:
            video_id = youtube_url.split('youtu.be/')[1].split('?')[0]

        if not video_id:
            await interaction.followup.send("Invalid YouTube URL provided.")
            return

        transcript = await self.download_transcript(video_id)
        if transcript.startswith("Failed"):
            await interaction.followup.send("Failed to download video. Please try a different video.")
            return

        role_story = getStoryByRole("youtube", interaction.user.id)
        final_summary = await self.split_and_summarize(transcript, role_story)

        await send_message_in_chunks(final_summary, interaction)

def setup(bot):
    bot.add_cog(SummarizeYouTubeCog(bot))
