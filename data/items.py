from firebase_admin import db
from functools import lru_cache

@lru_cache(maxsize=128)
def get_inventory_sync(user_id):
    ref = db.reference(f'users/{user_id}/inventory')
    return ref.get() or {}

async def get_inventory(user_id):
    return get_inventory_sync(user_id)

async def add_item(user_id, item_name):
    ref = db.reference(f'users/{user_id}/inventory')
    current_inventory = await get_inventory(user_id)
    current_inventory[item_name] = current_inventory.get(item_name, 0) + 1
    ref.update(current_inventory)
    get_inventory_sync.cache_clear()
