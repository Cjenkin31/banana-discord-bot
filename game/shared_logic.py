from data.Currency.currency import get_bananas
from utils.emoji_helper import BANANA_COIN_EMOJI

async def bet_checks(bet_amount, interaction):
    user_id = str(interaction.user.id)
    current_bananas = await get_bananas(user_id)
    error_message = None

    if isinstance(bet_amount, str):
        bet_amount = bet_amount.strip().lower()
        if bet_amount == 'all':
            if current_bananas == 0:
                error_message = f"You have no {BANANA_COIN_EMOJI}!"
            else:
                return True, current_bananas
        elif not bet_amount.isdigit():
            error_message = "Please input a valid number or 'all'"
        else:
            bet_amount = int(bet_amount)
    else:
        try:
            bet_amount = int(bet_amount)
        except ValueError:
            error_message = "Please input a valid number."

    if error_message is None:
        if bet_amount <= 0:
            error_message = "Bet amount must be a positive number."
        elif bet_amount > current_bananas:
            error_message = f"You don't have enough {BANANA_COIN_EMOJI} to make this bet."

    if error_message:
        return False, error_message

    return True, bet_amount