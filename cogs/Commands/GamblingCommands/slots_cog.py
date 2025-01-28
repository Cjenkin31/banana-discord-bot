import asyncio
import random
from config.config import SERVERS
from data.stats import get_luck
from discord.ext import commands
from discord import app_commands
import discord
from data.Currency.currency import add_bananas, remove_bananas
from game.shared_logic import bet_checks
from utils.emoji_helper import BANANA_COIN_EMOJI, SLOT_ROW_1_EMOJI, SLOT_ROW_2_EMOJI, SLOT_ROW_3_EMOJI, SLOT_EMOJI

class SlotsCommands(commands.Cog, name="slots"):
    def __init__(self, bot):
        self.bot = bot

    def normalize_weights(self, weights):
        total = sum(weights)
        return [w / total for w in weights] if total > 0 else [1/len(weights)] * len(weights)

    @app_commands.command(name="slots", description="Play slots")
    @app_commands.guilds(*SERVERS)
    @app_commands.describe(bet_amount="Amount of bananas to bet or 'all'")
    async def slots(self, interaction: discord.Interaction, bet_amount: str):
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

        luck_stat = await get_luck(user_id)
        slot_luck_stat = luck_stat/3600
        slot_data = {
            '🍒': {'weight': .9, 'payout': 1},
            '🍐': {'weight': .8+slot_luck_stat, 'payout': 2},
            '🍋': {'weight': .7+slot_luck_stat, 'payout': 2},
            '🍑': {'weight': .6+slot_luck_stat, 'payout': 2},
            '🍓': {'weight': .5+slot_luck_stat, 'payout': 3},
            '🍇': {'weight': .4+(slot_luck_stat*2), 'payout': 3},
            '⭐': {'weight': .3+(slot_luck_stat*3), 'payout': 5},
            '🍌': {'weight': .2+(slot_luck_stat*5), 'payout': 10},
            '💎': {'weight': .1+(slot_luck_stat*10), 'payout': 50}
        }

        slot_data = {symbol: {'weight': weight, 'payout': data['payout']}
                    for symbol, (weight, data) in zip(slot_data.keys(), zip(self.normalize_weights([data['weight'] for data in slot_data.values()]), slot_data.values()))}

        symbols = list(slot_data.keys())
        weights = [data['weight'] for data in slot_data.values()]
        slots = random.choices(symbols, weights, k=3)

        await asyncio.sleep(0.5)
        embed.set_field_at(0, name="Spinning...", value=f"{slots[0]} | {SLOT_ROW_2_EMOJI} | {SLOT_ROW_3_EMOJI}", inline=True)
        await slots_msg.edit(embed=embed)
        await asyncio.sleep(0.5)
        embed.set_field_at(0, name="Spinning...", value=f"{slots[0]} | {slots[1]} | {SLOT_ROW_3_EMOJI}", inline=True)
        await slots_msg.edit(embed=embed)
        await asyncio.sleep(0.5)

        if slots[0] == slots[1] == slots[2]:
            payout = slot_data[slots[0]]['payout'] * bet_amount * 10
            total_net_gain += payout
            result_text = f"Jackpot! You won {payout} {BANANA_COIN_EMOJI}"
            embed.color = 0x00ff00
        elif slots[0] == slots[1] or slots[1] == slots[2]:
            payout = slot_data[slots[1]]['payout'] * bet_amount
            total_net_gain += payout
            result_text = f"Congratulations! You won {payout} {BANANA_COIN_EMOJI}"
            embed.color = 0x00ff00
        else:
            result_text = f"Sorry, you didn't win this time. You lost {bet_amount} {BANANA_COIN_EMOJI}"
            embed.color = 0xff0000

        embed.set_field_at(0, name="Result", value=f"{slots[0]} | {slots[1]} | {slots[2]}", inline=False)
        embed.description += f"\n{result_text}"
        await slots_msg.edit(embed=embed)

        if total_net_gain > 0:
            await add_bananas(user_id, total_net_gain)
        elif total_net_gain < 0:
            await remove_bananas(user_id, abs(total_net_gain))

async def setup(bot):
    await bot.add_cog(SlotsCommands(bot))
