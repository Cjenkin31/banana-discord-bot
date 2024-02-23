from pymongo import MongoClient
import os

mongo_client = MongoClient(os.environ.get("MONGODB_URI"))
db = mongo_client.bananabread
roles_collection = db.roles

def add_role_to_server(guild_id, role_name):
    """Add a role to the server's list of selectable roles."""
    db.roles.update_one(
        {"guild_id": str(guild_id)},
        {"$addToSet": {"roles": role_name}},
        upsert=True
    )

def remove_role_from_server(guild_id, role_name):
    """Remove a role from the server's list of selectable roles."""
    db.roles.update_one(
        {"guild_id": str(guild_id)},
        {"$pull": {"roles": role_name}}
    )

def get_server_roles(guild_id):
    """Get the list of selectable roles for a server."""
    server_data = db.roles.find_one({"guild_id": str(guild_id)})
    if server_data:
        return server_data.get("roles", [])
    return []

def update_roles_message_id(guild_id, message_id):
    """Update the message ID of the roles message for a server."""
    db.roles.update_one(
        {"guild_id": str(guild_id)},
        {"$set": {"message_id": str(message_id)}}
    )

def get_roles_message_id(guild_id):
    """Get the message ID of the roles message for a server."""
    server_data = db.roles.find_one({"guild_id": str(guild_id)})
    if server_data:
        return server_data.get("message_id")
    return None
