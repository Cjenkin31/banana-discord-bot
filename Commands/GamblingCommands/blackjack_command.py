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
        
        embed = discord.Embed(title="Blackjack",
                        description=f"Playing for {bet_amount} {BANANA_COIN_EMOJI}",
                        colour=0xffff00)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
        embed.add_field(name="**You**", value="", inline=True)
        embed.add_field(name="**Dealer**", value="", inline=True)
        embed.set_footer(text="Dealing cards...")
        bj_msg = await interaction.channel.send(embed=embed)
        
        # Blackjack logic
        deck = Deck()
        
        player_cards = []
        for i in range(2):
            player_cards.append(deck.deal_card())
            player_score = calculate_score(player_cards)
            
            display_player_score = 21 if player_score == 0 else player_score
            embed.set_field_at(0, name=f"**You** `{display_player_score}`",
                            value=display_hand(player_cards),
                            inline=True)
            await bj_msg.edit(embed=embed)
            
            await asyncio.sleep(0.5)
        
        dealer_cards = [deck.deal_card()]
        dealer_score = calculate_score(dealer_cards)      
        dealer_cards.append(deck.deal_card())
    
        embed.set_field_at(1, name=f"**Dealer** `{dealer_score}`",
                        value=display_hand([dealer_cards[0]]),
                        inline=True)
        await bj_msg.edit(embed=embed)
        
        if player_score == 0: # Blackjack
            winnings = math.floor(bet_amount * 1.5)
            
            embed.set_footer(text=f"Blackjack, you win {winnings} {BANANA_COIN_EMOJI}")
            embed.color = 0x00ff00
            await bj_msg.edit(embed=embed)
            
            await add_bananas(user_id, winnings)
            return
        
        reaction_set = ["👊","🛑"]
        options_text = f"Hit (👊) or Stand (🛑)?"
        if bet_amount * 2 <= current_bananas:
            options_text = f"Hit (👊), Stand (🛑), or Double Down (⏬)?"
            reaction_set.append("⏬")
        for react in reaction_set:
            await bj_msg.add_reaction(react)
            
        embed.set_footer(text=options_text)
        await bj_msg.edit(embed=embed)
        
        # Player's turn
        doubled_down = False
        while player_score < 21 and not doubled_down:
            try: 
                def check(reaction, user):
                    return user == interaction.user and \
                            reaction.message.id == bj_msg.id and \
                            str(reaction.emoji) in reaction_set
                    
                action, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
            except:
                embed.set_footer(text=f"Game abandoned :( YOU LOST YOUR BET OF {bet_amount+1} {BANANA_COIN_EMOJI}! The bot stole 1 {BANANA_COIN_EMOJI}!")
                embed.color = 0xff0000
                await bj_msg.edit(embed=embed)
                await remove_bananas(user_id, bet_amount+1)
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
                doubled_down = True
                embed.description = f"Playing for {bet_amount} {BANANA_COIN_EMOJI}"
            
            embed.set_field_at(0, name=f"**You** `{player_score}`",
                            value=display_hand(player_cards),
                            inline=True)
            await bj_msg.edit(embed=embed)
        
        if player_score > 21:
            embed.set_footer(text=f"Bust! You lose {bet_amount} {BANANA_COIN_EMOJI}!")
            embed.color = 0xff0000
            await bj_msg.edit(embed=embed)
            await remove_bananas(user_id, bet_amount)
            return
        
        # Dealer's turn
        dealer_score = calculate_score(dealer_cards)
        dealer_score = 21 if dealer_score == 0 else dealer_score
        embed.set_field_at(1, name=f"**Dealer** `{dealer_score}`",
                        value=display_hand(dealer_cards),
                        inline=True)
        await bj_msg.edit(embed=embed)
        
        while dealer_score < 17:
            await asyncio.sleep(1)
            
            dealer_cards.append(deck.deal_card())
            dealer_score = calculate_score(dealer_cards)
            
            embed.set_field_at(1, name=f"**Dealer** `{dealer_score}`",
                        value=display_hand(dealer_cards),
                        inline=True)
            await bj_msg.edit(embed=embed)
            
        if dealer_score > 21:
            result_msg = f"Dealer busts, you win {bet_amount} {BANANA_COIN_EMOJI}!"
            embed.color = 0x00ff00
            await add_bananas(user_id, bet_amount)
        elif player_score > dealer_score:
            result_msg = f"You win {bet_amount} {BANANA_COIN_EMOJI}!"
            embed.color = 0x00ff00
            await add_bananas(user_id, bet_amount)
        elif player_score < dealer_score:
            result_msg = f"You lose {bet_amount} {BANANA_COIN_EMOJI}!"
            embed.color = 0xff0000
            await remove_bananas(user_id, bet_amount)
        else:
            result_msg = f"Push!"
            embed.color = 0xff6400

        embed.set_footer(text=result_msg)
        await bj_msg.edit(embed=embed)

def calculate_score(cards):
    score = sum(card_values[card.rank] for card in cards)
    if score == 21 and len(cards) == 2:
        return 0  # Blackjack
    
    for card in cards:
        if score > 21 and card.rank == 'A':
            score -= 10
              
    return score

def display_hand(cards):
    return "[ " + ", ".join(str(card) for card in cards) + " ]"