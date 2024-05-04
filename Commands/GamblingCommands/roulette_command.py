import asyncio
from discord import app_commands
import discord
import random
from data.currency import get_bananas, add_bananas, remove_bananas
from game.shared_logic import bet_checks
from utils.emoji_helper import BANANA_COIN_EMOJI
from discord import Embed

async def define_roulette_command(tree, servers, bot):
    bet_types = [
        app_commands.Choice(name="number", value="number"),
        app_commands.Choice(name="color", value="color"),
        app_commands.Choice(name="even or odd", value="even_odd"),
        app_commands.Choice(name="low (1-18) or high (19-36)", value="range"),
        app_commands.Choice(name="dozens (first, second, third)", value="dozens"),
        app_commands.Choice(name="columns (1, 2, 3)", value="columns")
    ]
    # Which column a number belongs to
    def get_column(number):
        if number % 3 == 1:
            return 1
        elif number % 3 == 2:
            return 2
        else:
            return 3
    @tree.command(name="roulette", description="Play roulette", guilds=servers)
    @app_commands.describe(bet_amount="Amount of bananas to bet",
                           bet_type="Type of bet you want to make",
                           bet_value="The value you want to bet on")
    @app_commands.choices(bet_type=bet_types)
    async def roulette(interaction: discord.Interaction, bet_type: app_commands.Choice[str], bet_value: str, bet_amount: int):
        user_id = str(interaction.user.id)
        bet_amount = 10 # Force bet_amount to 10 for testing
        valid, response = await bet_checks(bet_amount, interaction)
        if not valid:
            await interaction.response.send_message(str(response))
            return
        bet_amount = response

        numbers = list(range(37))
        colors = {num: 'red' if (num != 0 and (num < 10 or 18 < num < 28)) else 'black' for num in numbers}
        colors[0] = 'green'  # Zero is green

        payouts = {
            'number': 35,
            'color': 1,
            'even_odd': 1,
            'range': 1,
            'dozens': 2,
            'columns': 2
        }

        winning_number = random.choice(numbers)
        winning_color = colors[winning_number]
        win = False

        try:
            if bet_type.value == 'number':
                win = int(bet_value) == winning_number
            elif bet_type.value == 'color':
                win = bet_value.lower() == winning_color
            elif bet_type.value == 'even_odd':
                win = (bet_value == 'even' and winning_number % 2 == 0) or (bet_value == 'odd' and winning_number % 2 != 0)
            elif bet_type.value == 'range':
                win = (bet_value == 'low' and 1 <= winning_number <= 18) or (bet_value == 'high' and 19 <= winning_number <= 36)
            elif bet_type.value == 'dozens':
                win = (bet_value == 'first' and 1 <= winning_number <= 12) or \
                      (bet_value == 'second' and 13 <= winning_number <= 24) or \
                      (bet_value == 'third' and 25 <= winning_number <= 36)
            elif bet_type.value == 'columns':
                win = int(bet_value) == get_column(winning_number)
        except ValueError:
            await interaction.response.send_message("Invalid bet value. Please check your input and try again.")
            return
        embed = Embed(title="🎰 Roulette Wheel Spinning...", description="Let's see where the ball lands!", color=0x0099ff)
        embed.add_field(name="Your Bet", value=f"Type: {bet_type.name}\nValue: {bet_value}\nAmount: {bet_amount} {BANANA_COIN_EMOJI}", inline=False)
        await interaction.response.send_message(embed=embed)
        await asyncio.sleep(3)
        result_color = 0x00ff00 if win else 0xff0000
        embed.title = "Roulette Result"
        embed.description = f"The ball landed on **{winning_color} {winning_number}**."
        embed.color = result_color

        # Dont add or remove for testing
        if win:
            payout = payouts[bet_type.value] * bet_amount
            # add_bananas(user_id, payout)
            embed.add_field(name="Result", value=f"Congratulations! You won {payout} {BANANA_COIN_EMOJI}!", inline=False)
        else:
            # remove_bananas(bet_amount)
            embed.add_field(name="Result", value=f"Sorry, you lost {bet_amount} {BANANA_COIN_EMOJI}. Better luck next time!", inline=False)

        await interaction.edit_original_response(embed=embed)
