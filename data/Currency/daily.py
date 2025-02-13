from data.Currency.currency import add_bananas
from data.stats import get_luck
from firebase_admin import db
from datetime import datetime, timedelta, timezone
import random
from config.firebase_config import initialize_firebase
from utils.holidays import HOLIDAYS

initialize_firebase()

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


        base_bananas = random.randint(1, 100)
        user_luck = await get_luck(user_id) or 0
        luck_multiplier = 1 + (user_luck / 100.0)
        bananas_to_add = int(base_bananas * luck_multiplier)

        today_key = (now.month, now.day)
        if today_key in HOLIDAYS:
            holiday = HOLIDAYS[today_key]
            bananas_to_add = int(bananas_to_add * holiday["bonus_multiplier"]) + holiday["bonus_extra"]

        await add_bananas(user_id, bananas_to_add)
        await update_last_daily(user_id)
        return True, bananas_to_add
    except Exception as e:
        print(f"Error while collecting daily bananas: {e}")
        return None, "An error occurred. Please try again later."
