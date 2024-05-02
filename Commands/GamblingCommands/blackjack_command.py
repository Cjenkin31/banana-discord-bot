import asyncio
from discord import app_commands
import discord
import math
from data.currency import get_bananas, add_bananas, remove_bananas
from utils.emoji_helper import BANANA_COIN_EMOJI
from game.deck import Deck

card_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
               'J': 10, 'Q': 10, 'K': 10, 'A': 11}

def define_blackjack_command(tree, servers, bot):
    @tree.command(name="blackjack", description="Play blackjack", guilds=servers)
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
        
        await interaction.response.send_message(f"Playing Blackjack...")
        
        inprog_color = 0xffff00
        win_color = 0x00ff00
        lose_color = 0xff0000
        push_color = 0xff6400
        
        embed = discord.Embed(title="Blackjack",
                        description=f"Playing for {bet_amount} {BANANA_COIN_EMOJI}",
                        colour=inprog_color)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
        embed.add_field(name="**You**", value="", inline=True)
        embed.add_field(name="**Dealer**", value="", inline=True)
        embed.set_footer(text="Dealing cards...")
        bj_msg = await interaction.channel.send(embed=embed)
        
        def update_embed_field(hand, idx=0, is_active=False):
            player_text = "**You**"
            set_inline = True
            if idx == 1:
                player_text = "**Dealer**"
            elif idx > 2:
                set_inline = False
                
            active_text = ""
            if is_active:
                active_text = "\> "
                
            embed.set_field_at(idx, name=f"{active_text}{player_text} `{hand.score}` ({hand.bet} {BANANA_COIN_EMOJI})", inline=set_inline)
        
        # Blackjack Hand class, must be within command function scope
        class Hand:
            def __init__(self, cards=[], bet=0):
                self.cards = cards
                self.bet = bet
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
                score = sum(card_values[card.rank] for card in self.cards)
                for card in self.cards:
                    if score > 21 and card.rank == 'A':
                        score -= 10
                return score

            def __str__(self):
                return "[ " + ", ".join("**" + str(card) + "**" for card in self.cards) + " ]"
        
        deck = Deck() # Game deck
        deck.shuffle_deck() # Shuffle game deck
        
        player_hand = Hand(bet=bet_amount) # Player's initial hand
        player_hands = [player_hand] # List of all player's hands
        for _ in range(2): # Deal 2 cards to player to start
            player_hand.add_card(deck.deal_card())
            
            embed.set_field_at(0, name=f"**You** `{player_hand.score}` ({player_hand.bet} {BANANA_COIN_EMOJI})",
                            value=str(player_hand),
                            inline=True)
            await bj_msg.edit(embed=embed)
            
            await asyncio.sleep(0.5) # Quick pause between each card
            
        dealer_hand = Hand([deck.deal_card()]) # Dealer's hand
    
        embed.set_field_at(1, name=f"**Dealer** `{dealer_hand.score}`",
                        value=str(dealer_hand),
                        inline=True)
        await bj_msg.edit(embed=embed)
        
        dealer_hand.add_card(deck.deal_card()) # Dealer's concealed card
        
        if player_hand.score == 21 and len(player_hand.cards) == 2: # Blackjack
            bj_winnings = math.floor(player_hand.bet * 1.5)

            embed.set_field_at(0, name=f"**You** `{player_hand.score}` ({player_hand.bet} {BANANA_COIN_EMOJI})",
                            value=f"{str(player_hand)}\nBlackjack! +{bj_winnings} {BANANA_COIN_EMOJI}",
                            inline=True)
            embed.set_footer(text="Game over!")
            embed.description = f"You win {bj_winnings} {BANANA_COIN_EMOJI}!"
            embed.color = win_color
            await bj_msg.edit(embed=embed)
            
            await add_bananas(user_id, bj_winnings)
            return
        
        # Determine available player actions
        reaction_set = ["👊","🛑"]
        options_text = f"Hit (👊) or Stand (🛑)?"
        if bet_amount * 2 <= current_bananas: # Ability to make an additional bet (double down/split)
            options_text = f"Hit (👊), Stand (🛑), or Double Down (⏬)?"
            reaction_set.append("⏬")
            if (len(player_hand.cards) > 1 and # Ability to split hand
                    all(card_values[player_hand.cards[0].rank] == card_values[card.rank] for card in player_hand.cards)):
                options_text = f"Hit (👊), Stand (🛑), Double Down (⏬), or Split (🔀)?"
                reaction_set.append("🔀")
                
        for react in reaction_set:
            await bj_msg.add_reaction(react)

        embed.set_field_at(0, name=f"\> **You** `{player_hand.score}` ({player_hand.bet} {BANANA_COIN_EMOJI})",
                        value=str(player_hand),
                        inline=True)
        embed.set_footer(text=options_text)
        await bj_msg.edit(embed=embed)
        
        # Player's turn (first move)
        try: 
            def check(reaction, user):
                return user == interaction.user and \
                        reaction.message.id == bj_msg.id and \
                        str(reaction.emoji) in reaction_set
                
            action, user = await bot.wait_for("reaction_add", timeout=60.0, check=check) # Wait for player action
        except: # Timeout
            embed.description = f"YOU LOST YOUR BET OF {bet_amount+1} {BANANA_COIN_EMOJI}! The bot stole 1 {BANANA_COIN_EMOJI}!"
            embed.set_footer(text="Game abandoned!")
            embed.color = lose_color
            await bj_msg.edit(embed=embed)
            await remove_bananas(user_id, bet_amount+1)
            return

        try:
            await bj_msg.remove_reaction(action, user)
        except:
            pass
        
        one_move_only = False
        hit_first_move = False
        if str(action) == "👊": # Hit
            hit_first_move = True
            player_hand.add_card(deck.deal_card())
        elif str(action) == "🛑": # Stand
            one_move_only = True
            pass
        elif str(action) == "⏬": # Double Down
            one_move_only = True
            bet_amount += player_hand.bet
            player_hand.bet *= 2
            player_hand.add_card(deck.deal_card())
            embed.description = f"Playing for {bet_amount} {BANANA_COIN_EMOJI}"
        elif str(action) == "🔀": # Split
            bet_amount += player_hand.bet
            split_player_hand = Hand([player_hand.remove_card()], player_hand.bet)
            player_hands.append(split_player_hand)
            embed.description = f"Playing for {bet_amount} {BANANA_COIN_EMOJI}"
            embed.add_field(name=f"**You** `{split_player_hand.score}` ({split_player_hand.bet} {BANANA_COIN_EMOJI})", 
                        value=str(split_player_hand),
                        inline=False)

        embed.set_field_at(0, name=f"**You** `{player_hand.score}` ({player_hand.bet} {BANANA_COIN_EMOJI})",
                        value=str(player_hand),
                        inline=True)
        await bj_msg.edit(embed=embed)

        if player_hand.score > 21: # Bust
            embed.set_field_at(0, name=f"**You** `{player_hand.score}` ({player_hand.bet} {BANANA_COIN_EMOJI})",
                            value=f"{str(player_hand)}\nBust! -{player_hand.bet} {BANANA_COIN_EMOJI}",
                            inline=True)
            embed.description = f"You lose {player_hand.bet} {BANANA_COIN_EMOJI}!"
            embed.set_footer(text="Game over!")
            embed.color = lose_color
            await bj_msg.edit(embed=embed)
            await remove_bananas(user_id, player_hand.bet)
            return
        
        hands_to_calculate = []
        
        hand_idx = 0
        while len(player_hands): # Turns for each player's hand
            current_hand = player_hands.pop(0)
            hands_to_calculate.append(current_hand)
            
            if one_move_only:
                break
            
            field_idx = hand_idx
            inline_field = True
            if hand_idx > 0:
                inline_field = False
                field_idx += 1
            hand_idx += 1
                
            reaction_set = ["👊","🛑"]
            options_text = f"Hit (👊) or Stand (🛑)?"
            if not hit_first_move and bet_amount + current_hand.bet <= current_bananas:
                reaction_set = ["👊","🛑", "⏬"]
                options_text = f"Hit (👊), Stand (🛑), or Double Down (⏬)?"
            embed.set_footer(text=options_text)
            embed.set_field_at(field_idx, name=f"\> **You** `{current_hand.score}` ({current_hand.bet} {BANANA_COIN_EMOJI})",
                            value=str(current_hand),
                            inline=inline_field)
            await bj_msg.edit(embed=embed)
            
            while current_hand.score < 21: # Player's turn for hand
                if (bet_amount + current_hand.bet <= current_bananas and len(current_hand.cards) > 1 and # Ability to split hand
                        all(card_values[current_hand.cards[0].rank] == card_values[card.rank] for card in current_hand.cards)):
                    options_text = f"Hit (👊), Stand (🛑), Double Down (⏬), or Split (🔀)?"
                    reaction_set.append("🔀")
                    embed.set_footer(text=options_text)
                    await bj_msg.edit(embed=embed)
                    
                try: 
                    def check(reaction, user):
                        return user == interaction.user and \
                                reaction.message.id == bj_msg.id and \
                                str(reaction.emoji) in reaction_set
                        
                    action, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
                except:
                    embed.description = f"YOU LOST YOUR BET OF {bet_amount+1} {BANANA_COIN_EMOJI}! The bot stole 1 {BANANA_COIN_EMOJI}!"
                    embed.set_footer(text="Game abandoned!")
                    embed.color = lose_color
                    await bj_msg.edit(embed=embed)
                    await remove_bananas(user_id, bet_amount+1)
                    return
                
                try:
                    await bj_msg.remove_reaction(action, user)
                except:
                    pass
                
                if str(action) == "👊": # Hit
                    current_hand.add_card(deck.deal_card())
                    reaction_set = ["👊","🛑"]
                    options_text = f"Hit (👊) or Stand (🛑)?"
                    embed.set_footer(text=options_text)
                elif str(action) == "🛑": # Stand
                    break
                elif str(action) == "⏬": # Double Down
                    bet_amount += current_hand.bet
                    current_hand.bet *= 2
                    
                    current_hand.add_card(deck.deal_card())
                    embed.description = f"Playing for {bet_amount} {BANANA_COIN_EMOJI}"
                    embed.set_field_at(field_idx, name=f"\> **You** `{current_hand.score}` ({current_hand.bet} {BANANA_COIN_EMOJI})",
                                    value=str(current_hand),
                                    inline=inline_field)
                    await bj_msg.edit(embed=embed)
                    break
                elif str(action) == "🔀": # Split
                    bet_amount += current_hand.bet
                    split_player_hand = Hand([current_hand.remove_card()], current_hand.bet)
                    player_hands.append(split_player_hand)
                    embed.description = f"Playing for {bet_amount} {BANANA_COIN_EMOJI}"
                    embed.add_field(name=f"**You** `{split_player_hand.score}` ({split_player_hand.bet} {BANANA_COIN_EMOJI})", 
                                value=str(split_player_hand),
                                inline=False)
                    
                embed.set_field_at(field_idx, name=f"\> **You** `{current_hand.score}` ({current_hand.bet} {BANANA_COIN_EMOJI})",
                                value=str(current_hand),
                                inline=inline_field)
                await bj_msg.edit(embed=embed)
            
            if current_hand.score > 21:
                embed.set_field_at(field_idx, name=f"**You** `{current_hand.score}` ({current_hand.bet} {BANANA_COIN_EMOJI})",
                                value=f"{str(current_hand)}\nBust!",
                                inline=inline_field)
            else:
                embed.set_field_at(field_idx, name=f"**You** `{current_hand.score}` ({current_hand.bet} {BANANA_COIN_EMOJI})",
                                value=str(current_hand),
                                inline=inline_field)
            await bj_msg.edit(embed=embed)
        
        # Dealer's turn
        embed.set_footer(text="Dealer's turn...")
        embed.set_field_at(1, name=f"\> **Dealer** `{dealer_hand.score}`",
                        value=str(dealer_hand),
                        inline=True)
        await bj_msg.edit(embed=embed)
        
        while dealer_hand.score < 17:
            await asyncio.sleep(1)

            dealer_hand.add_card(deck.deal_card())
            
            embed.set_field_at(1, name=f"\> **Dealer** `{dealer_hand.score}`",
                        value=str(dealer_hand),
                        inline=True)
            await bj_msg.edit(embed=embed)
            
        if dealer_hand.score > 21:
            embed.set_field_at(1, name=f"**Dealer** `{dealer_hand.score}`",
                    value=f"{str(dealer_hand)}\nBust!",
                    inline=True)
        else:
            embed.set_field_at(1, name=f"**Dealer** `{dealer_hand.score}`",
                    value=str(dealer_hand),
                    inline=True)
        
        # Calculate winnings
        winnings = 0
        hand_idx = 0
        for hand in hands_to_calculate:
            field_idx = hand_idx
            inline_field = True
            if hand_idx > 0:
                inline_field = False
                field_idx += 1
            hand_idx += 1            

            result_msg = f"{str(hand)}\n"
            if hand.score > 21:
                winnings -= hand.bet
                result_msg += f"Bust! -{hand.bet} {BANANA_COIN_EMOJI}"
            elif dealer_hand.score > 21:
                winnings += hand.bet
                result_msg += f"Win! +{hand.bet} {BANANA_COIN_EMOJI}"
            elif hand.score > dealer_hand.score:
                winnings += hand.bet
                result_msg += f"Win! +{hand.bet} {BANANA_COIN_EMOJI}"
            elif hand.score < dealer_hand.score:
                winnings -= hand.bet
                result_msg += f"Loss! -{hand.bet} {BANANA_COIN_EMOJI}"
            else:
                result_msg += f"Push!"
                
            embed.set_field_at(field_idx, name=f"**You** `{hand.score}` ({hand.bet} {BANANA_COIN_EMOJI})",
                            value=result_msg,
                            inline=inline_field)
            
        if winnings > 0:
            embed.color = win_color
            embed.description = f"You win {winnings} {BANANA_COIN_EMOJI}!"
            await add_bananas(user_id, winnings)
        elif winnings < 0:
            embed.color = lose_color
            embed.description = f"You lose {abs(winnings)} {BANANA_COIN_EMOJI}!"
            await remove_bananas(user_id, abs(winnings))
        else:
            embed.description = "No winnings or losses!"
            embed.color = push_color

        embed.set_footer(text="Game over!")
        await bj_msg.edit(embed=embed)