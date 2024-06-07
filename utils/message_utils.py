import discord

DISCORD_MESSAGE_LIMIT = 2000
CHUNK_SIZE = 2000
# Requires the callee to have a deffer interaction response, i.e await interaction.response.defer()
async def send_message_in_chunks(response_string: str, interaction: discord.Interaction):
    if len(response_string) > DISCORD_MESSAGE_LIMIT - 1:
        chunks = [response_string[i:i + CHUNK_SIZE] for i in range(0, len(response_string), CHUNK_SIZE)]
        last_message = None
        for chunk in chunks:
            last_message = await interaction.followup.send(chunk)
        return last_message
    else:
        last_message = await interaction.followup.send(response_string)
        return last_message
