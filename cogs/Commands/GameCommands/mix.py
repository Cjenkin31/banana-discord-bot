from config.config import SERVERS
import discord
from discord.ext import commands
from discord import app_commands
from data.items import get_inventory
from game.crafting_service import DynamicCraftingService

class IngredientButton(discord.ui.Button):
    def __init__(self, ingredient: str, available: int):
        self.ingredient = ingredient
        self.available = available
        self.selected = 0
        label = f"{ingredient} (0/{available})"
        super().__init__(label=label, style=discord.ButtonStyle.secondary, custom_id=ingredient)

    async def callback(self, interaction: discord.Interaction):
        view: MixingView = self.view
        # Increment the selection if possible
        if self.selected < self.available:
            if view.total_selected() < view.max_total:
                self.selected += 1
                self.label = f"{self.ingredient} ({self.selected}/{self.available})"
                await interaction.response.edit_message(view=view)
            else:
                await interaction.followup.send("You have reached the maximum total ingredients.", ephemeral=True)
        else:
            await interaction.followup.send(f"You've already selected all available {self.ingredient}.", ephemeral=True)

class ResetButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Reset Selections", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        view: MixingView = self.view
        for button in view.buttons_dict.values():
            button.selected = 0
            button.label = f"{button.ingredient} (0/{button.available})"
        await interaction.response.edit_message(view=view)

class MixButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Mix", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)  # Defer immediately
        view: MixingView = self.view
        total = view.total_selected()
        if total < view.min_total:
            await interaction.followup.send(
                f"You must select at least {view.min_total} ingredients (you selected {total}).", ephemeral=True
            )
            return
        if total > view.max_total:
            await interaction.followup.send(
                f"You can only select up to {view.max_total} ingredients (you selected {total}).", ephemeral=True
            )
            return

        selection_list = view.get_selection_list()
        success, result_message = await DynamicCraftingService.craft_dynamic(view.user_id, selection_list)
        ingredients_str = ", ".join(selection_list)
        if not success:
            final_message = f"Failed to mix **{ingredients_str}**: {result_message}"
        else:
            final_message = f"By mixing **{ingredients_str}**, <@{view.user_id}> crafted: {result_message}"
        await interaction.followup.send(final_message, ephemeral=False)
        view.stop()


class CancelButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Cancel", style=discord.ButtonStyle.red)

    async def callback(self, interaction: discord.Interaction):
        await interaction.followup.send("Mixing canceled.", ephemeral=True)
        self.view.stop()

class MixingView(discord.ui.View):
    def __init__(self, user_id: str, inventory: dict):
        # Extended timeout from 60 to 180 seconds
        super().__init__(timeout=180)
        self.user_id = user_id
        self.min_total = 3
        self.max_total = 5
        self.buttons_dict = {}
        # Create a button for each ingredient in the inventory.
        for ingredient, qty in inventory.items():
            button = IngredientButton(ingredient, qty)
            self.buttons_dict[ingredient] = button
            self.add_item(button)
        # Add the Mix, Reset, and Cancel buttons.
        self.add_item(MixButton())
        self.add_item(ResetButton())
        self.add_item(CancelButton())

    def total_selected(self):
        return sum(button.selected for button in self.buttons_dict.values())

    def get_selection_list(self):
        # Return a list containing duplicates if necessary.
        selection = []
        for ingredient, button in self.buttons_dict.items():
            selection.extend([ingredient] * button.selected)
        return selection

class MixCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.guilds(*SERVERS)
    @app_commands.command(name="mix", description="Mix ingredients to craft an item")
    async def mix(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        user_id = str(interaction.user.id)
        inventory = await get_inventory(user_id)
        if not inventory:
            await interaction.followup.send("You have no ingredients to mix.", ephemeral=False)
            return
        view = MixingView(user_id, inventory)
        await interaction.followup.send(
            "Select ingredients to mix by clicking the buttons below.\n(Min: 3, Max: 5 total ingredients)\nIf you misclick, click **Reset Selections** to clear your current picks.",
            view=view,
            ephemeral=False,
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(MixCog(bot))
