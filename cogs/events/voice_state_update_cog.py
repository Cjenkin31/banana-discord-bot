import datetime
import asyncio

from discord.ext import commands
from firebase_admin import db

from data.firebase_voicechat import add_temp_vc, delete_temp_vc, get_join_to_create_vc, get_temp_vcs
from data.Firebase.firebase_activity import add_time_spent


class ActivityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Key: (user_id, guild_id) → Value: datetime.datetime (UTC) when they joined voice
        self._join_times: dict[tuple[int, int], datetime.datetime] = {}

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        guild_id = member.guild.id
        user_id = member.id

        if before.channel is not None:
            await self._maybe_delete_temp_vc(before.channel)

        join_to_create_vc_id = await get_join_to_create_vc(guild_id)
        if after.channel and after.channel.id == join_to_create_vc_id:
            guild = after.channel.guild
            category = after.channel.category
            channel_name = f"{member.display_name}'s VC"
            new_channel = await guild.create_voice_channel(name=channel_name, category=category)
            await member.move_to(new_channel)
            await add_temp_vc(guild_id, new_channel.id)

        if before.channel is not None and before.channel != after.channel:
            key = (user_id, guild_id)
            join_time = self._join_times.pop(key, None)
            if join_time:
                now_utc = datetime.datetime.utcnow()
                delta = now_utc - join_time
                minutes_spent = int(delta.total_seconds() // 60)
                if minutes_spent > 0:
                    add_time_spent(user_id, guild_id, minutes_spent)

        if after.channel is not None and before.channel != after.channel:
            key = (user_id, guild_id)
            self._join_times[key] = datetime.datetime.utcnow()

    async def _maybe_delete_temp_vc(self, channel):
        """
        If a “temp” VC is now empty, remove it from Firebase and delete the channel.
        """
        await asyncio.sleep(1)
        temp_vcs = await get_temp_vcs(channel.guild.id)
        if str(channel.id) in temp_vcs and len(channel.members) == 0:
            await delete_temp_vc(channel.guild.id, channel.id)
            await channel.delete(reason="VC Cleanup")

async def setup(bot):
    await bot.add_cog(ActivityCog(bot))
