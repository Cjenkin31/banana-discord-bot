from config.config import SERVERS
import discord
from discord import app_commands
from discord import commands

class CleanupVCCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="cleanupvc", description="Cleans up voice chats.", guilds=SERVERS)
    async def cleanupvc(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message("Something went wrong with guild interaction.")
            return

        vcListToClean = [vc for vc in guild.voice_channels if vc.name.endswith("'s VC") and len(vc.members) == 0]

        if not vcListToClean:
            await interaction.response.send_message("No empty VC's found to clean up.")
            return

        for vc in vcListToClean:
            await vc.delete(reason="VC Cleanup")

        await interaction.response.send_message(f"Cleaned up {len(vcListToClean)} VC(s).")

def setup(bot):
    bot.add_cog(CleanupVCCommand(bot))