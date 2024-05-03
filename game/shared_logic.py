
from data.currency import get_bananas
from discord import app_commands
import discord
from data.currency import get_bananas, add_bananas, remove_bananas
from utils.emoji_helper import BANANA_COIN_EMOJI

async def bet_checks(bet_amount, interaction):    
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
            response = interaction.response.send_message(str(e))
            return False, response

    user_id = str(interaction.user.id)
    current_bananas = await get_bananas(user_id)

    if current_bananas == 0:
        response = (f"You have no {BANANA_COIN_EMOJI}!")
        return False, response
    
    if bet_amount > current_bananas:
        response = (f"You don't have enough {BANANA_COIN_EMOJI} to make this bet.")
        return False, response
    return True, bet_amount