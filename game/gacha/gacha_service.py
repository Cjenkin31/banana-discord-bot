from asyncio.log import logger
import random
from data.gacha_config import INGREDIENTS
from data.Currency.currency import remove_bananas
from data.gacha_rolls import try_gacha
from data.items import add_item
from data.stats import get_luck
from game.shared_logic import bet_checks
from utils.gacha import GACHA_SPIN_COST

ROLL_COST = GACHA_SPIN_COST

class GachaService:
    @staticmethod
    async def roll_ingredient(user_id, interaction, amount=1,):
        bet_amount = ROLL_COST * amount

        valid, response = await bet_checks(bet_amount, interaction)

        if not valid:
            logger.warning("Bet validation failed for user %s. Response: %s", interaction.user, response)
            return False , response

        gacha_valid, gacha_resposne = await try_gacha(amount, user_id)
        if not gacha_valid:
            return False , gacha_resposne

        await remove_bananas(user_id, ROLL_COST*amount)

        base_weights = [item["weight"] for item in INGREDIENTS]
        user_luck = await get_luck(user_id)
        adjusted_weights = [w + (user_luck * 0.05) for w in base_weights]
        full_ingredient_list = []
        for _ in range(amount):
            ingredient = random.choices(INGREDIENTS, weights=adjusted_weights, k=1)[0]
            full_ingredient_list.append(ingredient)
            await add_item(user_id, ingredient["name"])
        message = f"You rolled {amount} times and got: {', '.join([ingredient['name'] for ingredient in full_ingredient_list])}"
        return full_ingredient_list, message
