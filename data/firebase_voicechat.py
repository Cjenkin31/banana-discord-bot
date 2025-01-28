from firebase_admin import db
from functools import lru_cache

@lru_cache(maxsize=128)
def get_join_to_create_vc_sync(guild_id):
    ref = db.reference(f'join_to_create_vc/{guild_id}')
    return ref.get()

async def get_join_to_create_vc(guild_id):
    return get_join_to_create_vc_sync(guild_id)

async def set_join_to_create_vc(guild_id, channel_id):
    ref = db.reference(f'join_to_create_vc/{guild_id}')
    ref.set(channel_id)
    get_join_to_create_vc_sync.cache_clear()

async def add_temp_vc(guild_id, channel_id):
    ref = db.reference(f'temp_vcs/{guild_id}/{channel_id}')
    ref.set(True)

async def delete_temp_vc(guild_id, channel_id):
    ref = db.reference(f'temp_vcs/{guild_id}/{channel_id}')
    ref.delete()

async def get_temp_vcs(guild_id):
    ref = db.reference(f'temp_vcs/{guild_id}')
    return ref.get() or {}