import os
import json
import firebase_admin
from firebase_admin import credentials, db
import config.firebase_config

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
    ref.update({'bananas': new_bananas})


async def get_leaderboard():
    ref = db.reference('users/')
    all_users = ref.get()
    leaderboard = sorted(
        ((user_id, user_data.get('bananas', 0)) for user_id, user_data in all_users.items() if 'bananas' in user_data),
        key=lambda x: x[1], reverse=True
    )
    return leaderboard
