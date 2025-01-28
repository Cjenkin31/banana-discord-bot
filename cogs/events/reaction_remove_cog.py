import discord
from discord.ext import commands
from data.saved_messages import guild_to_channel
from data.firebase_message import get_message_mapping, remove_message_mapping

class ReactionRemoveCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.user_id == self.bot.user.id:
            return

        channel = self.bot.get_channel(payload.channel_id)
        try:
            message = await channel.fetch_message(payload.message_id)
        except discord.NotFound:
            return
        except discord.HTTPException as e:
            print(f"Failed to fetch message: {e}")
            return

        reactions = {reaction.emoji: reaction.count for reaction in message.reactions}
        if ('🍌' not in reactions or reactions['🍌'] < 1) or ('🍞' not in reactions or reactions['🍞'] < 1):
            forwarded_message_id = await get_message_mapping(payload.message_id)
            if forwarded_message_id:
                target_channel_id = guild_to_channel[payload.guild_id]
                target_channel = self.bot.get_channel(target_channel_id)
                try:
                    forwarded_message = await target_channel.fetch_message(forwarded_message_id)
                    await forwarded_message.delete()
                    print("Removed forwarded message as original no longer has both reactions")
                except discord.NotFound:
                    print("Forwarded message already deleted.")
                except discord.HTTPException as e:
                    print(f"Failed to delete forwarded message: {e}")
                finally:
                    await remove_message_mapping(payload.message_id)

async def setup(bot):
    await bot.add_cog(ReactionRemoveCog(bot))
