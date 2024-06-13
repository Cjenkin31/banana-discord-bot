import discord
from discord.ext import commands
from discord import app_commands
from data.Currency.currency import get_bananas, add_bananas, remove_bananas
from utils.emoji_helper import BANANA_COIN_EMOJI
class ConfirmView(discord.ui.View):
    def __init__(self, user: discord.User, amount: int, initiator: discord.User, channel: discord.TextChannel):
        super().__init__()
        self.user = user
        self.amount = amount
        self.initiator = initiator
        self.channel = channel

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if initiator has enough bananas
        initiator_bananas = await get_bananas(str(self.initiator.id))
        if initiator_bananas < self.amount:
            await interaction.response.send_message("You do not have enough bananas to complete this transaction.", ephemeral=True)
            self.stop()
            return

        # Perform the banana transaction
        await remove_bananas(str(self.initiator.id), self.amount)
        await add_bananas(str(self.user.id), self.amount)

        # Disable all buttons in this view
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True

        await interaction.response.edit_message(content="Transaction completed.", view=self)

        # Send the public message to the channel
        message = f"{self.user.mention}, you have received {self.amount} {BANANA_COIN_EMOJI} from {self.initiator.mention}."
        await self.channel.send(message)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Notify the user that the transaction is canceled and disable buttons
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True

        await interaction.response.edit_message(content="Canceled trade.", view=None)
        self.stop()

async def define_send_bananas_command(tree, servers):
    @tree.command(name="send_bananas", description="Send bananas to another user", guilds=servers)
    async def send_bananas(interaction: discord.Interaction, user: discord.User, amount: int):
        if (interaction.user.id == user.id):
            await interaction.response.send_message(f"You cannot send yourself coins!", ephemeral=True)
            return
        if amount <= 0:
            await interaction.response.send_message(f"You cannot send a non-positive amount of {BANANA_COIN_EMOJI}.", ephemeral=True)
            return
        
        # Confirm transaction, using the channel from the interaction
        view = ConfirmView(user, amount, interaction.user, interaction.channel)
        await interaction.response.send_message(f"Are you sure you would like to give **{user.display_name}** {amount} {BANANA_COIN_EMOJI}?", view=view, ephemeral=True)

