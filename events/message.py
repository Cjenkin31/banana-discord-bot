import random
from GPT_stories import getStoryByRole
from data.currency import add_bananas
from utils.emoji_helper import BANANA_COIN_EMOJI
from utils.gpt import generate_gpt_response
from utils.users import UNBUTTERED_BAGEL_ID

async def setup_message(bot):
    @bot.event
    async def on_message(message):
        if message.author == bot.user:
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
        if random.randint(1, 100) == 1:
            banana_amount = random.randint(1,100)
            await add_bananas(message.author.id, banana_amount)
            await message.channel.send(f"<@{message.author.id}> You just found {banana_amount} {BANANA_COIN_EMOJI}")
        if bot.user.mentioned_in(message):
            model = "gpt-3.5-turbo"
            role = "bread"
            previous_context = ""
            if message.reference and message.reference.resolved:
                replied_message = await message.channel.fetch_message(message.reference.message_id)
                previous_context = f"You previously said: {replied_message.content}\n"
            story = getStoryByRole(role, message.author.id)
            story = previous_context + story
            story += f" Respond to user {message.author.display_name}, or use their @,  <@{message.author.id}>"
            response_message = await generate_gpt_response(model, story, message.content)
            await message.channel.send(response_message)
        if message.content.startswith('ertw'):
            await message.channel.send("\\")