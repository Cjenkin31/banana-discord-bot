import asyncio
from discord import app_commands
import discord
import math
from data.currency import get_bananas, add_bananas, remove_bananas
from game.shared_logic import bet_checks
from utils.emoji_helper import BANANA_COIN_EMOJI
from game.deck import Deck

black_jack_card_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
               'J': 10, 'Q': 10, 'K': 10, 'A': 11}

def define_blackjack_command(tree, servers, bot):
    @tree.command(name="blackjack", description="Play blackjack", guilds=servers)
    @app_commands.describe(bet_amount="Amount of bananas to bet or 'all'")
    async def blackjack(interaction: discord.Interaction, bet_amount: str):
        valid, response = await bet_checks(bet_amount, interaction)
        if (not valid):
            await interaction.response.send_message(str(response))
            return
        bet_amount = int(response)
        user_id = str(interaction.user.id)
        current_bananas = await get_bananas(user_id)
        
        await interaction.response.send_message(f"Playing Blackjack...")
        
        blackjack_score = 21 # Total score for Blackjack
        blackjack_multiplier = 1.5 # Payout multiplier for player Blackjack
        split_limit = 3 # Maximum number of times a player can split their hand(s)
        dealer_stand_threshold = 17 # Maximum score for dealer to draw to
        
        inprog_color = 0xffff00
        win_color = 0x00ff00
        lose_color = 0xff0000
        push_color = 0xff6400
        
        embed = discord.Embed(title="Blackjack",
                        description=f"Playing for {bet_amount} {BANANA_COIN_EMOJI}",
                        color=inprog_color)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
        embed.set_footer(text="Dealing cards...")
        bj_msg = await interaction.channel.send(embed=embed)
        
        def update_hand_display(hand, active=False, status=None):
            value_text = str(hand)
            if status:
                value_text += f"\n{str(status)}"
                
            active_text = ""
            if active:
                active_text = "\> "

            player_text = f"**You** `{hand.score}` ({hand.bet} {BANANA_COIN_EMOJI})"
            if hand.field_idx < 0 or hand.field_idx > len(embed.fields):
                raise ValueError(f"Invalid field index: {hand.field_idx}")
            elif hand.field_idx == 0:
                player_text = f"**Dealer** `{hand.score}`"
            
            if hand.field_idx == len(embed.fields):
                embed.add_field(name=f"{active_text}{player_text}",  
                                value=value_text,
                                inline=False)
            else:
                embed.set_field_at(hand.field_idx, 
                                name=f"{active_text}{player_text}", 
                                value=value_text,
                                inline=False)
        
        # Blackjack Hand class, must be within command function scope
        class Hand:
            def __init__(self, cards=None, bet=0, field_idx=-1):
                if cards is None:
                    self.cards = []
                else:
                    self.cards = cards
                self.bet = bet
                self.field_idx = field_idx
                self.score = self.calculate_score()
                
            def add_card(self, card):
                self.cards.append(card)
                self.score = self.calculate_score()
                
            def remove_card(self):
                if not len(self.cards):
                    return None
                card = self.cards.pop()
                self.score = self.calculate_score()
                return card

            def calculate_score(self):
                score = sum(black_jack_card_values[card.rank] for card in self.cards)
                for card in self.cards:
                    if score > blackjack_score and card.rank == 'A':
                        score -= 10
                return score

            def __str__(self):
                return "[ " + ", ".join("**" + str(card) + "**" for card in self.cards) + " ]"
        
        deck = Deck() # Game deck
        deck.shuffle_deck() # Shuffle game deck
        
        dealer_hand = Hand(field_idx=0) # Dealer's hand
        update_hand_display(dealer_hand)
        
        player_hands = [] # List of all player's hands
        
        player_hand = Hand(bet=bet_amount, field_idx=1) # Player's initial hand
        player_hands.append(player_hand)
        for _ in range(2): # Deal 2 cards to player to start
            player_hand.add_card(deck.deal_card())
            
            update_hand_display(player_hand)
            await bj_msg.edit(embed=embed)
            
            await asyncio.sleep(0.5) # Quick pause between each card
        
        dealer_hand.add_card(deck.deal_card()) # Dealer's shown card
        update_hand_display(dealer_hand)
        await bj_msg.edit(embed=embed)
        dealer_hand.add_card(deck.deal_card()) # Dealer's concealed card
        
        if player_hand.score == blackjack_score and len(player_hand.cards) == 2: # Blackjack
            bj_winnings = math.floor(player_hand.bet * blackjack_multiplier)

            update_hand_display(player_hand, status=f"Blackjack! +{bj_winnings} {BANANA_COIN_EMOJI}")
            embed.set_footer(text="Game over!")
            embed.description = f"You win {bj_winnings} {BANANA_COIN_EMOJI}!"
            embed.color = win_color
            await bj_msg.edit(embed=embed)
            
            await add_bananas(user_id, bj_winnings)
            return
        
        hands_to_calculate = [] # Player hands to calculate winnings for
        reaction_set = [] # Bot reactions on game message
        
        # Player's turn
        while len(player_hands): # Turns for each player's hand
            current_hand = player_hands.pop(0)
            hands_to_calculate.append(current_hand)
            
            can_double_down = True
            while current_hand.score <= blackjack_score: # Player's turn for hand
                if current_hand.score == blackjack_score:
                    update_hand_display(current_hand)
                    break
                
                available_actions = ["👊","🛑"]
                options_text = f"Hit (👊) or Stand (🛑)?"
                
                if bet_amount + current_hand.bet <= current_bananas: # Ability to make an additional bet
                    if can_double_down: # Ability to double down
                        available_actions.append("⏬")
                        options_text = f"Hit (👊), Stand (🛑), or Double Down (⏬)?"
                    if (bet_amount + current_hand.bet <= current_bananas and # Ability to split hand
                            len(player_hands) + len(hands_to_calculate) <= split_limit and 
                            len(current_hand.cards) > 1 and 
                            all(black_jack_card_values[current_hand.cards[0].rank] == 
                                black_jack_card_values[card.rank] for card in current_hand.cards)):
                        available_actions.append("🔀")
                        options_text = f"Hit (👊), Stand (🛑), Double Down (⏬), or Split (🔀)?"
                    
                for react in available_actions:
                    if react not in reaction_set:
                        await bj_msg.add_reaction(react)
                        reaction_set.append(react)
                    
                update_hand_display(current_hand, active=True)   
                embed.set_footer(text=options_text)    
                await bj_msg.edit(embed=embed)
                
                try: # Wait for player action
                    def check(reaction, user): # Only accept valid reactions
                        return user == interaction.user and \
                                reaction.message.id == bj_msg.id and \
                                str(reaction.emoji) in available_actions
                        
                    action, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
                except: # Timeout
                    embed.description = f"YOU LOST YOUR BET OF {bet_amount+1} {BANANA_COIN_EMOJI}! The bot stole 1 {BANANA_COIN_EMOJI}!"
                    embed.set_footer(text="Game abandoned!")
                    embed.color = lose_color
                    await bj_msg.edit(embed=embed)
                    await remove_bananas(user_id, bet_amount+1)
                    return
                
                embed.set_footer(text="Please wait...")
                await bj_msg.edit(embed=embed)
                
                try: # Remove player's reaction
                    await bj_msg.remove_reaction(action, user)
                except:
                    pass
                
                if str(action) == "👊": # Hit
                    can_double_down = False # Can't double down after hitting
                    current_hand.add_card(deck.deal_card())
                elif str(action) == "🛑": # Stand
                    update_hand_display(current_hand)
                    await bj_msg.edit(embed=embed)
                    break
                elif str(action) == "⏬": # Double Down
                    bet_amount += current_hand.bet
                    current_hand.bet *= 2
                    current_hand.add_card(deck.deal_card())
                    embed.description = f"Playing for {bet_amount} {BANANA_COIN_EMOJI}"
                    update_hand_display(current_hand)
                    await bj_msg.edit(embed=embed)
                    break
                elif str(action) == "🔀": # Split
                    bet_amount += current_hand.bet
                    split_player_hand = Hand([current_hand.remove_card()], bet=current_hand.bet, field_idx=len(embed.fields))
                    player_hands.append(split_player_hand)
                    
                    embed.description = f"Playing for {bet_amount} {BANANA_COIN_EMOJI}"
                    update_hand_display(current_hand, active=True)
                    update_hand_display(split_player_hand)
                    await bj_msg.edit(embed=embed)
                    
                    current_hand.add_card(deck.deal_card())
                    split_player_hand.add_card(deck.deal_card())
                    
                    await asyncio.sleep(0.5)
                    
                    update_hand_display(current_hand, active=True)
                    await bj_msg.edit(embed=embed)
                    
                if current_hand.score > blackjack_score: # Check for player bust
                    update_hand_display(current_hand, status="Bust!")
                elif current_hand.score == blackjack_score:
                    update_hand_display(current_hand)
                else:
                    update_hand_display(current_hand, active=True)
                    
                await bj_msg.edit(embed=embed)
        
        # Skip dealer's turn if only player's hand busted
        if not (len(hands_to_calculate) == 1 and hands_to_calculate[0].score > blackjack_score): 
            # Dealer's turn
            embed.set_footer(text="Dealer's turn...")
            update_hand_display(dealer_hand, active=True)
            await bj_msg.edit(embed=embed)
            
            while dealer_hand.score < dealer_stand_threshold:
                await asyncio.sleep(1)

                dealer_hand.add_card(deck.deal_card())
                
                if dealer_hand.score > blackjack_score: # Check for dealer bust
                    update_hand_display(dealer_hand, status="Bust!")
                else:
                    update_hand_display(dealer_hand, active=True)
                await bj_msg.edit(embed=embed)
            update_hand_display(dealer_hand, active=False)
        
        # Calculate winnings
        winnings = 0
        for hand in hands_to_calculate:           
            result_msg = None
            if hand.score > blackjack_score: # Player hand bust
                winnings -= hand.bet
                result_msg = f"Bust! -{hand.bet} {BANANA_COIN_EMOJI}"
            elif dealer_hand.score > blackjack_score: # Dealer hand bust
                winnings += hand.bet
                result_msg = f"Win! +{hand.bet} {BANANA_COIN_EMOJI}"
            elif hand.score > dealer_hand.score: # Player hand win
                winnings += hand.bet
                result_msg = f"Win! +{hand.bet} {BANANA_COIN_EMOJI}"
            elif hand.score < dealer_hand.score: # Dealer hand win
                winnings -= hand.bet
                result_msg = f"Loss! -{hand.bet} {BANANA_COIN_EMOJI}"
            else: # Tie
                result_msg = f"Push!"
                
            update_hand_display(hand, status=result_msg)
            
        if winnings > 0: # Player wins currency overall
            embed.color = win_color
            embed.description = f"You win {winnings} {BANANA_COIN_EMOJI}!"
            await add_bananas(user_id, winnings)
        elif winnings < 0: # Player loses currency overall
            embed.color = lose_color
            embed.description = f"You lose {abs(winnings)} {BANANA_COIN_EMOJI}!"
            await remove_bananas(user_id, abs(winnings))
        else: # Player is even overall
            embed.description = "No winnings or losses!"
            embed.color = push_color

        embed.set_footer(text="Game over!")
        await bj_msg.edit(embed=embed)