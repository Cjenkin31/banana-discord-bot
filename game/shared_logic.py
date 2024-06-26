from data.Currency.currency import get_bananas, add_bananas, remove_bananas
import discord
from discord import app_commands
from utils.emoji_helper import BANANA_COIN_EMOJI

async def bet_checks(bet_amount, interaction):
    user_id = str(interaction.user.id)
    current_bananas = await get_bananas(user_id)

    if isinstance(bet_amount, str):
        bet_amount = bet_amount.strip().lower()
        if bet_amount == 'all':
            if current_bananas == 0:
                return False, f"You have no {BANANA_COIN_EMOJI}!"
            return True, current_bananas
        elif not bet_amount.isdigit():
            return False, "Please input a valid number or 'all'"

    if isinstance(bet_amount, str):
        try:
            bet_amount = int(bet_amount)
        except ValueError:
            return False, "Please input a valid number."
    
    if not isinstance(bet_amount, int) or bet_amount <= 0:
        return False, "Bet amount must be a positive number."

    if bet_amount > current_bananas:
        return False, f"You don't have enough {BANANA_COIN_EMOJI} to make this bet."

    return True, bet_amount
