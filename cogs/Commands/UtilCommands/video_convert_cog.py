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

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.attachments:
            return
        for attachment in message.attachments:
            if attachment.filename.lower().endswith(".mkv"):
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
        input_path = os.path.join(self.temp_dir, f"{uid}.mkv")
        output_path = os.path.join(self.temp_dir, f"{uid}.mp4")
        comp_path = os.path.join(self.temp_dir, f"{uid}_compressed.mp4")
        trimmed_path = os.path.join(self.temp_dir, f"{uid}_trimmed.mp4")

        await attachment.save(input_path)

        # Convert container
        p1 = await asyncio.create_subprocess_exec(
            "ffmpeg", "-i", input_path, "-c", "copy", output_path,
            stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL
        )
        await p1.wait()

        try:
            if not os.path.exists(output_path):
                await channel.send("❌ Conversion failed: output not found.")
                return
            limit = self._get_upload_limit(channel.guild)
            size = os.path.getsize(output_path)
            if size <= limit:
                await channel.send(file=discord.File(output_path))
                return
            # Compress
            await channel.send("🔄 File too large, compressing to fit upload limit...")
            p2 = await asyncio.create_subprocess_exec(
                "ffmpeg", "-i", output_path,
                "-c:v", "libx264", "-preset", "fast", "-crf", "28",
                "-c:a", "aac", "-b:a", "128k", comp_path,
                stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL
            )
            await p2.wait()
            if not os.path.exists(comp_path):
                await channel.send("❌ Compression failed: output not found.")
                return
            comp_size = os.path.getsize(comp_path)
            if comp_size <= limit:
                mb = comp_size / (1024 * 1024)
                await channel.send(f"✅ Compressed video to {mb:.2f} MB to fit the server limit.")
                try:
                    await channel.send(file=discord.File(comp_path))
                except discord.HTTPException as e:
                    await channel.send(f"❌ Failed to send compressed video: {e}")
                return
            # Trim start
            await channel.send("✂️ Even after compression it’s too big; trimming start until it fits...")
            duration = await self._get_duration(comp_path)
            if duration <= 0:
                await channel.send("❌ Could not determine video duration for trimming.")
                return
            keep_ratio = limit / comp_size
            keep_duration = duration * keep_ratio
            start_time = max(0, duration - keep_duration)
            p3 = await asyncio.create_subprocess_exec(
                "ffmpeg", "-ss", str(start_time), "-i", comp_path,
                "-c", "copy", trimmed_path,
                stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL
            )
            await p3.wait()
            if not os.path.exists(trimmed_path):
                await channel.send("❌ Trimming failed: output not found.")
                return
            trim_size = os.path.getsize(trimmed_path)
            if trim_size <= limit:
                mb = trim_size / (1024 * 1024)
                await channel.send(f"✂️ Trimmed video to last {keep_duration:.1f}s (~{mb:.2f} MB), now fits limit.")
                try:
                    await channel.send(file=discord.File(trimmed_path))
                except discord.HTTPException as e:
                    await channel.send(f"❌ Failed to send trimmed video: {e}")
            else:
                mb = trim_size / (1024 * 1024)
                lmb = limit / (1024 * 1024)
                await channel.send(f"⚠️ Trimming still too big ({mb:.2f} MB) vs limit {lmb:.2f} MB.")
        except Exception as e:
            await channel.send(f"❌ An error occurred: {e}")
        finally:
            for path in (input_path, output_path, comp_path, trimmed_path):
                try:
                    os.remove(path)
                except OSError:
                    pass

async def setup(bot: commands.Bot):
    await bot.add_cog(VideoConvertCog(bot))
