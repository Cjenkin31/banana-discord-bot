from firebase_admin import db
from datetime import datetime, timedelta, timezone
from config.firebase_config import initialize_firebase

initialize_firebase()
async def get_gacha_reset(user_id):
    ref = db.reference(f'users/{user_id}/last_gacha_reset')
    return ref.get()

async def update_last_gacha_reset(user_id):
    ref = db.reference(f'users/{user_id}')
    ref.update({'last_gacha_reset': datetime.now(timezone.utc).isoformat()})

async def try_gacha(amount, user_id):
    """
    Attempts to perform a gacha spin for the given user.

    The user is allowed up to 100 gacha spins in any 24-hour period.
    If the user's last gacha reset was more than 24 hours ago, the attempt count is reset.

    :param amount: The number of gacha spins requested.
    :param user_id: The Discord user ID.
    :return: (bool, message) - success flag and a message.
    """
    now = datetime.now(timezone.utc)
    last_reset_str = await get_gacha_reset(user_id)
    attempts_ref = db.reference(f'users/{user_id}/gacha_attempts')
    current_attempts = attempts_ref.get() or 0

    # Check if we need to reset the gacha attempts.
    if last_reset_str is None:
        # No reset timestamp exists—initialize it.
        await update_last_gacha_reset(user_id)
        current_attempts = 0
        attempts_ref.set(0)
    else:
        try:
            last_reset = datetime.fromisoformat(last_reset_str)
        except Exception:
            last_reset = None

        # If 24 hours have passed since the last reset, then reset the attempts.
        if last_reset is None or now - last_reset >= timedelta(hours=24):
            current_attempts = 0
            await update_last_gacha_reset(user_id)
            attempts_ref.set(0)

    # Check if adding the requested amount exceeds the daily limit.
    print(f"Current attempts: {current_attempts}, Requested amount: {amount}")
    if current_attempts >= 100:
        return False, "You have reached the maximum of 100 gacha attempts in a 24-hour period. Please wait until your attempts reset."
    if current_attempts + amount > 100:
        return False, f"You cannot exceed 100 gacha attempts in a 24-hour period. Spin attempts Left: {100 - current_attempts}"

    new_attempts = current_attempts + amount
    attempts_ref.set(new_attempts)

    return True, f"Gacha attempt allowed. You have used {new_attempts}/100 attempts today."

