from config.config import FIREBASE_SERVICE_ACCOUNT
import firebase_admin
from firebase_admin import credentials
import os
import json

def initialize_firebase():
    if not firebase_admin._apps:
        service_account_info = json.loads(FIREBASE_SERVICE_ACCOUNT)
        cred = credentials.Certificate(service_account_info)
        firebase_admin.initialize_app(cred, {
            'databaseURL': os.getenv("FIREBASE_DATABASE_URL")
        })