import os
import json
import firebase_admin
from firebase_admin import credentials, db
import config.firebase_config
from functools import lru_cache

@lru_cache(maxsize=128)
def get_name_sync(user_id):
    ref = db.reference(f'users/{user_id}/user_name')
    return ref.get() or "Unknown User"

async def get_name(user_id):
    return get_name_sync(user_id)

async def add_name_if_not_exist_to_database(user_id, name):
    ref = db.reference(f'users/{user_id}')
    user_name_ref = ref.child('user_name')
    user_name = user_name_ref.get()
    if not user_name:
        user_name_ref.set(name)
        get_name(user_id).cache_clear()