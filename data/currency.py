import os
import json
import firebase_admin
from firebase_admin import credentials, db

service_account_info = json.loads(os.getenv('FIREBASE_SERVICE_ACCOUNT'))

cred = credentials.Certificate(service_account_info)
firebase_admin.initialize_app(cred, {
    'databaseURL': os.getenv("FIREBASE_DATABASE_URL")
})

async def get_bananas(user_id):
    ref = db.reference(f'users/{user_id}/bananas')
    return ref.get() or 0

async def add_bananas(user_id, amount):
    ref = db.reference(f'users/{user_id}')
    current_bananas = await get_bananas(user_id)
    ref.update({'bananas': current_bananas + amount})

def update_bananas(user_id, amount):
    ref = db.reference(f'users/{user_id}')
    current_bananas = get_bananas(user_id)
    ref.update({'bananas': current_bananas + amount})