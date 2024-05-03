BANANA_COIN_EMOJI_ID = "1234155554167849131"
BANANA_COIN_EMOJI_NAME = "bananacoin"
SLOT_EMOJI_1_ID = "1235798526689017899"
SLOT_EMOJI_2_ID = "1235799131327565854"
SLOT_EMOJI_3_ID = "1235799773190291498"

SLOT_EMOJI_1_NAME = "slots"
SLOT_EMOJI_2_NAME = "slots2"
SLOT_EMOJI_3_NAME = "slots3"

SLOT_MACHINE_NAME = "Slots"
SLOT_MACHINE_ID = "1153710427625246760"
# Function to return the full emoji format
def get_custom_emoji(name, id):
    return f"<:{name}:{id}>"

def get_custom_animated_emoji(name, id):
    return f"<a:{name}:{id}>"



BANANA_COIN_EMOJI = get_custom_emoji(BANANA_COIN_EMOJI_NAME, BANANA_COIN_EMOJI_ID)
SLOT_ROW_1_EMOJI = get_custom_animated_emoji(SLOT_EMOJI_1_NAME,SLOT_EMOJI_1_ID)
SLOT_ROW_2_EMOJI = get_custom_animated_emoji(SLOT_EMOJI_2_NAME,SLOT_EMOJI_2_ID)
SLOT_ROW_3_EMOJI  = get_custom_animated_emoji(SLOT_EMOJI_3_NAME,SLOT_EMOJI_3_ID)
SLOT_EMOJI = get_custom_emoji(SLOT_MACHINE_NAME, SLOT_MACHINE_ID)