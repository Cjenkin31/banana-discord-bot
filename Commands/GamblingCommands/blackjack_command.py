import asyncio
from discord.ext import commands
from discord import app_commands
import discord
import math
import random
from data.currency import get_bananas, add_bananas, remove_bananas
from utils.emoji_helper import BANANA_COIN_EMOJI

suits = [':heart_suit:', ':diamond_suit:', ':club_suit:', ':spade_suit:']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
card_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
               'J': 10, 'Q': 10, 'K': 10, 'A': 11}

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
        
        await interaction.response.send_message(f"Playing Blackjack for {bet_amount}{BANANA_COIN_EMOJI}.")

        # Blackjack logic
        bj_msg = await interaction.channel.send(content=f"Blackjack! {BANANA_COIN_EMOJI}\n\nDealing cards...")
        
        deck = Deck()
        
        player_cards = [deck.deal_card(), deck.deal_card()]
        dealer_cards = [deck.deal_card()]
        
        player_score = calculate_score(player_cards)
        dealer_score = calculate_score(dealer_cards)      
        
        dealer_cards.append(deck.deal_card())
        
        if player_score == 0:
            await bj_msg.edit(content=f"Blackjack! {BANANA_COIN_EMOJI}\n\nYou: {display_hand(player_cards)} (21)\nDealer: {display_hand([dealer_cards[0]])} ({dealer_score})\n\nBlackjack, you win {math.floor(bet_amount * 1.5)}{BANANA_COIN_EMOJI}")
            await add_bananas(user_id, math.floor(bet_amount * 1.5))
            return
        
        await bj_msg.edit(content=f"Blackjack! {BANANA_COIN_EMOJI}\n\nYou: {display_hand(player_cards)} ({player_score})\nDealer: {display_hand([dealer_cards[0]])} ({dealer_score})")

        reaction_set = ["👊","🛑"]
        options_text = f"Hit (👊) or Stand (🛑)?\n"
        if bet_amount * 2 <= current_bananas:
            options_text = f"Hit (👊), Stand (🛑), or Double Down (⏬)?\n"
            reaction_set.append("⏬")
        for react in reaction_set:
            await bj_msg.add_reaction(react)
        
        # Player's turn
        while player_score < 21:
            await bj_msg.edit(content=f"Blackjack! {BANANA_COIN_EMOJI}\n\nYou: {display_hand(player_cards)} ({player_score})\nDealer: {display_hand([dealer_cards[0]])} ({dealer_score})\n\n{options_text}")
            
            try: 
                action, user = await bot.wait_for("reaction_add", timeout=60.0, check=lambda reaction, user: user == interaction.user and str(reaction.emoji) in reaction_set)
            except:
                await bj_msg.edit(content=f"Blackjack! {BANANA_COIN_EMOJI}\n\nGame abandoned :(")
                return
            
            try:
                await bj_msg.remove_reaction(action, user)
            except:
                pass
            
            if str(action) == "👊":
                player_cards.append(deck.deal_card())
                player_score = calculate_score(player_cards)
            elif str(action) == "🛑":
                break
            elif str(action) == "⏬":
                bet_amount = bet_amount * 2
                player_cards.append(deck.deal_card())
                player_score = calculate_score(player_cards)
                break
        
        if player_score > 21:
            await bj_msg.edit(content=f"Blackjack! {BANANA_COIN_EMOJI}\n\nYou: {display_hand(player_cards)} ({player_score})\nDealer: {display_hand([dealer_cards[0]])} ({dealer_score})\n\nBusted, you lose {bet_amount}{BANANA_COIN_EMOJI}!")
            await remove_bananas(user_id, bet_amount)
            return
        
        # Dealer's turn
        dealer_score = calculate_score(dealer_cards)
        while dealer_score < 17:
            await bj_msg.edit(content=f"Blackjack! {BANANA_COIN_EMOJI}\n\nYou: {display_hand(player_cards)} ({player_score})\nDealer: {display_hand(dealer_cards)} ({dealer_score})")
            await asyncio.sleep(1)
            dealer_cards.append(deck.deal_card())
            dealer_score = calculate_score(dealer_cards)
            
        if dealer_score > 21:
            result_msg = f"Dealer busts, you win {bet_amount}{BANANA_COIN_EMOJI}!"
            await add_bananas(user_id, bet_amount)
        elif player_score > dealer_score:
            result_msg = f"You win {bet_amount}{BANANA_COIN_EMOJI}!"
            await add_bananas(user_id, bet_amount)
        elif player_score < dealer_score:
            result_msg = f"You lose {bet_amount}{BANANA_COIN_EMOJI}!"
            await remove_bananas(user_id, bet_amount)
        else:
            result_msg = f"Push!"

        await bj_msg.edit(content=f"Blackjack! {BANANA_COIN_EMOJI}\n\nYou: {display_hand(player_cards)} ({player_score})\nDealer: {display_hand(dealer_cards)} ({dealer_score})\n\n{result_msg}")


def calculate_score(cards):
    score = sum(card_values[card.rank] for card in cards)
    if score == 21 and len(cards) == 2:
        return 0  # Blackjack
    if score > 21 and any(card.rank == 'A' for card in cards):
        score -= 10  
    return score

def display_hand(cards):
    return "[ " + ", ".join(str(card) for card in cards) + " ]"

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank}{self.suit}"

class Deck:
    def __init__(self):
        self.cards = []
        for suit in suits:
            for rank in ranks:
                self.cards.append(Card(suit, rank))
        random.shuffle(self.cards)

    def deal_card(self):
        return self.cards.pop()