# data/firebase_activity.py

from firebase_admin import db

def add_time_spent(user_id: int, guild_id: int, minutes: int):
    """
    Increments the total minutes this user has spent in voice for this guild.
    """
    ref = db.reference(f'users/{user_id}/time_spent/{guild_id}')
    current = ref.get() or 0
    ref.set(current + minutes)

def get_time_spent(user_id: int, guild_id: int) -> int:
    """
    Returns the total minutes this user has spent in voice for this guild.
    """
    ref = db.reference(f'users/{user_id}/time_spent/{guild_id}')
    return ref.get() or 0

def increment_message_count(user_id: int, guild_id: int):
    """
    Increments this user’s message count for that guild.
    """
    ref = db.reference(f'users/{user_id}/messages_sent/{guild_id}')
    current = ref.get() or 0
    ref.set(current + 1)

def get_message_count(user_id: int, guild_id: int) -> int:
    """
    Returns how many messages this user has sent in that guild.
    """
    ref = db.reference(f'users/{user_id}/messages_sent/{guild_id}')
    return ref.get() or 0
