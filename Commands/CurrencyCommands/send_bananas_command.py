import discord
from discord.ext import commands
from discord import app_commands
from data.currency import get_bananas, add_bananas, remove_bananas

class ConfirmView(discord.ui.View):
    def __init__(self, user: discord.User, amount: int, initiator: discord.User):
        super().__init__()
        self.user = user
        self.amount = amount
        self.initiator = initiator

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if initiator has enough bananas
        initiator_bananas = await get_bananas(str(self.initiator.id))
        if initiator_bananas < self.amount:
            await interaction.response.send_message("You do not have enough bananas to complete this transaction.", ephemeral=True)
            self.stop()
            return
        
        await remove_bananas(str(self.initiator.id), self.amount)
        await add_bananas(str(self.user.id), self.amount)
        
        await interaction.response.send_message(f"Successfully gave {self.user.display_name} {self.amount} bananas.")
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Canceled trade.", ephemeral=True)
        self.stop()

async def define_send_bananas_command(tree, servers):
    @tree.command(name="send_bananas", description="Give bananas to another user", guilds=servers)
    async def send_bananas(interaction: discord.Interaction, user: discord.User, amount: int):
        if amount <= 0:
            await interaction.response.send_message("You cannot send a non-positive amount of bananas.", ephemeral=True)
            return
        
        view = ConfirmView(user, amount, interaction.user)
        await interaction.response.send_message(f"Are you sure you would like to give **{user.display_name}** {amount} bananas?", view=view, ephemeral=True)
