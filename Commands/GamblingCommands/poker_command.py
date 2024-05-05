import asyncio
from discord import app_commands
import discord
import math
from data.currency import get_bananas, add_bananas, remove_bananas
from game.poker.poker_hand import card_rank_values
from game.poker.flush import Flush
from game.poker.four_of_a_kind import FourOfAKind
from game.poker.full_house import FullHouse
from game.poker.high_card import HighCard
from game.poker.pair import Pair
from game.poker.royal_flush import RoyalFlush
from game.poker.straight import Straight
from game.poker.straight_flush import StraightFlush
from game.poker.three_of_a_kind import ThreeOfAKind
from game.poker.two_pair import TwoPair
from game.shared_logic import bet_checks
from utils.emoji_helper import BANANA_COIN_EMOJI
from game.deck import Deck

def define_poker_command(tree, servers, bot):
    @tree.command(name="poker", description="Play Mississippi Stud poker", guilds=servers)
    @app_commands.describe(bet_amount="Amount of bananas to bet or 'all'")
    async def poker(interaction: discord.Interaction, bet_amount: str):
        valid, response = await bet_checks(bet_amount, interaction)
        if (not valid):
            await interaction.response.send_message(str(response))
            return
        bet_amount = int(response)
        
        user_id = str(interaction.user.id)
        current_bananas = await get_bananas(user_id)
        
        if bet_amount * 3 > current_bananas:
            await interaction.response.send_message("You don't have enough :bananacoin: to play this game.")
            return
        original_bet = bet_amount
        
        await interaction.response.send_message(f"Playing Mississippi Stud Poker...")
        
        poker_hands = {
            HighCard: {'value': 0, 'payout': 0},
            Pair: {'value': 1, 'payout': 1},
            TwoPair: {'value': 2, 'payout': 2},
            ThreeOfAKind: {'value': 3, 'payout': 3},
            Straight: {'value': 4, 'payout': 4},
            Flush: {'value': 5, 'payout': 6},
            FullHouse: {'value': 6, 'payout': 10},
            FourOfAKind: {'value': 7, 'payout': 40},
            StraightFlush: {'value': 8, 'payout': 100},
            RoyalFlush: {'value': 9, 'payout': 500}
        }
        
        def get_poker_hand(cards):
            poker_hand_values = []
            for hand_type, data in poker_hands.items():
                poker_hand_values.append(hand_type(data['value']))
            poker_hand_values.sort(key=lambda rank: rank.hand_type_value, reverse=True)

            for hand in poker_hand_values:
                if hand.makes_hand(cards):
                    return hand
            return None
        
        number_streets = 3

        inprog_color = 0xffff00
        win_color = 0x00ff00
        lose_color = 0xff0000
        push_color = 0xff6400
        
        embed = discord.Embed(title="Poker",
                        description=f"Ante: {original_bet} {BANANA_COIN_EMOJI}\nPlaying for {bet_amount} {BANANA_COIN_EMOJI}",
                        color=inprog_color)
        embed.add_field(name="**Streets**", value="", inline=False)
        embed.add_field(name="**Hole Cards**", value="", inline=False)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
        embed.set_footer(text="Dealing cards...")
        poker_msg = await interaction.channel.send(embed=embed)
        
        class Hand:
            def __init__(self, cards=None, field_idx=0):
                if cards is None:
                    self.cards = [] 
                else:
                    self.cards = cards
                self.field_idx = field_idx
                
            def add_card(self, card):
                self.cards.append(card)

            def __str__(self):
                return "[ " + ", ".join("**" + str(card) + "**" for card in self.cards) + " ]"
        
        deck = Deck() # Game deck
        deck.shuffle_deck() # Shuffle game deck
        
        streets_hand = Hand(field_idx=0)
        embed.set_field_at(0, name="**Streets**", 
                        value=str(streets_hand),
                        inline=False)  
        
        player_hand = Hand(field_idx=1)
        for _ in range(2): # Deal 2 cards to player to start
            player_hand.add_card(deck.deal_card())
            
            embed.set_field_at(1, name="**Hole Cards**", 
                            value=str(player_hand),
                            inline=False)
            await poker_msg.edit(embed=embed)
            
            await asyncio.sleep(0.5) # Quick pause between each card
            
        ranked_hand = get_poker_hand(player_hand.cards + streets_hand.cards)
        made_poker_hand = Hand(ranked_hand.get_ranked_cards(), field_idx=2)
        embed.add_field(name=f"**{ranked_hand.get_name()}**", 
                        value=str(made_poker_hand),
                        inline=False)
            
        available_actions = ["1️⃣", "2️⃣", "3️⃣", "❌"]
        
        for react in available_actions:
            await poker_msg.add_reaction(react)
        
        folded = False
        remaining_bananas = current_bananas - bet_amount
        for _ in range(number_streets): # For each street  
            available_actions = ["1️⃣", "2️⃣", "3️⃣", "❌"]
            options_text = f"Bet 1x (1️⃣) / 2x (2️⃣) / 3x (3️⃣) Ante, or Fold (❌)"
            if remaining_bananas - (original_bet * 3) < 0:
                available_actions = ["1️⃣", "2️⃣", "❌"]
                options_text = f"Bet 1x (1️⃣) / 2x (2️⃣) Ante, or Fold (❌)"
            if remaining_bananas - (original_bet * 2) < 0:
                available_actions = ["1️⃣", "❌"]
                options_text = f"Bet 1x (1️⃣) Ante, or Fold (❌)"
            if remaining_bananas - original_bet < 0:
                available_actions = ["❌"]
                options_text = f"Fold (❌)"

            embed.set_footer(text=options_text)
            await poker_msg.edit(embed=embed)
                      
            try: # Wait for player action
                def check(reaction, user): # Only accept valid reactions
                    return user == interaction.user and \
                            reaction.message.id == poker_msg.id and \
                            str(reaction.emoji) in available_actions
                    
                action, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
            except: # Timeout
                embed.description = f"YOU LOST YOUR BET OF {bet_amount+1} {BANANA_COIN_EMOJI}! The bot stole 1 {BANANA_COIN_EMOJI}!"
                embed.set_footer(text="Game abandoned!")
                embed.color = lose_color
                await poker_msg.edit(embed=embed)
                await remove_bananas(user_id, bet_amount+1)
                return
            
            embed.set_footer(text="Please wait...")
            await poker_msg.edit(embed=embed)
            
            try: # Remove player's reaction
                await poker_msg.remove_reaction(action, user)
            except:
                pass
            
            if str(action) == "1️⃣": # Bet 1x
                bet_amount += original_bet
                remaining_bananas -= original_bet
            elif str(action) == "2️⃣": # Bet 2x
                bet_amount += (original_bet * 2)
                remaining_bananas -= (original_bet * 2)
            elif str(action) == "3️⃣": # Bet 3x
                bet_amount += (original_bet * 3)
                remaining_bananas -= (original_bet * 3)
            elif str(action) == "❌": # Fold
                folded = True
                break
            
            embed.description=f"Ante: {original_bet} {BANANA_COIN_EMOJI}\nPlaying for {bet_amount} {BANANA_COIN_EMOJI}"
            streets_hand.add_card(deck.deal_card())
            embed.set_field_at(0, name="**Streets**", 
                        value=str(streets_hand),
                        inline=False)

            ranked_hand = get_poker_hand(player_hand.cards + streets_hand.cards)
            made_poker_hand.cards = ranked_hand.get_ranked_cards()
            embed.set_field_at(2, name=f"**{ranked_hand.get_name()}**", 
                            value=str(made_poker_hand),
                            inline=False)
            
        if folded:
            embed.description=f"Fold, you lose {bet_amount} {BANANA_COIN_EMOJI}!"
            embed.color = lose_color
            await remove_bananas(user_id, bet_amount)
        elif ranked_hand is None:
            embed.description=f"You lose {bet_amount} {BANANA_COIN_EMOJI}!"
            embed.color = lose_color
            await remove_bananas(user_id, bet_amount)
        elif isinstance(ranked_hand, Pair):
            if card_rank_values[ranked_hand.rank] > 10:
                embed.description=f"You win {bet_amount} {BANANA_COIN_EMOJI}!"
                embed.color = win_color
                await add_bananas(user_id, bet_amount)
            else:
                embed.description=f"Push, no winnings or losses!"
                embed.color = push_color
        else:
            winnings = 0
            for hand_type, data in poker_hands.items():
                if isinstance(ranked_hand, hand_type):
                    winnings = bet_amount * data['payout']
                    
            if winnings > 0:
                embed.description=f"You win {winnings} {BANANA_COIN_EMOJI}"
                embed.color = win_color
                await add_bananas(user_id, winnings)
            else:
                embed.description=f"You lose {bet_amount} {BANANA_COIN_EMOJI}"
                embed.color = lose_color
                await remove_bananas(user_id, bet_amount)  
                            
        embed.set_footer(text="Game over!")
        await poker_msg.edit(embed=embed)