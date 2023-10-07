import os
import requests
import discord
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import Bot
from logic import ChooseLocalOrApi
from voicelines import GetVoiceLines
from pets import RandomPet

import random
overwatchHeroTankList = ["D.VA", "Doomfist", "Junkerqueen","Orisa","Reinhardt","Roadhog","Sigma","Winston","Wrecking Ball","Zarya","Ramattra"]
overwatchHeroDPSList = ["Ashe", "Bastion", "Cassidy","Echo","Genji","Hanzo","Junkrat","Mei","Pharah","Reaper","Sojourn","Soldier 76","Sombra(Please Dont)","Symmetra","Torbjorn","Tracer","Widowmaker"]
overwatchHeroSupportList = ["Ana", "Baptiste", "Brigitte","Kiriko","Lucio","Mercy","Moira","Zenyatta"]
overwatchRoleList = ["Tank", "DPS", "Support"]
overwatchGameModeList = ["Competitive", "Quick Play", "Custom Games", "Arcade"]
mainServerId=discord.Object(id=222147212681936896)
sideServerId=discord.Object(id=1101665956314501180)

def DefineAllCommands(tree):
    mainServerId=discord.Object(id=222147212681936896)
    sideServerId=discord.Object(id=1101665956314501180)
    servers = [mainServerId, sideServerId]
    for server in servers:
        @tree.command(name="randomtank", description="rolls a random tank hero from overwatch", guild=server)
        async def first_command(interaction):
            await interaction.response.send_message(random.choice(overwatchHeroTankList))

        @tree.command(name="randomsupport", description="rolls a random support hero from overwatch", guild=server)
        async def first_command(interaction):
            await interaction.response.send_message(random.choice(overwatchHeroSupportList))

        @tree.command(name="randomvoiceline", description="rolls a random voiceline from overwatch", guild=server)
        async def first_command(interaction):
            await interaction.response.send_message(random.choice(overwatchVoiceLines))

        @tree.command(name="randomdps", description="rolls a random support dps from overwatch", guild=server)
        async def first_command(interaction):
            await interaction.response.send_message(random.choice(overwatchHeroDPSList))

        @tree.command(name="randomroleow", description="rolls a random role for overwatch", guild=server)
        async def first_command(interaction):
            await interaction.response.send_message(random.choice(overwatchRoleList))

        @tree.command(name="randomgamemodeow", description="rolls a random game mode for overwatch", guild=server)
        async def first_command(interaction):
            await interaction.response.send_message(random.choice(overwatchGameModeList))

        @tree.command(name = "yesno", description = "picks yes or no", guild=server) 
        async def first_command(interaction):
            await interaction.response.send_message(random.choice(["Yes", "No"]))

        @tree.command(name = "pickfromlist", description = "input things to be chosen seperated by a ,. Ex. Overwatch,League", guild=server) 
        async def self(interaction: discord.Interaction, items: str):
            await interaction.response.send_message(random.choice(items.split(',')))

        @tree.command(name = "sleepygenerator", description = "will give an amt of Z's that are randomly uppercased and lower", guild=server) 
        async def self(interaction: discord.Interaction, items: int):
            itemCount=items
            zString = "" if itemCount<=200 else "Limiting to 200 Z's:   "
            if (itemCount > 200):
                itemCount=200
            while (itemCount>0):
                randomZ="Z" if random.randint(1,2) == 1 else "z"
                zString = zString+randomZ
                itemCount-=1
            await interaction.response.send_message(zString)
    
        @tree.command(name = "randomnumber", description = "Choose a random number between 2 inputs", guild=server) 
        async def self(interaction: discord.Interaction, items: str):
            try:
                await interaction.response.send_message(random.randint(int(items.split(',')[0]),int(items.split(',')[1])))
            except:
                await interaction.response.send_message("Either you messed up or I did. But It was prob you")

        @tree.command(name="rhythmroll", description="rolls number 1-100", guild=server) 
        async def first_command(interaction):
            await interaction.response.send_message(random.randint(0,100))

        @tree.command(name = "randomfullcomp", description = "Rolls 1 tank, 2 dps, 2 supports", guild=server) 
        async def first_command(interaction):
            firstDPS=random.choice(overwatchHeroDPSList)
            secondDPS=random.choice(overwatchHeroDPSList)
            while(firstDPS==secondDPS):
                secondDPS=random.choice(overwatchHeroDPSList)
            
            firstSupport=random.choice(overwatchHeroSupportList)
            secondSupport=random.choice(overwatchHeroSupportList)
            while(firstSupport==secondSupport):
                secondSupport=random.choice(overwatchHeroSupportList)
            
            await interaction.response.send_message("Tank: "+random.choice(overwatchHeroTankList)+"\nDPS: "+firstDPS+", "+secondDPS+"\nSupport: "+firstSupport+", "+secondSupport)
        
        @tree.command(name="randompet", description="Random pet picture from friends!", guild=server) 
        async def random_pet(interaction):
            # Fetch the image from GitHub/cataas
            name,file_url = ChooseLocalOrApi()
            response = requests.get(file_url, stream=True)
            if response.status_code == 200:
                # Create a temporary file to hold the image
                with open('temp_image.jpg', 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                
                # Send the image to Discord
                discord_file = discord.File('temp_image.jpg', filename='image.jpg')
                await interaction.response.send_message(f'Sure! Here\'s a random pet from {name}!', file=discord_file)
                
                os.remove('temp_image.jpg')
            else:
                print(file_url)
                print(name)
                await interaction.response.send_message('Sorry, I could not fetch the image.')



    @tree.command(name = "coinflip", description = "flips a coin") 
    async def self(interaction: discord.Interaction, items: str):
        await interaction.response.send_message(random.choice(["Heads","Tails"]))