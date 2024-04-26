import discord

async def is_admin(interaction: discord.Interaction) -> bool:
    return interaction.user.guild_permissions.administrator