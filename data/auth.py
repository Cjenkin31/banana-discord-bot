from firebase_admin import db
from functools import lru_cache
from config.firebase_config import initialize_firebase

initialize_firebase()

@lru_cache(maxsize=128)
def get_auth_token_sync(user_id):
    ref = db.reference(f'users/{user_id}/auth_token')
    return ref.get() or None

async def get_auth_token(user_id):
    return get_auth_token_sync(user_id)

async def set_auth_token(user_id, new_token):
    try:
        ref = db.reference(f'users/{user_id}')
        auth_ref = ref.child('auth_token')
        auth_token = auth_ref.get()
        if not auth_token:
            auth_ref.set(new_token)
            get_auth_token_sync.cache_clear()
        return True
    except:
        return False