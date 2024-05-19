import discord
from discord.ext import commands
from discord import app_commands
from youtube_transcript_api import YouTubeTranscriptApi
from GPT_stories import getStoryByRole
from utils.gpt import generate_gpt_response
from utils.message_utils import send_message_in_chunks

MAX_TOKENS = 4096
CHUNK_SIZE = 2000

async def download_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        try:
            transcript = transcript_list.find_transcript(['en'])
        except:
            transcript = transcript_list.find_generated_transcript(['en'])
        transcript_fetch = transcript.fetch()
        transcript_text = ' '.join([item['text'] for item in transcript_fetch])
        return transcript_text
    except Exception as e:
        return f"Failed to download transcript: {e}"

async def split_and_summarize(transcript, role_story):
    chunks = [transcript[i:i+CHUNK_SIZE] for i in range(0, len(transcript), CHUNK_SIZE)]
    summaries = []
    for chunk in chunks:
        response_message = await generate_gpt_response("gpt-3.5-turbo", role_story, chunk)
        summaries.append(response_message)
    final_summary = "\n".join(summaries)
    return final_summary

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

        role_story = getStoryByRole("youtube", interaction.user.id)
        final_summary = await split_and_summarize(transcript, role_story)
        
        await send_message_in_chunks(final_summary, interaction)