from data.currency import add_bananas, get_bananas
import firebase_admin
import os
import json
from firebase_admin import credentials, db
from datetime import datetime, timedelta, timezone
import random
import config.firebase_config


async def get_last_daily(user_id):
    ref = db.reference(f'users/{user_id}/last_daily')
    return ref.get()

async def update_last_daily(user_id):
    ref = db.reference(f'users/{user_id}')
    ref.update({'last_daily': datetime.now(timezone.utc).isoformat()})

async def try_collect_daily(user_id):
    try:
        last_daily_str = await get_last_daily(user_id)
        last_daily = datetime.fromisoformat(last_daily_str) if last_daily_str else None
        now = datetime.now(timezone.utc)
        
        if last_daily and (now - last_daily < timedelta(days=1)):
            return False, (last_daily + timedelta(days=1)) - now
        
        bananas_to_add = random.randint(1, 100)
        current_bananas = await get_bananas(user_id)
        await add_bananas(user_id, bananas_to_add)
        await update_last_daily(user_id)
        return True, bananas_to_add
    except Exception as e:
        print(f"Error while collecting daily bananas: {e}")
        return None, "An error occurred. Please try again later."
