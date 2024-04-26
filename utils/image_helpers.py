from PIL import Image
import requests
from io import BytesIO

def download_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        return img
    return None

def resize_image(image, size):
    return image.resize(size, Image.ANTIALIAS)