from data.saved_messages import guild_to_channel
from utils.embed_utils import create_embed_message
import discord
from discord.ext import commands
from data.firebase_message import set_message_mapping, get_message_mapping

class ReactionAddCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return

        if payload.emoji.name == "🍞":
            channel = self.bot.get_channel(payload.channel_id)
            try:
                message = await channel.fetch_message(payload.message_id)
            except discord.NotFound:
                return
            except discord.HTTPException as e:
                print(f"Failed to fetch message: {e}")
                return
            
            # Check if 🍌 (banana) is already there
            banana_reaction = next((r for r in message.reactions if str(r.emoji) == "🍌"), None)
            bread_reaction = next((r for r in message.reactions if str(r.emoji) == "🍞"), None)
            print(f"Banana Reaction: {banana_reaction} Count: {banana_reaction.count}")
            print(f"Bread Reaction: {bread_reaction} Count: {bread_reaction.count}")
            if banana_reaction and banana_reaction.count > 0 and bread_reaction and bread_reaction.count > 0:
                if not await get_message_mapping(payload.message_id):
                    target_channel_id = guild_to_channel[payload.guild_id]
                    target_channel = self.bot.get_channel(target_channel_id)
                    embed = create_embed_message(message)
                    try:
                        sent_message = await target_channel.send(embed=embed)
                        await set_message_mapping(payload.message_id, sent_message.id)
                    except discord.HTTPException as e:
                        print(f"Failed to send message: {e}")

def setup(bot):
    bot.add_cog(ReactionAddCog(bot))
