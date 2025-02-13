from firebase_admin import db
from config.firebase_config import initialize_firebase

initialize_firebase()

async def get_inventory(user_id):
    ref = db.reference(f'users/{user_id}/inventory')
    return ref.get() or {}

async def add_item(user_id, item_name):
    ref = db.reference(f'users/{user_id}/inventory')
    current_inventory = await get_inventory(user_id)
    current_inventory[item_name] = current_inventory.get(item_name, 0) + 1
    ref.update(current_inventory)

async def remove_item(user_id, item_name, amount=1):
    ref = db.reference(f'users/{user_id}/inventory')
    current_inventory = await get_inventory(user_id)
    if current_inventory.get(item_name, 0) >= amount:
        current_inventory[item_name] -= amount
        if current_inventory[item_name] == 0:
            del current_inventory[item_name]
        if current_inventory == {}:
            ref.delete()
        else:
            ref.update(current_inventory)
        print(f"Removed {amount} {item_name} from {user_id}'s inventory.")
        print(f"New inventory: {current_inventory}")
        return True
    return False