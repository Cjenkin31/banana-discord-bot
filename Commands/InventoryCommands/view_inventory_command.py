import discord
from discord.ext import commands
from data.items import get_inventory

async def define_view_inventory_command(tree, servers):
    @tree.command(name="view_inventory", description="View your inventory", guilds=servers)
    async def view_inventory(interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        inventory = await get_inventory(user_id)
        
        if not inventory:
            await interaction.response.send_message("Your inventory is empty.", ephemeral=True)
            return

        items_text = "\n".join([f"{item}: {count}" for item, count in inventory.items()])
        embed = discord.Embed(title="Inventory", description=items_text, color=discord.Color.blurple())
        await interaction.response.send_message(embed=embed, ephemeral=True)
