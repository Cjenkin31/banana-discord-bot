from datetime import datetime, timedelta, timezone
from firebase_admin import db
from config.firebase_config import initialize_firebase

initialize_firebase()

COOLDOWN_PERIODS = {
    "daily": timedelta(days=1),
    "weekly": timedelta(days=7),
    "steal": timedelta(days=1)
}

async def apply_cooldown_reduction(user_id: str, reduction_percentage: float):
    """
    Apply a cooldown reduction effect for the given user.
    This function updates the 'last_*' timestamps so that any active cooldown is reduced.

    Parameters:
      user_id: The Discord user ID.
      reduction_percentage: A float between 0 and 1 representing the fraction by which
                            to reduce the remaining cooldown (e.g. 0.2 for 20% reduction).

    Returns:
      A dict of updated cooldown timestamps for debugging purposes.
    """
    now = datetime.now(timezone.utc)
    user_ref = db.reference(f'users/{user_id}')
    updates = {}

    for cooldown, period in COOLDOWN_PERIODS.items():
        key = f"last_{cooldown}"
        last_time_str = db.reference(f'users/{user_id}/{key}').get()
        if last_time_str is None:
            continue
        try:
            last_time = datetime.fromisoformat(last_time_str)
        except Exception:
            continue

        elapsed = now - last_time

        if elapsed >= period:
            continue

        remaining = period - elapsed
        new_remaining = remaining * (1 - reduction_percentage)

        new_last = now - (period - new_remaining)
        updates[key] = new_last.isoformat()

    if updates:
        user_ref.update(updates)

    return updates
