import asyncio
import random
from discord import app_commands
import discord
from data.currency import get_bananas, add_bananas, remove_bananas
from game.shared_logic import bet_checks
from utils.emoji_helper import BANANA_COIN_EMOJI, SLOT_ROW_1_EMOJI, SLOT_ROW_2_EMOJI, SLOT_ROW_3_EMOJI, SLOT_EMOJI

def define_slots_command(tree, servers):
    @tree.command(name="slots", description="Play slots", guilds=servers)
    @app_commands.describe(bet_amount="Amount of bananas to bet or 'all'")
    async def slots(interaction: discord.Interaction, bet_amount: str):
        valid, response = await bet_checks(bet_amount, interaction)
        if not valid:
            await interaction.response.send_message(str(response))
            return
        bet_amount = int(response)
        user_id = str(interaction.user.id)

        # Initialize total net gain which is -amt they put in
        total_net_gain = -bet_amount

        await interaction.response.send_message("Playing slots...")
        
        embed = discord.Embed(title=f"Slots {SLOT_EMOJI}", description=f"Playing for {bet_amount} {BANANA_COIN_EMOJI}", color=0xffff00)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.add_field(name="Spinning...", value=f"{SLOT_ROW_1_EMOJI} | {SLOT_ROW_2_EMOJI} | {SLOT_ROW_3_EMOJI}", inline=True)
        slots_msg = await interaction.channel.send(embed=embed)

        # Slot machine data
        slot_data = {
            '🍇': {'weight': 9, 'payout': 1},
            '🍓': {'weight': 8, 'payout': 1},
            '🍋': {'weight': 7, 'payout': 2},
            '🍒': {'weight': 6, 'payout': 3},
            '🍑': {'weight': 5, 'payout': 5},
            '🍐': {'weight': 4, 'payout': 15},
            '⭐': {'weight': 3, 'payout': 20},
            '🍌': {'weight': 2, 'payout': 25},
            '💎': {'weight': 1, 'payout': 50}
        }

        weighted_symbols = [symbol for symbol, data in slot_data.items() for _ in range(data['weight'])]

        slot1 = random.choice(weighted_symbols)
        slot2 = random.choice(weighted_symbols)
        slot3 = random.choice(weighted_symbols)

        await asyncio.sleep(0.5)
        embed.set_field_at(0, name="Spinning...", value=f"{slot1} | {SLOT_ROW_2_EMOJI} | {SLOT_ROW_3_EMOJI}", inline=True)
        await slots_msg.edit(embed=embed)
        await asyncio.sleep(0.5)
        embed.set_field_at(0, name="Spinning...", value=f"{slot1} | {slot2} | {SLOT_ROW_3_EMOJI}", inline=True)
        await slots_msg.edit(embed=embed)
        await asyncio.sleep(0.5)

        result_text = ""
        if slot1 == slot2 == slot3:
            payout = slot_data[slot1]['payout'] * bet_amount * 10
            total_net_gain += payout
            result_text = "Jackpot!"
            embed.description = f"Jackpot! You gained {total_net_gain} {BANANA_COIN_EMOJI}"
            embed.color = 0x00ff00
        elif slot1 == slot2 or slot2 == slot3:
            payout = slot_data[slot1]['payout'] * bet_amount
            if slot2 == slot3:
                payout = slot_data[slot2]['payout'] * bet_amount
            total_net_gain += payout
            result_text = "You won!"
            embed.description = f"Congratulations! You gained {total_net_gain} {BANANA_COIN_EMOJI}"
            embed.color = 0x00ff00
        else:
            result_text = "Try again!"
            embed.description = f"Sorry, you didn't win this time. You lost {total_net_gain} {BANANA_COIN_EMOJI}"
            embed.color = 0xff0000

        embed.set_field_at(0, name=result_text, value=f"{slot1} | {slot2} | {slot3}", inline=True)
        await slots_msg.edit(embed=embed)

        if total_net_gain > 0:
            await add_bananas(user_id, total_net_gain)
        elif total_net_gain < 0:
            await remove_bananas(user_id, abs(total_net_gain))