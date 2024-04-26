import discord
from discord.ext import commands
from discord import app_commands
import requests
from utils.api_requests import make_api_get_request

async def define_valorant_account_command(tree, servers):
    @tree.command(name="valorant_account", description="Fetches Valorant account details.", guilds=servers)
    async def valorant_account(interaction: discord.Interaction, name: str, tag: str):
        await interaction.response.defer()
        url = f"https://api.henrikdev.xyz/valorant/v1/account/{name}/{tag}"
        data = make_api_get_request(url)
        if data:
            embed = discord.Embed(title=f"{data['name']}'s Valorant Profile", description=f"Tag: {data['tag']}\nLevel: {data['account_level']}", color=0x00ff00)
            embed.set_thumbnail(url=data['card']['large'])
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("Failed to fetch Valorant account details. Please check the player name and tag.")