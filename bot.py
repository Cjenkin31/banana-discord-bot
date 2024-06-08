from Commands.setup_commands import define_all_commands
from data.firebase_voicechat import delete_temp_vc, get_temp_vcs
import discord
from discord.ext import commands
from config.config import SERVERS, TOKEN, INTENTS
from events.setup_events import setup_events
from utils.error_handlers import setup_logging

bot = commands.Bot(command_prefix="!", intents=INTENTS)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    await setup_events(bot)
    await define_all_commands(bot, SERVERS)
    await cleanup_temp_vcs()
    for guild in SERVERS:
        try:
            await bot.tree.sync(guild=guild)
            print(f"Commands synced successfully with guild: {guild.id}")
        except Exception as e:
            print(f"Failed to sync commands with guild: {guild.id}, error: {e}")

async def cleanup_temp_vcs():
    for guild in bot.guilds:
        temp_vcs = await get_temp_vcs(guild.id)
        for channel_id in temp_vcs:
            channel = guild.get_channel(int(channel_id))
            if channel and len(channel.members) == 0:
                await delete_temp_vc(guild.id, channel.id)
                await channel.delete(reason="VC Cleanup after bot restart")

if __name__ == "__main__":
    bot.run(TOKEN)
