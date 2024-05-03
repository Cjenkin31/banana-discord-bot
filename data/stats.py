import firebase_admin
from firebase_admin import db
from functools import lru_cache
import random
import math

@lru_cache(maxsize=128)
def get_stats_sync(user_id):
    ref = db.reference(f'users/{user_id}/stats')
    return ref.get() or {}

async def get_stats(user_id):
    return get_stats_sync(user_id)

async def get_luck(user_id):
    stats = await get_stats(user_id)
    return stats.get('luck', 0)

async def increase_luck(user_id, amt=1):
    ref = db.reference(f'users/{user_id}/stats')
    current_stats = await get_stats(user_id)
    current_luck = current_stats.get('luck', 0)
    current_stats['luck'] = current_luck + amt
    ref.update(current_stats)
    get_stats_sync.cache_clear()

async def random_luck(user_id, currency_amount):
    if currency_amount < 1:
        return 0
    max_luck = min(100, int(5 * math.log(currency_amount, 10) ** 2))
    min_luck = max(0, max_luck - 40)

    luck_to_add = random.randint(min_luck, max_luck)
    
    await increase_luck(user_id, amt=luck_to_add)

    return luck_to_add

async def set_luck(user_id, luck):
    ref = db.reference(f'users/{user_id}/stats')
    try:
        ref.update({'luck': luck})
        get_stats_sync.cache_clear()
    except Exception as e:
        print(f"Failed to set luck: {e}")