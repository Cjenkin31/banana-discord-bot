import asyncio
from discord import app_commands
import discord
import math
from data.currency import get_bananas, add_bananas, remove_bananas
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
        bet_amount = int(response)
        user_id = str(interaction.user.id)
        current_bananas = await get_bananas(user_id)
        original_bet = bet_amount
        
        await interaction.response.send_message(f"Playing Mississippi Stud Poker...")

        inprog_color = 0xffff00
        win_color = 0x00ff00
        lose_color = 0xff0000
        
        embed = discord.Embed(title="Poker",
                        description=f"Playing for {bet_amount} {BANANA_COIN_EMOJI}",
                        color=inprog_color)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
        embed.set_footer(text="Dealing cards...")
        poker_msg = await interaction.channel.send(embed=embed)
        
        def update_card_display(hand, status=None):
            value_text = str(hand)
            if status:
                value_text += f"\n{str(status)}"

            player_text = f"**Hand**"
            if hand.field_idx < 0 or hand.field_idx > len(embed.fields):
                raise ValueError(f"Invalid field index: {hand.field_idx}")
            elif hand.field_idx == 0:
                player_text = f"**Streets**"
            
            if hand.field_idx == len(embed.fields):
                embed.add_field(name=f"{player_text}",  
                                value=value_text,
                                inline=False)
            else:
                embed.set_field_at(hand.field_idx, 
                                name=f"{player_text}", 
                                value=value_text,
                                inline=False)
        
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
        update_card_display(streets_hand)   
        
        player_hand = Hand(field_idx=1)
        for _ in range(2): # Deal 2 cards to player to start
            player_hand.add_card(deck.deal_card())
            
            update_card_display(player_hand)
            await poker_msg.edit(embed=embed)
            
            await asyncio.sleep(0.5) # Quick pause between each card
            
        rank = get_poker_hand(player_hand.cards + streets_hand.cards)
        update_card_display(player_hand, rank.ranked_cards_str())
            
        available_actions = ["1️⃣", "2️⃣", "3️⃣", "❌"]
        options_text = f"Bet 1x (1️⃣), 2x (2️⃣), 3x (3️⃣), or Fold (❌)?"
            
        for react in available_actions:
            await poker_msg.add_reaction(react)
        
        folded = False
        for _ in range(3): # For each street  
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
            elif str(action) == "2️⃣": # Bet 2x
                bet_amount += (original_bet * 2)
            elif str(action) == "3️⃣": # Bet 3x
                bet_amount += (original_bet * 3)
            elif str(action) == "❌": # Fold
                folded = True
                break
            
            embed.description=f"Playing for {bet_amount} {BANANA_COIN_EMOJI}"
            streets_hand.add_card(deck.deal_card())
            update_card_display(streets_hand)

            rank = get_poker_hand(player_hand.cards + streets_hand.cards)
            update_card_display(player_hand, rank.ranked_cards_str())
                            
        embed.set_footer(text="Game over!")
        await poker_msg.edit(embed=embed)
        
def get_poker_hand(cards):
    pokerHands = [
        HighCard(0),
        Pair(1),
        TwoPair(2),
        ThreeOfAKind(3),
        Straight(4),
        Flush(5),
        FullHouse(6),
        FourOfAKind(7),
        StraightFlush(8),
        RoyalFlush(9)
    ]
    pokerHands.sort(key=lambda rank: rank.hand_type_value, reverse=True)

    for hand in pokerHands:
        if hand.makes_hand(cards):
            return hand
    return None