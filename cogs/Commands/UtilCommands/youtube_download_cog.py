import discord
from discord.ext import commands
from discord import app_commands
from config.config import SERVERS
import yt_dlp
import tempfile
import os
import logging

# Configure logging for this cog
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YTDLCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _download_and_send(self, send_func, mention, url: str):
        """
        Internal helper to download YouTube audio as MP3 and send via the provided send_func.
        """
        logger.info("Starting download for URL: %s", url)
        temp_dir = tempfile.gettempdir()
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(temp_dir, '%(id)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
            file_path = os.path.join(temp_dir, f"{info['id']}.mp3")
            logger.info("Downloaded and converted: %s", file_path)
            with open(file_path, 'rb') as f:
                await send_func(file=discord.File(f, filename=f"{info['title']}.mp3"))
            logger.info("Sent MP3 to user: %s", mention)
        except Exception as e:
            logger.error("Error during download/send: %s", e, exc_info=True)
            await send_func(content=f"{mention} Failed to download audio: {e}")
        finally:
            # Cleanup temporary file
            try:
                if 'file_path' in locals() and os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info("Removed temporary file: %s", file_path)
            except Exception as cleanup_err:
                logger.warning("Failed to remove temp file: %s", cleanup_err)

    @commands.command(name="ytmp3", help="Download YouTube audio as MP3")
    async def ytmp3(self, ctx: commands.Context, url: str):
        """Prefix command to download YouTube audio as MP3."""
        await ctx.trigger_typing()
        await self._download_and_send(
            send_func=lambda **kwargs: ctx.send(ctx.author.mention, **kwargs),
            mention=ctx.author.mention,
            url=url
        )
    @app_commands.guilds(*SERVERS)
    @app_commands.command(name="ytmp3", description="Download YouTube audio as MP3")
    @app_commands.describe(url="YouTube video or music URL to download audio from")
    async def ytmp3_slash(self, interaction: discord.Interaction, url: str):
        """Slash command to download YouTube audio as MP3."""
        logger.info("Slash command invoked by %s: %s", interaction.user, url)
        await interaction.response.defer()
        # Use followup for sending after defer
        await self._download_and_send(
            send_func=lambda **kwargs: interaction.followup.send(content=interaction.user.mention, **kwargs),
            mention=interaction.user.mention,
            url=url
        )

async def setup(bot: commands.Bot):
    """Set up the YTDLCog."""
    await bot.add_cog(YTDLCog(bot))
