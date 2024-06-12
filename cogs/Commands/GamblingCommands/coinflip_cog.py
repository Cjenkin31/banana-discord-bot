from config.config import SERVERS
from discord import app_commands
import discord
import random
from data.currency import get_bananas, add_bananas, remove_bananas
from game.shared_logic import bet_checks
from utils.emoji_helper import BANANA_COIN_EMOJI

class Coinflip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="coinflip", description="Guess Heads or Tails to double your bet or lose it")
    @app_commands.guilds(SERVERS)
    @app_commands.describe(choice="Choose Heads or Tails", bet_amount="Amount of bananas to bet or 'all'")
    async def coinflip(self, interaction: discord.Interaction, choice: str, bet_amount: str):
        user_choice = choice.strip().lower()
        valid_heads = ['heads', 'head', 'h']
        valid_tails = ['tails', 'tail', 't']

        if user_choice not in valid_heads + valid_tails:
            await interaction.response.send_message("Please choose either 'Heads' or 'Tails'.")
            return
        
        valid, response = await bet_checks(bet_amount, interaction)
        if not valid:
            await interaction.response.send_message(str(response))
        bet_amount = int(response)

        user_id = str(interaction.user.id)

        # Coin flip logic
        result = "heads" if random.choice([True, False]) else "tails"
        win = (user_choice in valid_heads and result == "heads") or (user_choice in valid_tails and result == "tails")

        if win:
            await add_bananas(user_id, bet_amount)
            message = f"It's **{result}**! You won! Your bet has been doubled, increasing by {bet_amount} {BANANA_COIN_EMOJI}."
        else:
            await remove_bananas(user_id, bet_amount)
            message = f"It's **{result}**! You lost your bet of {bet_amount} {BANANA_COIN_EMOJI}."

        await interaction.response.send_message(message)

def setup(bot):
    bot.add_cog(Coinflip(bot))
