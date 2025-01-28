from firebase_admin import db
from functools import lru_cache

@lru_cache(maxsize=128)
def get_announcement_channel_sync(guild_id):
    ref = db.reference(f'announcement_channel/{guild_id}')
    return ref.get()

async def get_announcement_channel(guild_id):
    return get_announcement_channel_sync(guild_id)

async def set_announcement_channel(guild_id, channel_id):
    ref = db.reference(f'announcement_channel/{guild_id}')
    ref.set(channel_id)
    get_announcement_channel_sync.cache_clear()

async def get_all_announcement_channels():
    ref = db.reference('announcement_channel')
    return ref.get() or {}