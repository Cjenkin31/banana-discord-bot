from config.config import SERVERS
from data.firebase_announcement import set_announcement_channel, get_announcement_channel
import discord
from discord.ext import commands
from discord import app_commands
from utils.users import UNBUTTERED_BAGEL_ID

class SetAnnouncementChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="set_announcement_channel", description="Sets the announcement channel for announcements.")
    @app_commands.describe(channel="Sets the announcement channel for announcements.")
    @app_commands.guilds(*SERVERS)
    @app_commands.check(lambda interaction: interaction.user.id == UNBUTTERED_BAGEL_ID)
    async def set_announcement_channel_command(self, interaction: discord.Interaction, channel: discord.TextChannel):
        existing_channel_id = await get_announcement_channel(interaction.guild.id)
        if existing_channel_id == channel.id:
            await interaction.response.send_message(f"The 'Announcement Channel' is already set to {channel.name}.", ephemeral=True)
            return

        await set_announcement_channel(interaction.guild.id, channel.id)
        await interaction.response.send_message(f"The 'Announcement Channel' has been set to {channel.name}.")

async def setup(bot):
    await bot.add_cog(SetAnnouncementChannel(bot))