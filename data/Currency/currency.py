from firebase_admin import db
from config.firebase_config import initialize_firebase

initialize_firebase()
async def get_bananas(user_id):
    ref = db.reference(f'users/{user_id}/bananas')
    return ref.get() or 0

async def add_bananas(user_id, amount):
    ref = db.reference(f'users/{user_id}')
    current_bananas = await get_bananas(user_id)
    new_bananas = current_bananas + amount
    ref.update({'bananas': new_bananas})

async def remove_bananas(user_id, amount):
    ref = db.reference(f'users/{user_id}')
    current_bananas = await get_bananas(user_id)
    new_bananas = max(0, current_bananas - amount)
    if current_bananas - amount < 0:
        await set_debt(user_id, amount - current_bananas)
    ref.update({'bananas': new_bananas})
    return new_bananas >= 0

async def get_leaderboard():
    ref = db.reference('users/')
    all_users = ref.get()
    leaderboard = sorted(
        ((user_id, user_data.get('bananas', 0)) for user_id, user_data in all_users.items() if 'bananas' in user_data),
        key=lambda x: x[1], reverse=True
    )
    return leaderboard

async def get_debt_leaderboard():
    ref = db.reference('users/')
    all_users = ref.get()
    leaderboard = sorted(
        ((user_id, user_data.get('debt', 0)) for user_id, user_data in all_users.items() if 'debt' in user_data),
        key=lambda x: x[1], reverse=True
    )
    return leaderboard

async def set_debt(user_id, amount):
    ref = db.reference(f'users/{user_id}')
    ref.update({'debt': amount})