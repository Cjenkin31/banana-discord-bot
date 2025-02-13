import random
import asyncio
from collections import Counter
from firebase_admin import db
from data.gacha_config import INGREDIENTS
from data.stats import increase_luck
from data.Currency.currency import add_bananas
from utils.cooldown import apply_cooldown_reduction
from GPT_stories import getStoryByRole
from utils.gpt import generate_gpt_response
from utils.deepseek import generate_deepseek_response
from utils.gacha import GACHA_SPIN_COST
import math

GPT_MODEL = "gpt-4o"

def calculate_bonus_value(final_sweet, cost):
    """
    Logistic (S-curve) scaling function.
    bonus_multiplier = L / (1 + exp(-k * (final_sweet - x0)))

    For our tuning:
      - L (max multiplier) = 20, so the function saturates at 20× cost.
      - x0 (midpoint) = 50, so at final_sweet=50 the multiplier is 20/2 = 10.
      - k = 0.2 controls the steepness.

    This means:
      - For final_sweet well below 30, the bonus is very low.
      - At final_sweet=30, bonus ≈ 10 * cost = 1000.
      - For final_sweet above 30, the bonus climbs toward 20× cost.
    """
    L = 20  # Maximum multiplier
    k = 0.2 # Steepness constant
    x0 = 50 # Midpoint where bonus_multiplier = L/2 = 10
    bonus_multiplier = L / (1 + math.exp(-k * (final_sweet - x0)))
    bonus_value = cost * bonus_multiplier
    return bonus_value

class DynamicCraftingService:

    @staticmethod
    async def craft_dynamic(user_id: str, chosen_ingredients: list):
        """
        Craft a dynamic item by mixing chosen ingredients.
        :param user_id: The Discord user ID.
        :param chosen_ingredients: A list of ingredient names (as strings).
        :return: (success: bool, message: str)
        """
        ref = db.reference(f'users/{user_id}/inventory')

        ingredient_counts = Counter(chosen_ingredients)

        def transaction_update(inventory):
            if inventory is None:
                inventory = {}
            for ingredient, required_qty in ingredient_counts.items():
                if inventory.get(ingredient, 0) < required_qty:
                    raise Exception(f"Not enough {ingredient} in inventory. Required: {required_qty}, Available: {inventory.get(ingredient, 0)}")

            # Remove ingredients in one go
            for ingredient, required_qty in ingredient_counts.items():
                new_qty = inventory.get(ingredient, 0) - required_qty
                if new_qty <= 0:
                    del inventory[ingredient]
                else:
                    inventory[ingredient] = new_qty
            return inventory

        try:
            await asyncio.to_thread(ref.transaction, transaction_update)
        except Exception as e:
            return False, f"Error during ingredient removal: {e}"
        print("Ingredients removed successfully")
        # ----- Crafting Logic: Compute Totals for Each Attribute -----
        total_sweet = 0
        total_rich = 0
        total_magic = 0

        # Sum each attribute based on the chosen ingredients
        for ingredient_name in chosen_ingredients:
            ingredient = next(
                (item for item in INGREDIENTS if item["name"].lower() == ingredient_name.lower()),
                None
            )
            if ingredient:
                total_sweet += ingredient.get("sweetness", 0)
                total_rich += ingredient.get("richness", 0)
                total_magic += ingredient.get("magic", 0)
        print(f"Total sweetness: {total_sweet}, Total richness: {total_rich}, Total magic: {total_magic}")
        # Apply a random modifier to each total
        final_sweet = total_sweet * random.uniform(0.8, 1.2)
        final_rich = total_rich * random.uniform(0.8, 1.2)
        final_magic = total_magic * random.uniform(0.8, 1.2)

        # ----- Determine the Dominant Attribute -----
        if final_sweet >= final_rich and final_sweet >= final_magic:
            dominant = "sweetness"
        elif final_rich >= final_sweet and final_rich >= final_magic:
            dominant = "richness"
        else:
            dominant = "magic"

        # ----- Set Outcome Based on Dominant Attribute -----
        if dominant == "sweetness":
            if final_sweet < 15:
                bonus = "small_currency_bonus"
            elif final_sweet < 30:
                bonus = "small_currency_bonus"
            else:
                bonus = "big_currency_bonus"
            try:
                value = calculate_bonus_value(final_sweet, GACHA_SPIN_COST)
                value = round(value)
            except Exception as e:
                print(f"Error calculating bonus value: {e}")
                value = GACHA_SPIN_COST

            effect_description = "the inherent sweetness shines through"
        elif dominant == "richness":
            if final_rich < 15:
                bonus = "cooldown_reduction"
                value = 5
            elif final_rich < 30:
                bonus = "cooldown_reduction"
                value = 10
            else:
                bonus = "cooldown_reduction"
                value = 15
            effect_description = "the deep richness empowers your craft"
        else:
            if final_magic < 15:
                bonus = "luck_boost"
                value = 1
            elif final_magic < 30:
                bonus = "luck_boost"
                value = 2
            else:
                bonus = "luck_boost"
                value = 3
            effect_description = "a subtle magic infuses your mix"

        role = "item_flavor"

        try:
            item_story_string = f"The user has crafted a concoction with the following attributes: Sweetness: {final_sweet}, Richness: {final_rich}, Magic: {final_magic}. The dominant attribute is {dominant}. The outcome effect is {effect_description}. Using the following ingredients: {chosen_ingredients}."
            if random.choice([True, False]):
                item = await generate_deepseek_response("", getStoryByRole(role, user_id), item_story_string)
            else:
                item = await generate_gpt_response(GPT_MODEL, getStoryByRole(role, user_id), item_story_string)
        except Exception as e:
            item = f"Failed to generate item description: {e}"
        print(f"Item: {item}")
        # ----- Apply the Outcome Effect -----
        try:
            result_msg = f"You have crafted {item}, Your concoction, with {effect_description}, grants you "
            if bonus == "luck_boost":
                await increase_luck(user_id, value)
                result_msg += f"a luck boost of {value}!"
            elif bonus == "small_currency_bonus":
                await add_bananas(user_id, value)
                result_msg += f"{value} bonus bananas!"
            elif bonus == "big_currency_bonus":
                await add_bananas(user_id, value)
                result_msg += f"a huge bonus of {value} bananas!"
            elif bonus == "cooldown_reduction":
                await apply_cooldown_reduction(user_id, value / 100)
                result_msg += f"a cooldown reduction of {value}%!"
            else:
                result_msg += "an unexpected effect."
            print(result_msg)
        except Exception as e:
            return False, f"Error applying outcome effect: {e}"

        return True, result_msg
