import random
import logging
from discord.ext import commands
from GPT_stories import getStoryByRole
from data.Currency.currency import add_bananas
from data.stats import get_luck
from utils.emoji_helper import BANANA_COIN_EMOJI
from utils.gpt import generate_gpt_response

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class MessageCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if message.content.startswith('ggez'):
            await message.channel.send(random.choice([
                "Well played. I salute you all.",
                "For glory and honor! Huzzah comrades!",
                "I'm wrestling with some insecurity issues in my life but thank you all for playing with me.",
                "It's past my bedtime. Please don't tell my mommy.",
                "Gee whiz! That was fun. Good playing!",
                "I feel very, very small... please hold me..."
            ]))
        if "🍞" in message.content:
            await message.add_reaction("🍞")
        if random.randint(1, 150) == 1:
            user_luck = await get_luck(message.author.id)
            lower_bound = max(1, user_luck - 10)
            upper_bound = min(100, user_luck + 10)
            banana_amount = random.randint(lower_bound, upper_bound)
            await add_bananas(message.author.id, banana_amount)
            await message.channel.send(
                f"<@{message.author.id}> You just found {banana_amount} {BANANA_COIN_EMOJI}"
            )
        if self.bot.user.mentioned_in(message):
            logger.info(
                "Bot mentioned by user '%s' in channel '%s' with content: %s",
                message.author,
                message.channel,
                message.content
            )

            model = "gpt-4o"
            role = "meanbread" if random.randint(1, 100) == 1 else "bread"
            previous_context = ""
            logger.info("Message reference: %s", message.reference)
            if message.reference and message.reference.resolved:
                replied_message = await message.channel.fetch_message(message.reference.message_id)
                logger.info("Replied message: %s", replied_message.content)
                previous_context = (
                    f" <@{replied_message.author.id} previously said: {replied_message.content}\n"
                )

            story = getStoryByRole(role, message.author.id)
            story += previous_context
            story += f", Now respond to user {message.author.display_name}, or use their @,  <@{message.author.id}>"

            response_message = await generate_gpt_response(model, story, message.content)
            await message.channel.send(response_message)

async def setup(bot):
    await bot.add_cog(MessageCog(bot))
