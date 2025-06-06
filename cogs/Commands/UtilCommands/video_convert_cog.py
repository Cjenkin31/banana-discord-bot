import os
import uuid
import asyncio
import discord
from discord.ext import commands

class VideoConvertCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.temp_dir = "temp_videos"
        os.makedirs(self.temp_dir, exist_ok=True)
        # Limit concurrent conversions to avoid memory spikes
        self._semaphore = asyncio.Semaphore(1)
        # Cleanup any leftover files on startup
        for f in os.listdir(self.temp_dir):
            try:
                os.remove(os.path.join(self.temp_dir, f))
            except OSError:
                pass

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.attachments:
            return
        for attachment in message.attachments:
            if attachment.filename.lower().endswith(".mkv"):
                # Ensure only one conversion at a time
                asyncio.create_task(self._handle_conversion(attachment, message))

    async def _handle_conversion(self, attachment: discord.Attachment, message: discord.Message):
        async with self._semaphore:
            await self.convert_and_send(attachment, message)

    def _get_upload_limit(self, guild: discord.Guild) -> int:
        tier = getattr(guild, 'premium_tier', 0)
        if tier >= 3:
            return 100 * 1024 * 1024
        if tier == 2:
            return 50 * 1024 * 1024
        return 8 * 1024 * 1024

    async def _get_duration(self, path: str) -> float:
        proc = await asyncio.create_subprocess_exec(
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", path,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL
        )
        out, _ = await proc.communicate()
        try:
            return float(out)
        except:
            return 0.0

    async def convert_and_send(self, attachment: discord.Attachment, message: discord.Message):
        channel = message.channel
        uid = uuid.uuid4().hex
        paths = {
            "input": os.path.join(self.temp_dir, f"{uid}.mkv"),
            "mp4": os.path.join(self.temp_dir, f"{uid}.mp4"),
            "compressed": os.path.join(self.temp_dir, f"{uid}_c.mp4"),
            "trimmed": os.path.join(self.temp_dir, f"{uid}_t.mp4"),
        }
        # Download
        await attachment.save(paths["input"])

        # 1: Container conversion
        await asyncio.create_subprocess_exec(
            "ffmpeg", "-i", paths["input"], "-c", "copy", paths["mp4"],
            stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL
        ).wait()

        try:
            if not os.path.exists(paths["mp4"]):
                await channel.send("❌ Conversion failed: output not found.")
                return
            limit = self._get_upload_limit(channel.guild)
            size = os.path.getsize(paths["mp4"])
            if size <= limit:
                await channel.send(file=discord.File(paths["mp4"]))
                return
            # 2: Compress
            await channel.send("🔄 File too large, compressing...")
            await asyncio.create_subprocess_exec(
                "ffmpeg", "-i", paths["mp4"],
                "-c:v", "libx264", "-preset", "fast", "-crf", "28",
                "-c:a", "aac", "-b:a", "128k", paths["compressed"],
                stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL
            ).wait()
            if not os.path.exists(paths["compressed"]):
                await channel.send("❌ Compression failed: output not found.")
                return
            if os.path.getsize(paths["compressed"]) <= limit:
                await channel.send(f"✅ Compressed video fits limit.")
                try:
                    await channel.send(file=discord.File(paths["compressed"]))
                except discord.HTTPException as e:
                    await channel.send(f"❌ Send failed: {e}")
                return
            # 3: Trim
            await channel.send("✂️ Still too large, trimming start...")
            dur = await self._get_duration(paths["compressed"])
            keep_ratio = limit / os.path.getsize(paths["compressed"])
            keep_sec = dur * keep_ratio
            start = max(0, dur - keep_sec)
            await asyncio.create_subprocess_exec(
                "ffmpeg", "-ss", str(start), "-i", paths["compressed"],
                "-c", "copy", paths["trimmed"],
                stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL
            ).wait()
            if os.path.exists(paths["trimmed"]) and os.path.getsize(paths["trimmed"]) <= limit:
                await channel.send(file=discord.File(paths["trimmed"]))
            else:
                await channel.send("⚠️ Trimmed output still exceeds the upload limit.")
        except Exception as e:
            await channel.send(f"❌ Error during processing: {e}")
        finally:
            # Remove all temp files
            for p in paths.values():
                try:
                    os.remove(p)
                except OSError:
                    pass

async def setup(bot: commands.Bot):
    await bot.add_cog(VideoConvertCog(bot))
