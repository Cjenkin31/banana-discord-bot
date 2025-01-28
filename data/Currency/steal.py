from data.Currency.currency import add_bananas, get_bananas, remove_bananas
from datetime import datetime, timedelta, timezone
from data.stats import get_luck
from firebase_admin import db
import random
import discord
from utils.emoji_helper import BANANA_COIN_EMOJI
from utils.gpt import generate_gpt_response

STEAL_COOLDOWN = timedelta(days=1)
BASE_STEAL_CHANCE = 0.2
LOW_BANANAS_STEAL_CHANCE = 0.05
LUCK_BONUS = 0.1
LUCK_PENALTY = -0.1
BANANA_RATIO = 0.1

async def get_last_steal(user_id):
    ref = db.reference(f'users/{user_id}/last_steal')
    return ref.get()

async def update_last_steal(user_id):
    ref = db.reference(f'users/{user_id}')
    ref.update({'last_steal': datetime.now(timezone.utc).isoformat()})

async def calculate_steal_chance(thief_bananas, target_bananas, thief_luck, target_luck):
    steal_chance = BASE_STEAL_CHANCE if thief_bananas > 0 else LOW_BANANAS_STEAL_CHANCE
    steal_chance += LUCK_BONUS if thief_luck > target_luck else LUCK_PENALTY
    if thief_bananas > target_bananas:
        steal_chance += LUCK_BONUS
    return steal_chance

async def try_steal(thief_id, target_id, thief: discord.User, target: discord.User):
    if thief_id == target_id:
        return False, "You cannot steal from yourself."

    last_steal_str = await get_last_steal(thief_id)
    last_steal = datetime.fromisoformat(last_steal_str) if last_steal_str else None
    now = datetime.now(timezone.utc)

    if last_steal and (now - last_steal < STEAL_COOLDOWN):
        next_attempt_time = (last_steal + STEAL_COOLDOWN) - now
        return False, f"Too soon to steal again. Try again in {next_attempt_time.total_seconds() // 3600} hours."

    target_bananas = await get_bananas(target_id)
    if target_bananas == 0:
        return False, f"{target.mention}, you are safe as you have no bananas to steal. {thief.mention} failed to steal."

    thief_bananas = await get_bananas(thief_id)
    thief_luck = await get_luck(thief_id) or 0
    target_luck = await get_luck(target_id) or 0

    max_steal_amount = int(target_bananas * BANANA_RATIO)
    steal_chance = await calculate_steal_chance(thief_bananas, target_bananas, thief_luck, target_luck)

    stolen_amount = random.randint(1, max_steal_amount)

    if random.random() < steal_chance:
        await add_bananas(thief_id, stolen_amount)
        await remove_bananas(target_id, stolen_amount)
        await update_last_steal(thief_id)
        story = (
            "You are a Narrator making whacky and interesting turn around stories about how people steal money in the funniest ways possible. "
            "The story always ends up with the person stealing gaining money. He does it in one line."
        )
        user_input = f"{thief.mention} succeeded in stealing from {target.mention}"
        gpt_response = await generate_gpt_response("gpt-3.5-turbo", story, user_input)
        gpt_response += f"\n +{stolen_amount} {BANANA_COIN_EMOJI}"
        return True, gpt_response
    else:
        penalty_amount = stolen_amount
        penalty = min(thief_bananas, penalty_amount)
        await remove_bananas(thief_id, penalty)
        await add_bananas(target_id, penalty)
        await update_last_steal(thief_id)
        story = (
            "You are a Narrator making whacky and interesting turn around stories about how people fail stealing in the funniest ways possible. "
            "The story always ends up with the person stealing losing the money and the target receiving it, as in they gain extra money that they would have lost. "
            "He does it in one line. He never mentions how much was gained or lost."
        )
        user_input = f"{thief.mention} failed in stealing from {target.mention}"
        gpt_response = await generate_gpt_response("gpt-3.5-turbo", story, user_input)
        gpt_response += f"\n -{penalty} {BANANA_COIN_EMOJI}"
        return False, gpt_response