from firebase_admin import db
from functools import lru_cache

@lru_cache(maxsize=128)
def get_nickname_sync(user_id):
    ref = db.reference(f'users/{user_id}/nickname')
    return ref.get() or {}

async def get_nickname(user_id):
    return get_nickname_sync(user_id)

async def set_nickname(user_id, nickname):
    ref = db.reference(f'users/{user_id}')
    ref.set({'nickname': nickname})
    get_nickname_sync.cache_clear()
    return nickname

async def remove_nickname(user_id):
    ref = db.reference(f'users/{user_id}/nickname')
    ref.delete()
    get_nickname_sync.cache_clear()