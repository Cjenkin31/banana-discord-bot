import asyncio
import random
from discord import app_commands
import discord
from data.currency import get_bananas, add_bananas, remove_bananas
from utils.emoji_helper import BANANA_COIN_EMOJI, SLOT_ROW_1_EMOJI, SLOT_ROW_2_EMOJI, SLOT_ROW_3_EMOJI, SLOT_EMOJI
def define_slots_command(tree, servers):
    @tree.command(name="slots", description="Play slots", guilds=servers)
    @app_commands.describe(bet_amount="Amount of bananas to bet or 'all'")
    async def coinflip(interaction: discord.Interaction, bet_amount: str):        
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
                await interaction.response.send_message("Please put a valid betting amount")
                return

        user_id = str(interaction.user.id)
        current_bananas = await get_bananas(user_id)

        if current_bananas == 0:
            await interaction.response.send_message(f"You have no {BANANA_COIN_EMOJI}!")
            return
        
        if bet_amount > current_bananas:
            await interaction.response.send_message(f"You don't have enough {BANANA_COIN_EMOJI} to make this bet.")
            return

        # Slots logic
        jackpot_multiplier = 10
        
        winning_color = 0x00ff00
        losing_color = 0xff0000
        inprog_color = 0xffff00
        
        await interaction.response.send_message(f"Playing slots...")
        
        await remove_bananas(user_id, bet_amount)
        
        embed = discord.Embed(title=f"Slots {SLOT_EMOJI}",
                        description=f"Playing for {bet_amount} {BANANA_COIN_EMOJI}",
                        color=inprog_color)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
        embed.add_field(name="Spinning...", value=f"\{SLOT_ROW_1_EMOJI}| \{SLOT_ROW_2_EMOJI} | \{SLOT_ROW_3_EMOJI}", inline=True)
        slots_msg = await interaction.channel.send(embed=embed)
        
        # Slot machine data
        # Weight: likelihood of being selected (higher is more likely)
        # Payout: payout multiplier (multiplied by bet amount)
        # Note: payout of '1' only wins back bet amount
        slot_data = {
            '🍇': {'weight': 9, 'payout': 1},
            '🍓': {'weight': 8, 'payout': 1},
            '🍋': {'weight': 7, 'payout': 2},
            '🍒': {'weight': 6, 'payout': 2},
            '🍑': {'weight': 5, 'payout': 5},
            '🍐': {'weight': 4, 'payout': 5},
            '⭐': {'weight': 3, 'payout': 10},
            '🍌': {'weight': 2, 'payout': 25},
            '💎': {'weight': 1, 'payout': 50}
        }
        
        weighted_symbols = [symbol for symbol, data in slot_data.items() for _ in range(data['weight'])]
        
        slot1 = random.choice(weighted_symbols)
        slot2 = random.choice(weighted_symbols)
        slot3 = random.choice(weighted_symbols)
        
        await asyncio.sleep(0.5)
        
        embed.set_field_at(0, name="Spinning...", value=f"{slot1} | ➖ | ➖", inline=True)
        await slots_msg.edit(embed=embed)
        
        await asyncio.sleep(0.5)
        
        embed.set_field_at(0, name="Spinning...", value=f"{slot1} | {slot2} | ➖", inline=True)
        await slots_msg.edit(embed=embed)
        
        await asyncio.sleep(0.5)
        
        result_text = ""
        if slot1 == slot2 == slot3:
            payout = slot_data[slot1]['payout'] * bet_amount * jackpot_multiplier
            result_text = "Jackpot!"
            embed.description = f"Jackpot! You won {payout} {BANANA_COIN_EMOJI}"
            embed.color = winning_color
            await add_bananas(user_id, payout)
        elif slot1 == slot2 or slot1 == slot3 or slot2 == slot3:
            payout = slot_data[slot1]['payout'] * bet_amount
            if slot2 == slot3:
                payout = slot_data[slot2]['payout'] * bet_amount
            result_text = "You won!"
            embed.description = f"Congratulations! You won {payout} {BANANA_COIN_EMOJI}"
            embed.color = winning_color
            await add_bananas(user_id, payout)
        else:
            result_text = "Try again!"
            embed.description = "Sorry, you didn't win this time."
            embed.color = losing_color
        
        embed.set_field_at(0, name=result_text, value=f"{slot1} | {slot2} | {slot3}", inline=True)
        await slots_msg.edit(embed=embed)
