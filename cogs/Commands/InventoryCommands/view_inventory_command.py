from config.config import SERVERS
import discord
from discord.ext import app_commands
from discord.ext.commands import Cog
from data.items import get_inventory

class ViewInventoryCommand(Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="view_inventory", description="View your inventory")
    @app_commands.guilds(SERVERS)
    async def view_inventory(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        inventory = await get_inventory(user_id)
        
        if not inventory:
            await interaction.response.send_message("Your inventory is empty.", ephemeral=True)
            return

        items_text = "\n".join([f"{item}: {count}" for item, count in inventory.items()])
        embed = discord.Embed(title="Inventory", description=items_text, color=discord.Color.blurple())
        await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(ViewInventoryCommand(bot))
