from data.pets import RandomCatAPIPet, RandomPet
from utils.image_helpers import download_image
import discord
from discord.ext import commands
from discord import app_commands
import os
import random

def ChooseLocalOrApi():
    if ( random.random() >= .5 ):
        return RandomPet()
    return RandomCatAPIPet()

async def SendCatImage(interaction, file_url, name, sent_message):
    image = download_image(file_url)
    if image:
        file_path = download_image(image, 'temp_image.jpg')
        discord_file = discord.File(file_path, filename='image.jpg')
        await interaction.response.send_message(sent_message, file=discord_file)
        os.remove(file_path)
    else:
        await interaction.response.send_message('Sorry, I could not fetch the image.')

def define_random_pet_command(tree,servers):
    @tree.command(name="randompet", description="Random pet picture from friends!", guilds=servers) 
    async def random_pet(interaction):
        # Fetch the image from GitHub/cataas
        file_url, name = ChooseLocalOrApi()
        sent_message = f'Sure! Here\'s a random picture from {name}!'
        await SendCatImage(interaction, file_url, name, sent_message)