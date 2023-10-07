import random
import requests

def GetDictPets():
    base_url = "https://raw.githubusercontent.com/Cjenkin31/banana-discord-bot/main/images/"
    return { f"{base_url}/IMG_6913.jpg":"Amber", f"{base_url}/IMG_6903.jpg":"Amber", f"{base_url}/IMG_6895.png":"Amber", f"{base_url}/IMG_6839.png":"Amber", f"{base_url}/IMG_6781.jpg":"Amber",f"{base_url}/Polish_20230808_163228438.jpg":"Jake",f"{base_url}/IMG_6721-1.png":"Amber",f"{base_url}/IMG_6306.jpg":"Amber",f"{base_url}/IMG_6195.jpg":"Kaylie",f"{base_url}/IMG_5781.jpg":"Amber",f"{base_url}/IMG_2839.jpg":"Donovan",f"{base_url}/IMG_2838.jpg":"Donovan",f"{base_url}/IMG_5587.jpg":"Amber",f"{base_url}/43CE5474-E5E3-42BC-BF89-A0A6CC034C88.jpg":"Jeremy",f"{base_url}/1B9ABD25-F1B6-4956-B08B-9D74438C7390.jpg":"Jeremy",f"{base_url}/Attachment.jpg":"Amber",f"{base_url}/20230527_170343.jpg":"Chris",f"{base_url}/IMG_5155.jpg":"Amber",f"{base_url}/image0.jpg":"JP",f"{base_url}/19B73A22-6D9E-4CFD-85EF-FDE6D13A936F.jpg":"Jeremy",f"{base_url}/6259240B-B2C4-4DCC-B285-7AE9DDEE3C9B.jpg":"Jeremy",f"{base_url}/3DE72052-988A-4B42-B5FA-9E506B72C079.jpg":"Jeremy",f"{base_url}/D4C2A3E2-847D-4CD4-A70B-0F81966E6A75.jpg":"Jeremy",f"{base_url}/IMG_5072.png":"Amber",f"{base_url}/6FBA885E-E8F9-45DB-8244-923EFE3FB09F.jpg":"Amber",f"{base_url}/IMG_5070.png":"Amber",f"{base_url}/EA245A40-EA03-420E-B4C4-3449F80F250A.jpg":"Amber",f"{base_url}/47E3C3F4-BD43-4D6F-93F8-0E68EA2B496B.jpg":"Amber",f"{base_url}/IMG_5056.png":"Amber",f"{base_url}/IMG_2808.jpg":"Donovan",f"{base_url}/70328765316__A71D91FD-0A7C-4816-9643-5891BBFFBF4D.jpg":"Donovan",f"{base_url}/70328776443__83F26C35-98EB-4B69-BF9A-B88CE6739387.jpg":"Donovan",f"{base_url}/0870272E-E771-424B-BF88-F6CBFD8C54C1.jpg":"Amber",f"{base_url}/3AD7DD97-04EA-44CC-810E-1C099F6EE8CC.jpg":"Kaylie",f"{base_url}/05EF7D7A-BAE7-4A58-B1AA-782E9B8A2A1F.jpg":"Jeremy",f"{base_url}/IMG_3007.jpg":"Jeremy", f"{base_url}/IMG_5300.jpeg":"Max", f"{base_url}IMG_3673.jpg":"Evan"}

def RandomPet():
    pets_dict = GetDictPets()
    random_key = random.choice(list(pets_dict.keys()))
    return [random_key, pets_dict[random_key]]

def RandomCatAPIPet():
    response = requests.get('https://cataas.com/cat')
    if response.status_code == 200:
        return ['cataas.com', response.url]
    else:
        print('Failed to retrieve cat image from cataas.com')
        return [None, None]