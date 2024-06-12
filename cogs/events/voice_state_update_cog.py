from data.firebase_voicechat import add_temp_vc, delete_temp_vc, get_join_to_create_vc, get_temp_vcs
import discord
from discord.ext import commands
import asyncio

class VoiceStateUpdateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        guild_id = member.guild.id

        if before.channel is not None:
            await self.on_member_leave_vc(before.channel)

        join_to_create_vc_id = await get_join_to_create_vc(guild_id)
        if after.channel and after.channel.id == join_to_create_vc_id:
            guild = after.channel.guild
            category = after.channel.category
            channel_name = f"{member.display_name}'s VC"
            new_channel = await guild.create_voice_channel(name=channel_name, category=category)
            await member.move_to(new_channel)
            await add_temp_vc(guild_id, new_channel.id)

    async def on_member_leave_vc(self, channel):
        await asyncio.sleep(1)
        
        temp_vcs = await get_temp_vcs(channel.guild.id)
        if str(channel.id) in temp_vcs and len(channel.members) == 0:
            await delete_temp_vc(channel.guild.id, channel.id)
            await channel.delete(reason="VC Cleanup")

def setup(bot):
    bot.add_cog(VoiceStateUpdateCog(bot))