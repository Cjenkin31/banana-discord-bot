import json
import os
import random

def load_fish_data(filepath="fish_data.json"):
    script_dir = os.path.dirname(__file__)
    file_path = os.path.join(script_dir, filepath)
    with open(file_path, "r", encoding="utf-8") as file:
        fish_data = json.load(file)
    return fish_data

def select_fish_by_rarity(fish_data):
    rarity_weights = {
        "S": 1,
        "A": 5,
        "B": 10,
        "C": 20,
        "D": 30,
        "F": 40
    }
    fish_pool = []
    for fish in fish_data:
        fish_pool.extend([fish] * rarity_weights[fish["rarity"]])
    selected_fish = random.choice(fish_pool)
    return selected_fish