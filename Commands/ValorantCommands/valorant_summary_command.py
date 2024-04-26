import discord
from discord.ext import commands
from discord import app_commands
from utils.api_requests import make_api_get_request

async def define_valorant_summary_command(tree, servers):
    @tree.command(name="valorant_summary", description="Provides a performance summary of the last few games.", guilds=servers)
    async def valorant_summary(interaction: discord.Interaction, name: str, tag: str, region: str = "na"):
        await interaction.response.defer()
        url = f"https://api.henrikdev.xyz/valorant/v3/matches/{region}/{name}/{tag}"
        data = make_api_get_request(url)
        if data:
            matches = data['data'][:5]  # Analyze the last 5 matches
            total_kills = sum([p['stats']['kills'] for match in matches for p in match['players']['all_players'] if p['name'].lower() == name.lower() and p['tag'].lower() == tag.lower()])
            total_deaths = sum([p['stats']['deaths'] for match in matches for p in match['players']['all_players'] if p['name'].lower() == name.lower() and p['tag'].lower() == tag.lower()])
            kda = total_kills / total_deaths if total_deaths > 0 else total_kills
            embed = discord.Embed(title=f"Performance Summary for {name}#{tag}", description=f"Total Kills: {total_kills}\nTotal Deaths: {total_deaths}\nKDA: {kda:.2f}", color=0x00ff00)
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("Failed to fetch performance data. Please check the player name, tag, and region.")
