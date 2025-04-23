import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import tempfile
import os
import logging
import browser_cookie3
import http.cookiejar
from config.config import SERVERS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
DEFAULT_COOKIES_PATH = os.getenv('YTDL_COOKIE_FILE') or os.path.join(tempfile.gettempdir(), 'yt_cookies.txt')

class YTDLCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cookies_path = DEFAULT_COOKIES_PATH

    def regenerate_cookies(self):
        """
        Extract YouTube cookies from the browser and save to cookies_path.
        """
        logger.info("Regenerating YouTube cookies into %s", self.cookies_path)
        # Load cookies from browser for youtube.com
        cj = browser_cookie3.chrome(domain_name='youtube.com')
        mozilla_jar = http.cookiejar.MozillaCookieJar(self.cookies_path)
        for c in cj:
            mozilla_jar.set_cookie(c)
        mozilla_jar.save(ignore_discard=True, ignore_expires=True)
        logger.info("Saved regenerated cookies to %s", self.cookies_path)
        return self.cookies_path

    async def _download_and_send(self, send_func, mention: str, url: str):
        """
        Internal helper to download YouTube audio as MP3, auto-regenerating cookies if auth error.
        send_func should accept keyword args content and file.
        """
        logger.info("Starting download for URL: %s", url)
        temp_dir = tempfile.gettempdir()
        # Base yt-dlp options
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
        # Try download, regenerate cookies on auth failure
        attempt = 0
        last_error = None
        while attempt < 2:
            attempt += 1
            opts = base_opts.copy()
            # include cookies if available
            if os.path.exists(self.cookies_path):
                opts['cookiefile'] = self.cookies_path
                logger.info("Using cookies file at %s", self.cookies_path)
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                file_path = os.path.join(temp_dir, f"{info['id']}.mp3")
                logger.info("Downloaded and converted: %s", file_path)
                # Send MP3
                with open(file_path, 'rb') as f:
                    await send_func(content=mention, file=discord.File(f, filename=f"{info['title']}.mp3"))
                logger.info("Sent MP3 to user: %s", mention)
                # Cleanup
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info("Removed temporary file: %s", file_path)
                return
            except Exception as e:
                last_error = e
                err_str = str(e)
                logger.error("Download attempt %d failed: %s", attempt, err_str)
                # If first failure due to auth, regenerate cookies and retry
                if attempt == 1 and 'Sign in to confirm' in err_str:
                    try:
                        self.regenerate_cookies()
                        continue
                    except Exception as regen_err:
                        logger.error("Cookie regeneration failed: %s", regen_err)
                        break
                # otherwise break and report
                break
        # If we reach here, all attempts failed
        logger.error("All download attempts failed: %s", last_error, exc_info=True)
        await send_func(content=f"{mention} Failed to download audio after retries: {last_error}")

    @commands.command(name="ytmp3", help="Download YouTube audio as MP3")
    async def ytmp3(self, ctx: commands.Context, url: str):
        """Prefix command to download YouTube audio as MP3."""
        await ctx.trigger_typing()
        await self._download_and_send(
            send_func=ctx.send,
            mention=ctx.author.mention,
            url=url
        )

    @app_commands.command(name="ytmp3", description="Download YouTube audio as MP3")
    @app_commands.guilds(*SERVERS)
    @app_commands.describe(url="YouTube video or music URL to download audio from")
    async def ytmp3_slash(self, interaction: discord.Interaction, url: str):
        """Slash command to download YouTube audio as MP3."""
        logger.info("Slash command invoked by %s: %s", interaction.user, url)
        await interaction.response.defer()
        await self._download_and_send(
            send_func=interaction.followup.send,
            mention=interaction.user.mention,
            url=url
        )

async def setup(bot: commands.Bot):
    """Set up the YTDLCog."""
    await bot.add_cog(YTDLCog(bot))
