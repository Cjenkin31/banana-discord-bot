from discord.ext import commands
from discord import app_commands
import discord
import random
from data.currency import get_bananas, add_bananas, remove_bananas

def define_coinflip_command(tree, servers):
    @tree.command(name="coinflip", description="Guess Heads or Tails to double your bet or lose it", guilds=servers)
    @app_commands.describe(choice="Choose Heads or Tails", bet_amount="Amount of bananas to bet or 'all'")
    async def coinflip(interaction: discord.Interaction, choice: str, bet_amount: str):
        user_choice = choice.strip().lower()
        valid_heads = ['heads', 'head', 'h']
        valid_tails = ['tails', 'tail', 't']

        if user_choice not in valid_heads + valid_tails:
            await interaction.response.send_message("Please choose either 'Heads' or 'Tails'.")
            return
        
        # Determine if the bet is 'all' or a specific amount
        if bet_amount.lower() == 'all':
            current_bananas = await get_bananas(str(interaction.user.id))
            bet_amount = current_bananas
        else:
            try:
                bet_amount = int(bet_amount)
                if bet_amount <= 0:
                    raise ValueError("Bet amount must be a positive number.")
            except ValueError as e:
                await interaction.response.send_message(str(e))
                return

        user_id = str(interaction.user.id)
        current_bananas = await get_bananas(user_id)

        if bet_amount > current_bananas:
            await interaction.response.send_message("You don't have enough bananas to make this bet.")
            return

        # Coin flip logic
        result = "heads" if random.choice([True, False]) else "tails"
        win = (user_choice in valid_heads and result == "heads") or (user_choice in valid_tails and result == "tails")

        if win:
            await add_bananas(user_id, bet_amount)
            message = f"It's **{result}**! You won! Your bet has been doubled, increasing by {bet_amount} bananas."
        else:
            await remove_bananas(user_id, bet_amount)
            message = f"It's **{result}**! You lost your bet of {bet_amount} bananas."

        await interaction.response.send_message(message)
