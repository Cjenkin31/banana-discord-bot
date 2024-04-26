import discord
from discord.ext import commands
from discord import app_commands
from pick_from_list_command import *
from rhythm_roll_command import *
from random_pet_command import *
from random_number_command import *
def define_all_random_commands(tree, servers):
    define_pick_from_list_command(tree, servers)
    define_random_number_command(tree, servers)
    define_random_pet_command(tree, servers)
    define_rhythm_roll_command(tree, servers)