import discord
from discord.ext import commands
from discord.ui import View, Button
from data.items import add_item
from data.currency import get_bananas, remove_bananas
from utils.emoji_helper import BANANA_COIN_EMOJI

class ShopView(View):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.add_item(Button(label=f"Item 1 (50 {BANANA_COIN_EMOJI})", style=discord.ButtonStyle.primary, custom_id="buy_item_1", callback=self.interaction_handler))
        self.add_item(Button(label=f"Item 2 (100 {BANANA_COIN_EMOJI})", style=discord.ButtonStyle.primary, custom_id="buy_item_2", callback=self.interaction_handler))

    async def on_timeout(self):
        self.clear_items()

    async def on_error(self, error, item, interaction):
        self.clear_items()
        await interaction.response.send_message("An error occurred while processing your request. Please try again later.", ephemeral=True)

    async def buy_item(self, interaction, item_name, item_cost):
        user_bananas = await get_bananas(str(self.user_id))
        if user_bananas < item_cost:
            await interaction.response.send_message(f"You do not have enough {BANANA_COIN_EMOJI} to purchase this item.", ephemeral=True)
            return
        else:
            await remove_bananas(str(self.user_id), item_cost)
            await add_item(str(self.user_id), item_name)
            await interaction.response.send_message(f"{item_name} purchased successfully!", ephemeral=True)

    async def interaction_handler(self, interaction):
        if interaction.custom_id == "buy_item_1":
            await self.buy_item(interaction, "Item 1", 50)
        elif interaction.custom_id == "buy_item_2":
            await self.buy_item(interaction, "Item 2", 100)

async def define_shop_command(tree, servers):
    @tree.command(name="shop", description="Visit the shop to buy items", guilds=servers)
    async def shop(interaction: discord.Interaction):
        user_id = interaction.user.id
        view = ShopView(user_id)
        await interaction.response.send_message("Welcome to the shop!", view=view, ephemeral=True)
