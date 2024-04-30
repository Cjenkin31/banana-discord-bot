import discord
from discord.ui import View, Button
from data.items import add_item
from data.currency import get_bananas, remove_bananas
from utils.emoji_helper import BANANA_COIN_EMOJI

class ShopView(View):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        
        item_1_button = Button(label=f"Item 1 (50 {BANANA_COIN_EMOJI})", style=discord.ButtonStyle.primary, custom_id="buy_item_1")
        item_1_button.callback = self.buy_item_1_callback
        self.add_item(item_1_button)
        
        item_2_button = Button(label=f"Item 2 (100 {BANANA_COIN_EMOJI})", style=discord.ButtonStyle.primary, custom_id="buy_item_2")
        item_2_button.callback = self.buy_item_2_callback
        self.add_item(item_2_button)

    async def buy_item_1_callback(self, interaction: discord.Interaction):
        await self.buy_item(interaction, "Item 1", 50)

    async def buy_item_2_callback(self, interaction: discord.Interaction):
        await self.buy_item(interaction, "Item 2", 100)

    async def buy_item(self, interaction, item_name, item_cost):
        user_bananas = await get_bananas(str(self.user_id))
        if user_bananas < item_cost:
            await interaction.response.send_message(f"You do not have enough {BANANA_COIN_EMOJI} to purchase this item.", ephemeral=True)
        else:
            await remove_bananas(str(self.user_id), item_cost)
            await add_item(str(self.user_id), item_name)
            await interaction.response.send_message(f"{item_name} purchased successfully!", ephemeral=True)

    async def on_timeout(self):
        self.clear_items()

    async def on_error(self, error, item, interaction):
        self.clear_items()
        await interaction.response.send_message("An error occurred while processing your request. Please try again later.", ephemeral=True)

async def define_shop_command(tree, servers):
    @tree.command(name="shop", description="Visit the shop to buy items", guilds=servers)
    async def shop(interaction: discord.Interaction):
        user_id = interaction.user.id
        view = ShopView(user_id)
        await interaction.response.send_message("Welcome to the shop!", view=view, ephemeral=True)
