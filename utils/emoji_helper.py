# Define your custom emojis as constants
BANANA_COIN_EMOJI_ID = "1234155554167849131"
BANANA_COIN_EMOJI_NAME = "bananacoin"

# Function to return the full emoji format
def get_custom_emoji(name, id):
    return f"<:{name}:{id}>"

BANANA_COIN_EMOJI = get_custom_emoji(BANANA_COIN_EMOJI_NAME, BANANA_COIN_EMOJI_ID)
