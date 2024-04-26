import discord
from discord.ext import commands
from discord import app_commands
from utils.api_requests import make_api_get_request

async def define_valorant_matches_command(tree, servers):   
    @tree.command(name="valorant_matches", description="Fetches last 3 Valorant matches.", guilds=servers)
    async def valorant_matches(interaction: discord.Interaction, name: str, tag: str, region: str = "na"):
        await interaction.response.defer()
        url = f"https://api.henrikdev.xyz/valorant/v3/matches/{region}/{name}/{tag}"
        data = make_api_get_request(url)
        if data:
            matches = data['data'][:3]  # Get only the last 3 matches
            embed = discord.Embed(title=f"Last 3 Matches for {name}#{tag}", color=0x00ff00)
            for match in matches:
                map_name = match['metadata']['map']
                mode = match['metadata']['mode']
                score = ", ".join([f"{p['name']}#{p['tag']} - {p['stats']['score']} points" for p in match['players']['all_players'][:5]])  # Display top 5 scorers
                embed.add_field(name=f"{map_name} ({mode})", value=score, inline=False)
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("Failed to fetch match history. Please check the player name, tag, and region.")
