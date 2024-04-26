import discord
from discord.ext import commands
from discord import app_commands
import requests
from cachetools import TTLCache

async def define_overwatch_player_details_command(tree, servers):
    # Setup cache with TTL of 1 hour (3600 seconds)
    cache = TTLCache(maxsize=100, ttl=3600)

    def fetch_player_profile(player_id):
        """Fetch player profile from API with caching."""
        if player_id in cache:
            return cache[player_id]

        url = f'https://overfast-api.tekrop.fr/players/{player_id}/summary'
        response = requests.get(url)
        if response.status_code == 200:
            profile_data = response.json()
            cache[player_id] = profile_data  # Cache the response
            return profile_data
        else:
            return None

    def fetch_player_stats(player_id):
        """Fetch player stats from API."""
        url = f'https://overfast-api.tekrop.fr/players/{player_id}/stats/summary'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    @tree.command(name="overwatchplayerdetails", description="Fetches detailed player information including profile and stats.", guilds=servers)
    async def player_details(interaction: discord.Interaction, player_id: str):
        await interaction.response.defer()
        sanitized_player_id = player_id.replace('#', '-')

        # Fetch player profile and stats
        player_profile = fetch_player_profile(sanitized_player_id)
        player_stats = fetch_player_stats(sanitized_player_id)
        
        if player_profile and player_stats:
            tier_values = {
                'Bronze': 1, 'Silver': 2, 'Gold': 3, 'Platinum': 4, 
                'Diamond': 5, 'Master': 6, 'Grandmaster': 7, 'Champions': 8, 'Top 500': 9
            }
            
            competitive = player_profile.get('competitive', {})
            pc_competitive = competitive.get('pc', {})
            highest_tier = 0
            primary_role = ''
            
            # Determine highest tier role
            for role, details in pc_competitive.items():
                if role == 'season':
                    continue
                if isinstance(details, dict):
                    current_tier = tier_values.get(details.get('division', ''), 0) * 5 + int(details.get('tier', 5))  # Using 5 as default for division
                    if current_tier > highest_tier:
                        highest_tier = current_tier
                        primary_role = role

            # Embed construction
            embed = discord.Embed(title=f"{player_profile['username']}'s Profile", description=f"*{player_profile['title']}*", color=0x00ff00)
            embed.set_image(url=player_profile['namecard'])

            if primary_role:
                details = pc_competitive[primary_role]
                rank_icon = details.get('rank_icon', '')
                embed.set_thumbnail(url=rank_icon)
                division = details.get('division', 'N/A').capitalize()
                tier = details.get('tier', 'N/A')
                embed.add_field(name=f"{primary_role.capitalize()} Role", value=f"Division: {division} - Tier: {tier}", inline=False)

            for role, details in pc_competitive.items():
                if role == primary_role or role == 'season':
                    continue
                if isinstance(details, dict):
                    division = details.get('division', 'N/A').capitalize()
                    tier = details.get('tier', 'N/A')
                    embed.add_field(name=f"{role.capitalize()} Role", value=f"Division: {division} - Tier: {tier}", inline=False)

            # Embed for stats information
            stats_message = f"**Games Played:** {player_stats['general']['games_played']}\n"
            stats_message += f"**Games Won:** {player_stats['general']['games_won']}\n"
            stats_message += f"**Games Lost:** {player_stats['general']['games_lost']}\n"
            stats_message += f"**KDA:** {player_stats['general']['kda']}\n"
            stats_message += f"**Time Played:** {player_stats['general']['time_played'] / 3600:.2f} hours\n"
            stats_message += f"**Winrate:** {player_stats['general']['winrate']}%"
            
            embed.add_field(name="General Stats", value=stats_message, inline=False)
            
            await interaction.followup.send(embed=embed)