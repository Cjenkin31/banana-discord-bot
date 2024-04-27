from discord.ext import commands
from discord import app_commands
import discord
import random
from data.currency import get_bananas, add_bananas, remove_bananas

def define_coinflip_command(tree, servers):
    @tree.command(name="coinflip", description="Guess Heads or Tails to double your bet or lose it", guilds=servers)
    @app_commands.describe(choice="Choose Heads or Tails", bet_amount="Amount of bananas to bet")
    async def coinflip(interaction: discord.Interaction, choice: str, bet_amount: int):
        if bet_amount <= 0:
            await interaction.response.send_message("You need to bet a positive amount of bananas.")
            return

        user_choice = choice.strip().lower()
        if user_choice not in ['heads', 'tails']:
            await interaction.response.send_message("Please choose either 'Heads' or 'Tails'.")
            return

        user_id = str(interaction.user.id)
        current_bananas = await get_bananas(user_id)

        if bet_amount > current_bananas:
            await interaction.response.send_message("You don't have enough bananas to make this bet.")
            return

        result = "heads" if random.choice([True, False]) else "tails"

        if user_choice == result:
            await add_bananas(user_id, bet_amount)
            message = f"It's **{result}**! You won! Your bet has been doubled, increasing by {bet_amount} bananas."
        else:
            await remove_bananas(user_id, bet_amount)
            message = f"It's **{result}**! You lost your bet of {bet_amount} bananas."

        await interaction.response.send_message(message)