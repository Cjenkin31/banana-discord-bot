from discord.ext import commands
from discord import app_commands
import discord
import random
from data.currency import get_bananas, add_bananas, remove_bananas
from utils.emoji_helper import BANANA_COIN_EMOJI
def define_blackjack_command(tree, servers, bot):
    @tree.command(name="blackjack", description="Guess Heads or Tails to double your bet or lose it", guilds=servers)
    @app_commands.describe(bet_amount="Amount of bananas to bet or 'all'")
    async def blackjack(interaction: discord.Interaction, bet_amount: str):
        # Determine if the bet is 'all' or a specific amount
        if bet_amount.lower() == 'all':
            current_bananas = await get_bananas(str(interaction.user.id))
            bet_amount = current_bananas
        else:
            try:
                bet_amount = int(bet_amount)
                if bet_amount <= 0:
                    raise ValueError("Bet amount must be a positive number.")
            except ValueError as e:
                await interaction.response.send_message(str(e))
                return

        user_id = str(interaction.user.id)
        current_bananas = await get_bananas(user_id)

        if current_bananas == 0:
            await interaction.response.send_message(f"You have no {BANANA_COIN_EMOJI}!")
            return
        
        if bet_amount > current_bananas:
            await interaction.response.send_message(f"You don't have enough {BANANA_COIN_EMOJI} to make this bet.")
            return

        # Blackjack logic
        player_cards = [draw_card(), draw_card()]
        dealer_cards = [draw_card(), draw_card()]
        
        player_score = calculate_score(player_cards)
        dealer_score = calculate_score(dealer_cards)      
        
        bot_msg = await interaction.response.send_message(content=f"Blackjack! {BANANA_COIN_EMOJI}\n\n \
                        Dealing cards...")
        
        # Player's turn
        while player_score < 21:
            await bot_msg.edit(content=f"Blackjack! {BANANA_COIN_EMOJI}\n\n \
                            Your cards: {player_cards}, current score: {player_score}\n \
                            Dealer's first card: {dealer_cards[0]}\n\n \
                            Do you want to hit or stand? Type: 'hit' or 'stand'")
            
            # TODO implement reactions instead of message replies
            # try:
            #     reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=lambda msg: msg.author == interaction.author and (str(reaction.emoji) == '👍' or str(reaction.emoji) == '👎'))
            # except:
            #     return
            # else:
            #     pass
            
            try: 
                message = await bot.wait_for("message", check=lambda msg: msg.author == interaction.author, timeout=60.0)
            except:
                await bot_msg.edit(content=f"Blackjack! {BANANA_COIN_EMOJI}\n\nGame abandoned :(")
                return
            else:
                pass
            
            action = message.content.lower()
            if action == 'h' or action =='hit':
                player_cards.append(draw_card())
                player_score = calculate_score(player_cards)
                if player_score == 0:
                    await bot_msg.edit(content=f"Blackjack! {BANANA_COIN_EMOJI}\n\n \
                                    Your cards: {player_cards}, current score: {player_score}\n \
                                    Dealer's first card: {dealer_cards[0]}\n\n \
                                    BLACKJACK! {BANANA_COIN_EMOJI}")
                    await add_bananas(user_id, bet_amount * 1.5)
                    return
            elif action == 's' or action == 'stand':
                break
        
        # Dealer's turn
        while dealer_score < 17:
            dealer_cards.append(draw_card())
            dealer_score = calculate_score(dealer_cards)
        
        if player_score > 21:
            result_msg = f"You went over 21. You lose! {BANANA_COIN_EMOJI}"
            await remove_bananas(user_id, bet_amount)
        elif dealer_score > 21:
            result_msg = f"Dealer went over 21. You win! {BANANA_COIN_EMOJI}"
            await add_bananas(user_id, bet_amount)
        elif player_score > dealer_score:
            result_msg = f"You win! {BANANA_COIN_EMOJI}"
            await add_bananas(user_id, bet_amount)
        elif player_score < dealer_score:
            result_msg = f"You lose! {BANANA_COIN_EMOJI}"
            await remove_bananas(user_id, bet_amount)
        else:
            result_msg = f"It's a tie! {BANANA_COIN_EMOJI}"

        await bot_msg.edit(content=f"Blackjack! {BANANA_COIN_EMOJI}\n\n \
                        Your cards: {player_cards}, final score: {player_score}\n \
                        Dealer's cards: {dealer_cards}, final score: {dealer_score}\n\n \
                        {result_msg}")


def draw_card():
    return random.randint(1, 11)


def calculate_score(cards):
    if sum(cards) == 21 and len(cards) == 2:
        return 0  # Blackjack
    if 11 in cards and sum(cards) > 21:
        cards.remove(11)
        cards.append(1)
    return sum(cards)