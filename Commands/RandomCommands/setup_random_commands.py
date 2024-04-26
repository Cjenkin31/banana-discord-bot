import discord
from discord.ext import commands
from discord import app_commands
from Commands.RandomCommands.pick_from_list_command import *
from Commands.RandomCommands.rhythm_roll_command import *
from Commands.RandomCommands.random_pet_command import *
from Commands.RandomCommands.random_number_command import *
def define_all_random_commands(tree, servers):
    define_pick_from_list_command(tree, servers)
    define_random_number_command(tree, servers)
    define_random_pet_command(tree, servers)
    define_rhythm_roll_command(tree, servers)