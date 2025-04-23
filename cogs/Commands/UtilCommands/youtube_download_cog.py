import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import tempfile
import os
import logging
import base64
from config.config import SERVERS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
DEFAULT_COOKIES_PATH = os.getenv('YTDL_COOKIE_FILE') or os.path.join(tempfile.gettempdir(), 'yt_cookies.txt')
COOKIES_B64 = os.getenv('YTDL_COOKIES_B64')

class YTDLCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cookies_path = DEFAULT_COOKIES_PATH
        if COOKIES_B64:
            try:
                decoded = base64.b64decode(COOKIES_B64)
                with open(self.cookies_path, 'wb') as f:
                    f.write(decoded)
                logger.info("Loaded YouTube cookies from env var into %s", self.cookies_path)
            except Exception as e:
                logger.error("Failed to decode/load YTDL_COOKIES_B64: %s", e)

    async def _download_and_send(self, send_func, mention: str, url: str):
        """
        Download YouTube audio as MP3, retrying once on auth failure.
        send_func should accept keyword args content and file.
        """
        logger.info("Starting download for URL: %s", url)
        temp_dir = tempfile.gettempdir()
        base_opts = {
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
        attempt = 0
        last_error = None
        while attempt < 2:
            attempt += 1
            opts = base_opts.copy()
            if os.path.exists(self.cookies_path):
                opts['cookiefile'] = self.cookies_path
                logger.info("Using cookies file at %s", self.cookies_path)
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                file_path = os.path.join(temp_dir, f"{info['id']}.mp3")
                logger.info("Downloaded and converted: %s", file_path)
                with open(file_path, 'rb') as f:
                    await send_func(content=mention, file=discord.File(f, filename=f"{info['title']}.mp3"))
                if os.path.exists(file_path):
                    os.remove(file_path)
                return
            except Exception as e:
                last_error = e
                err_str = str(e)
                logger.error("Download attempt %d failed: %s", attempt, err_str)
                if attempt == 1 and 'Sign in to confirm' in err_str:
                    logger.info("Auth error detected; retrying with existing cookies...")
                    continue
                break
        logger.error("All download attempts failed: %s", last_error, exc_info=True)
        await send_func(content=f"{mention} Failed to download audio after retries: {last_error}")

    @commands.command(name="ytmp3", help="Download YouTube audio as MP3")
    async def ytmp3(self, ctx: commands.Context, url: str):
        """Prefix command to download YouTube audio as MP3."""
        await ctx.trigger_typing()
        await self._download_and_send(ctx.send, ctx.author.mention, url)

    @app_commands.command(name="ytmp3", description="Download YouTube audio as MP3")
    @app_commands.guilds(*SERVERS)
    @app_commands.describe(url="YouTube video or music URL to download audio from")
    async def ytmp3_slash(self, interaction: discord.Interaction, url: str):
        """Slash command to download YouTube audio as MP3."""
        logger.info("Slash command invoked by %s: %s", interaction.user, url)
        await interaction.response.defer()
        await self._download_and_send(interaction.followup.send, interaction.user.mention, url)

async def setup(bot: commands.Bot):
    """Set up the YTDLCog."""
    await bot.add_cog(YTDLCog(bot))
