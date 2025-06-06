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
        self._semaphore = asyncio.Semaphore(1)
        # Cleanup leftover files
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
                asyncio.create_task(self._handle_conversion(attachment, message))

    async def _handle_conversion(self, attachment: discord.Attachment, message: discord.Message):
        # Limit concurrent conversions
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
        except ValueError:
            return 0.0

    async def convert_and_send(self, attachment: discord.Attachment, message: discord.Message):
        channel = message.channel
        uid = uuid.uuid4().hex
        paths = {
            'input': os.path.join(self.temp_dir, f"{uid}.mkv"),
            'mp4': os.path.join(self.temp_dir, f"{uid}_mp4.mp4"),
            'comp': os.path.join(self.temp_dir, f"{uid}_comp.mp4"),
            'seg_pattern': os.path.join(self.temp_dir, f"{uid}_seg%03d.mp4"),
        }
        await attachment.save(paths['input'])

        # FFmpeg common args to limit memory usage via single thread
        ff_args = ["-threads", "1", "-nostdin"]

        # 1) Change container
        proc1 = await asyncio.create_subprocess_exec(
            "ffmpeg", *ff_args,
            "-i", paths['input'], "-c", "copy", paths['mp4'],
            stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL
        )
        await proc1.wait()

        limit = self._get_upload_limit(channel.guild)
        if not os.path.exists(paths['mp4']):
            await channel.send("❌ Conversion failed.")
        elif os.path.getsize(paths['mp4']) <= limit:
            await channel.send(file=discord.File(paths['mp4']))
        else:
            # 2) Compress
            await channel.send("🔄 Too large, compressing...")
            proc2 = await asyncio.create_subprocess_exec(
                "ffmpeg", *ff_args,
                "-i", paths['mp4'],
                "-c:v", "libx264", "-preset", "fast", "-crf", "28",
                "-c:a", "aac", "-b:a", "128k", paths['comp'],
                stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL
            )
            await proc2.wait()
            if not os.path.exists(paths['comp']):
                await channel.send("❌ Compression failed.")
            elif os.path.getsize(paths['comp']) <= limit:
                await channel.send("✅ Compressed fits limit.")
                await channel.send(file=discord.File(paths['comp']))
            else:
                # 3) Split segments
                await channel.send("✂️ Still too large; splitting into segments...")
                dur = await self._get_duration(paths['comp'])
                if dur <= 0:
                    await channel.send("❌ Cannot determine duration to split.")
                else:
                    # segment time to keep under limit
                    seg_time = max(1, int(dur * (limit / os.path.getsize(paths['comp']))))
                    proc3 = await asyncio.create_subprocess_exec(
                        "ffmpeg", *ff_args,
                        "-i", paths['comp'],
                        "-c", "copy", "-map", "0",
                        "-f", "segment", "-segment_time", str(seg_time),
                        "-reset_timestamps", "1", paths['seg_pattern'],
                        stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL
                    )
                    await proc3.wait()
                    # Send segments
                    for f in sorted(os.listdir(self.temp_dir)):
                        if f.startswith(f"{uid}_seg") and f.endswith(".mp4"):
                            seg_path = os.path.join(self.temp_dir, f)
                            if os.path.getsize(seg_path) <= limit:
                                await channel.send(file=discord.File(seg_path))
                            else:
                                await channel.send(f"⚠️ Segment {f} still too large.")
        # Cleanup
        for f in os.listdir(self.temp_dir):
            if uid in f:
                try:
                    os.remove(os.path.join(self.temp_dir, f))
                except OSError:
                    pass

async def setup(bot: commands.Bot):
    await bot.add_cog(VideoConvertCog(bot))
