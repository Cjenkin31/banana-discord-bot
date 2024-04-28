from PIL import Image
import requests
from io import BytesIO
import discord
import os

def download_image(url, local_filename):
    images_directory = 'images'
    response = requests.get(url)
    if not os.path.exists(images_directory):
        os.makedirs(images_directory)
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        img_path = os.path.join(images_directory, local_filename)
        img.save(img_path)
        return img_path
    return None

def resize_image(image, size):
    return image.resize(size, Image.ANTIALIAS)


async def download_from_github(path: str):
    base_url = "https://raw.githubusercontent.com/Cjenkin31/banana-discord-bot/main/images/"
    corrected_path = path.lstrip('/')
    full_url = f"{base_url}{corrected_path}"

    local_filename = 'temp_image.jpg'
    image_path = download_image(full_url, local_filename)
    
    if image_path:
        discord_file = discord.File(image_path, filename='image.jpg')
        os.remove(image_path)
        return discord_file
    else:
        return None
