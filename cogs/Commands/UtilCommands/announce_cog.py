from config.config import SERVERS
from data.firebase_announcement import get_announcement_channel, get_all_announcement_channels
import discord
from discord.ext import commands
from discord import app_commands
from utils.users import UNBUTTERED_BAGEL_ID

class AnnouncementCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_owner():
        async def predicate(interaction: discord.Interaction):
            return interaction.user.id == UNBUTTERED_BAGEL_ID
        return app_commands.check(predicate)

    @app_commands.command(name="announce", description="...")
    @app_commands.guilds(*SERVERS)
    @is_owner()
    async def announce(self, interaction: discord.Interaction, user_input: str, channel_ids: str = ""):
        await interaction.response.defer()
        print(channel_ids)
        if not channel_ids:
            print("getting all channels")
            channel_ids = await get_all_announcement_channels()
            print(channel_ids)
        else:
            print("splitting channel ids")
            channel_ids = [int(id.strip()) for id in channel_ids.split(",") if id.strip().isdigit()]
            print(channel_ids)
        for channel_id in channel_ids:
            print(channel_id)
            channel = self.bot.get_channel(int(channel_id))
            if channel is None:
                try:
                    channel = await self.bot.fetch_channel(int(channel_id))
                except discord.NotFound:
                    await interaction.response.send_message(f"Channel with ID {channel_id} not found.", ephemeral=True)
                    continue
                except discord.Forbidden:
                    await interaction.response.send_message(f"Bot does not have access to the channel with ID {channel_id}.", ephemeral=True)
                    continue
                except discord.HTTPException as e:
                    await interaction.response.send_message(f"Failed to fetch channel due to an HTTP error: {e}", ephemeral=True)
                    continue
            print(f"Channel = {channel}")
            if channel:
                print("sending message")
                await channel.send(user_input)
            else:
                await interaction.response.send_message(f"Failed to send message to channel {channel_id}", ephemeral=True)
            await interaction.followup.send("Message sent to all channels", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AnnouncementCog(bot))
