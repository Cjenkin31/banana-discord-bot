import asyncio
from discord import app_commands
import discord
import random
from data.currency import get_bananas, add_bananas, remove_bananas
from game.shared_logic import bet_checks
from utils.emoji_helper import BANANA_COIN_EMOJI
from discord import Embed
from utils.image_helpers import download_from_github, download_gif_from_github

async def define_roulette_command(tree, servers):
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
    async def bet_value_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        choices = []
        bet_type = interaction.data.get('options', [])[0].get('value')
        if bet_type == 'color':
            choices = [
                app_commands.Choice(name="Red", value="red"),
                app_commands.Choice(name="Black", value="black"),
                app_commands.Choice(name="Green", value="green")
            ]
        elif bet_type == 'even_odd':
            choices = [
                app_commands.Choice(name="Even", value="even"),
                app_commands.Choice(name="Odd", value="odd")
            ]
        elif bet_type == 'range':
            choices = [
                app_commands.Choice(name="Low (1-18)", value="low"),
                app_commands.Choice(name="High (19-36)", value="high")
            ]
        elif bet_type == 'dozens':
            choices = [
                app_commands.Choice(name="First Dozen (1-12)", value="first"),
                app_commands.Choice(name="Second Dozen (13-24)", value="second"),
                app_commands.Choice(name="Third Dozen (25-36)", value="third")
            ]
        elif bet_type == 'columns':
            choices = [
                app_commands.Choice(name="Column 1", value="1"),
                app_commands.Choice(name="Column 2", value="2"),
                app_commands.Choice(name="Column 3", value="3")
            ]
        elif bet_type == 'number':
            return []
        # Filter choices based on the current input to reduce suggestions
        filtered_choices = [choice for choice in choices if current.lower() in choice.name.lower()]
        return filtered_choices

    @tree.command(name="roulette", description="Play roulette", guilds=servers)
    @app_commands.describe(bet_amount="Amount of bananas to bet",
                           bet_type="Type of bet you want to make",
                           bet_value="The value you want to bet on")
    @app_commands.choices(bet_type=bet_types)
    @app_commands.autocomplete(bet_value=bet_value_autocomplete)
    async def roulette(interaction: discord.Interaction, bet_type: app_commands.Choice[str], bet_value: str, bet_amount: int):
        user_id = str(interaction.user.id)
        valid, response = await bet_checks(bet_amount, interaction)
        if not valid:
            await interaction.response.send_message(str(response))
            return
        bet_amount = response

        if bet_type.value == 'number':
            try:
                bet_value_int = int(bet_value)
                if not 0 <= bet_value_int <= 36:
                    await interaction.response.send_message("Please choose a number between 0 and 36.", ephemeral=True)
                    return
            except ValueError:
                await interaction.response.send_message("Invalid input. Please enter a valid number.", ephemeral=True)
                return

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
        gif_file = await download_gif_from_github("spinning_wheel.gif")
        winning_number = random.choice(numbers)
        winning_color = colors[winning_number]
        win = False
        embed = Embed(title="🎰 Roulette Wheel Spinning...", description="Let's see where the ball lands!", color=0x0099ff)
        embed.add_field(name="Your Bet", value=f"Type: {bet_type.name}\nValue: {bet_value}\nAmount: {bet_amount} {BANANA_COIN_EMOJI}", inline=False)
        embed.set_image(url="attachment://image.gif")
        await interaction.response.send_message(embed=embed, file=gif_file)
        await asyncio.sleep(3)

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

        result_embed = Embed(title="Roulette Result", description=f"The ball landed on **{winning_color} {winning_number}**.", color=0x00ff00 if win else 0xff0000)
        result_embed.add_field(name="Your Bet", value=f"Type: {bet_type.name}\nValue: {bet_value}\nAmount: {bet_amount} {BANANA_COIN_EMOJI}", inline=False)

        result_color = 0x00ff00 if win else 0xff0000
        result_embed.title = "Roulette Result"
        result_embed.description = f"The ball landed on **{winning_color} {winning_number}**."
        result_embed.color = result_color
        result_embed.set_image(url=None)

        if win:
            payout = payouts[bet_type.value] * bet_amount
            await add_bananas(user_id, payout)
            result_embed.add_field(name="Result", value=f"Congratulations! You won {payout} {BANANA_COIN_EMOJI}!", inline=False)
        else:
            await remove_bananas(user_id, bet_amount)
            result_embed.add_field(name="Result", value=f"Sorry, you lost {bet_amount} {BANANA_COIN_EMOJI}. Better luck next time!", inline=False)

        await interaction.edit_original_response(embed=result_embed, attachments=[])
