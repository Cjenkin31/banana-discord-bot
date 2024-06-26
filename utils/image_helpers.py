from PIL import Image
import requests
from io import BytesIO
import discord
import os
from discord import File
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
        discord_file = File(image_path, filename='image.jpg')
        os.remove(image_path)
        return discord_file
    else:
        return None

async def download_gif_from_github(path: str):
    base_url = "https://raw.githubusercontent.com/Cjenkin31/banana-discord-bot/main/images/"
    corrected_path = path.lstrip('/')
    full_url = f"{base_url}{corrected_path}"
    try:
        response = requests.get(full_url, stream=True)
        if response.status_code == 200:
            local_filename = 'temp_image.gif'
            with open(local_filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)

            discord_file = File(local_filename, filename='image.gif')
            os.remove(local_filename)
            return discord_file

        else:
            return None
    except Exception as e:
        print(f"An error occurred in download_gif_from_github: {e}")
        return None