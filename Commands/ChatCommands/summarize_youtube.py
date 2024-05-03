import discord
from discord.ext import commands
from discord import app_commands
from youtube_transcript_api import YouTubeTranscriptApi
from GPT_stories import getStoryByRole
from utils.gpt import generate_gpt_response

async def download_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(['en'])

        if not transcript.is_generated:
            transcript = transcript_list.find_generated_transcript(['en'])

        transcript_fetch = transcript.fetch()
        transcript_text = ' '.join([item['text'] for item in transcript_fetch])
        return transcript_text
    except Exception as e:
        print(e)
        return f"Failed to download transcript: {e}"

async def define_summarize_youtube_video_command(tree, servers):
    @tree.command(name="summarize_youtube", description="Summarizes a YouTube video based on its transcript.", guilds=servers)
    async def summarize_youtube(interaction: discord.Interaction, youtube_url: str):
        await interaction.response.defer()

        video_id = ''
        if 'youtube.com/watch?v=' in youtube_url:
            video_id = youtube_url.split('v=')[1].split('&')[0]
        elif 'youtu.be/' in youtube_url:
            video_id = youtube_url.split('youtu.be/')[1].split('?')[0]

        if not video_id:
            await interaction.followup.send("Invalid YouTube URL provided.")
            return

        transcript = await download_transcript(video_id)
        if transcript.startswith("Failed"):
            await interaction.followup.send("Failed to download video. Please try a different video.")
            return

        if len(transcript) > 2048:
            transcript = transcript[:2048] + '...'

        role_story = getStoryByRole("youtube", interaction.user.id)
        response_message = await generate_gpt_response("gpt-3.5-turbo", role_story, transcript)

        await interaction.followup.send(response_message)