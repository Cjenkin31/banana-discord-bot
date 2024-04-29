from data.currency import add_bananas, get_bananas, remove_bananas
from datetime import datetime, timedelta, timezone
from firebase_admin import credentials, db
import random
import config.firebase_config
from discord.ext import commands
from discord import app_commands
import discord

async def get_last_steal(user_id):
    ref = db.reference(f'users/{user_id}/last_steal')
    return ref.get()

async def update_last_steal(user_id):
    ref = db.reference(f'users/{user_id}')
    ref.update({'last_steal': datetime.now(timezone.utc).isoformat()})

async def try_steal(thief_id, target_id, thief: discord.User, target: discord.User):
    if thief_id == target_id:
        return False, "You cannot steal from yourself."

    last_steal_str = await get_last_steal(thief_id)
    last_steal = datetime.fromisoformat(last_steal_str) if last_steal_str else None
    now = datetime.now(timezone.utc)

    if last_steal and (now - last_steal < timedelta(days=1)):
        next_attempt_time = (last_steal + timedelta(days=1)) - now
        return False, f"Too soon to steal again. Try again in {next_attempt_time.total_seconds() // 3600} hours."

    target_bananas = await get_bananas(target_id)
    if target_bananas == 0:
        return False, f"{target.mention}, you are safe as you have no bananas to steal. {thief.mention} failed to steal."

    thief_bananas = await get_bananas(thief_id)
    max_steal_amount = int(target_bananas * 0.1)
    steal_chance = 0.2

    if thief_bananas < target_bananas:
        steal_chance += 0.1

    if random.random() < steal_chance:
        stolen_amount = random.randint(1, max_steal_amount)
        await add_bananas(thief_id, stolen_amount)
        await remove_bananas(target_id, stolen_amount)
        await update_last_steal(thief_id)
        return True, f"{target.mention}, {thief.mention} successfully stole {stolen_amount} bananas from you."
    else:
        penalty_amount = stolen_amount = random.randint(1, max_steal_amount)
        await remove_bananas(thief_id, penalty_amount)
        await update_last_steal(thief_id)
        return False, f"{thief.mention}, your attempt to steal from {target.mention} failed. You lost {penalty_amount} bananas as a penalty."
