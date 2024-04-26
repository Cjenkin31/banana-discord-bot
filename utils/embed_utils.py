import discord

def create_embed_message(message):
    embed = discord.Embed(description=message.content, color=0x00ff00)
    embed.add_field(name="Link", value=f"[Go To Message]({message.jump_url})")
    embed.set_author(name=message.author.display_name, icon_url=message.author.avatar.url)
    embed.timestamp = message.created_at
    if message.attachments:
        embed.set_image(url=message.attachments[0].url)
    return embed
