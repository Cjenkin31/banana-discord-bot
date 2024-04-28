from data.currency import add_bananas, get_bananas
import firebase_admin
import os
import json
from firebase_admin import credentials, db
from datetime import datetime, timedelta, timezone
import random
import config.firebase_config


async def get_last_weekly(user_id):
    ref = db.reference(f'users/{user_id}/last_weekly')
    return ref.get()

async def update_last_weekly(user_id):
    ref = db.reference(f'users/{user_id}')
    ref.update({'last_weekly': datetime.now(timezone.utc).isoformat()})

async def try_collect_weekly(user_id):
    try:
        last_weekly_str = await get_last_weekly(user_id)
        last_weekly = datetime.fromisoformat(last_weekly_str) if last_weekly_str else None
        now = datetime.now(timezone.utc)
        
        if last_weekly and (now - last_weekly >= timedelta(days=7)):
            bananas_to_add = random.randint(1, 1000)
            await add_bananas(user_id, bananas_to_add)
            await update_last_weekly(user_id)
            return True, bananas_to_add
        else:
            if last_weekly:
                time_left = last_weekly + timedelta(days=7) - now
                return False, time_left
            else:
                bananas_to_add = random.randint(1, 1000)
                await add_bananas(user_id, bananas_to_add)
                await update_last_weekly(user_id)
                return True, bananas_to_add
    except Exception as e:
        print(f"Error while collecting weekly bananas: {e}")
        return None, "An error occurred. Please try again later."

