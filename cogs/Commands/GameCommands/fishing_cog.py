import discord
from discord.ext import commands
from discord import app_commands
from config.config import SERVERS
import random
import asyncio
from datetime import datetime, timedelta
from data.Fishing.fish_utils import load_fish_data, select_fish_by_rarity
import os
from utils.image_helpers import download_gif_from_github

class FishingView(discord.ui.View):
    def __init__(self, bot, user):
        super().__init__(timeout=None)
        self.bot = bot
        self.user = user
        print("Fishing View Init")

    @discord.ui.button(label="Cast Line", style=discord.ButtonStyle.primary, custom_id="cast_line")
    async def cast_line(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message("This is not your fishing session!", ephemeral=True)

        await interaction.response.defer()

        # Load fish data and shuffle actions
        fish_data = load_fish_data()
        caught_fish = select_fish_by_rarity(fish_data)
        random.shuffle(caught_fish["actions"])
        for action in caught_fish["actions"]:
            random.shuffle(action["options"])

        fishing_man = await download_gif_from_github("FishingMan.gif")
        if fishing_man:
            await interaction.followup.send("Casting line...", file=fishing_man)

        # Wait for the fish 'bite' time
        await asyncio.sleep(caught_fish['wait_time'])

        # Update message for caught fish and load mini-game
        man_caught_fish_gif = await download_gif_from_github("CaughtFish.gif")
        minigame_view = MiniGameView(self.bot, self.user, caught_fish, 0, datetime.utcnow())
        if man_caught_fish_gif:
            await interaction.followup.send("You got a bite! What will you do?", files=[man_caught_fish_gif], view=minigame_view)
        else:
            await interaction.followup.send("Failed to load the fish image, but you got a bite! What will you do?", view=minigame_view)

class MiniGameView(discord.ui.View):
    def __init__(self, bot, user, fish, action_index, last_action_time):
        super().__init__(timeout=None)
        self.bot = bot
        self.user = user
        self.fish = fish
        self.action_index = action_index
        self.last_action_time = last_action_time

        self.correct_action = self.fish['actions'][self.action_index]['correct']
        self.options = self.fish['actions'][self.action_index]['options']

        self.option_1 = discord.ui.Button(label=self.options[0], style=discord.ButtonStyle.primary, custom_id="option_1")
        self.option_2 = discord.ui.Button(label=self.options[1], style=discord.ButtonStyle.secondary, custom_id="option_2")

        self.option_1.callback = self.option_1_callback
        self.option_2.callback = self.option_2_callback

        self.add_item(self.option_1)
        self.add_item(self.option_2)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user.id

    async def option_1_callback(self, interaction: discord.Interaction):
        await self.handle_action(interaction, self.option_1)

    async def option_2_callback(self, interaction: discord.Interaction):
        await self.handle_action(interaction, self.option_2)

    async def handle_action(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            current_time = datetime.utcnow()
            time_diff = current_time - self.last_action_time

            if time_diff > timedelta(seconds=10):
                await interaction.followup.send("The fish escaped due to taking too long!", ephemeral=True)
                return

            selected_action = button.label

            if selected_action == self.correct_action:
                self.action_index += 1
                if self.action_index < len(self.fish['actions']):
                    next_view = MiniGameView(self.bot, self.user, self.fish, self.action_index, current_time)
                    await interaction.followup.send(content="Good job! Next action: What will you do?", view=next_view, ephemeral=False)
                else:
                    await interaction.followup.send(f"Congratulations! You caught a {self.fish['name']} worth {self.fish['value']} Banana Coins! Size: {self.fish['size']}, Rarity: {self.fish['rarity']}", ephemeral=False)
            else:
                await interaction.followup.send("The fish escaped! Better luck next time.", ephemeral=True)
        except Exception as e:
            print(f"Error handling action: {e}")
            await interaction.followup.send("An error occurred while processing your action.", ephemeral=True)

    async def clear_embeds(self, interaction: discord.Interaction, content: str):
        await interaction.followup.send(content=content, attachments=[], ephemeral=False)

class FishingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="fishing", description="Fishing Game!")
    @app_commands.guilds(*SERVERS)
    async def fishing_command(self, interaction: discord.Interaction):
        print("Fishing Command")
        await interaction.response.send_message("You have started fishing (THIS DOES NOT GIVE REAL COINS)! Press the 'Cast Line' button to begin.", view=FishingView(self.bot, interaction.user))

async def setup(bot):
    await bot.add_cog(FishingCog(bot))
