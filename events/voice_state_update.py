import discord
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import Bot
import asyncio

async def setup_voice_state_update(bot):
    @bot.event
    async def on_voice_state_update(member, before, after):
        if before.channel is not None:
            await on_member_leave_vc(before.channel)
        if after.channel and after.channel.name == "Join To Create VC":
            guild = after.channel.guild
            category = after.channel.category
            channel_name = f"{member.display_name}'s VC"
            new_channel = await guild.create_voice_channel(name=channel_name, category=category)
            await member.move_to(new_channel)

async def on_member_leave_vc(channel):
    await asyncio.sleep(1)

    if channel.name.endswith("'s VC") and len(channel.members) == 0:
        await channel.delete(reason="VC Cleanup")