import asyncio
from config.config import SERVERS
from discord.ext import commands
from discord import app_commands
import discord

from data.Currency.currency import get_bananas, add_bananas, remove_bananas
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


class PokerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    POKER_HANDS = {
        HighCard:        {'value': 0, 'payout': 0},
        Pair:            {'value': 1, 'payout': 1},
        TwoPair:         {'value': 2, 'payout': 2},
        ThreeOfAKind:    {'value': 3, 'payout': 3},
        Straight:        {'value': 4, 'payout': 4},
        Flush:           {'value': 5, 'payout': 6},
        FullHouse:       {'value': 6, 'payout': 10},
        FourOfAKind:     {'value': 7, 'payout': 40},
        StraightFlush:   {'value': 8, 'payout': 100},
        RoyalFlush:      {'value': 9, 'payout': 500}
    }

    IN_PROGRESS_COLOR = 0xffff00
    WIN_COLOR         = 0x00ff00
    LOSE_COLOR        = 0xff0000
    PUSH_COLOR        = 0xff6400
    NUMBER_STREETS    = 3

    @app_commands.guilds(*SERVERS)
    @app_commands.command(name="poker", description="Play Mississippi Stud poker")
    @app_commands.describe(bet_amount="Amount of bananas to bet or 'all'")
    async def poker(self, interaction: discord.Interaction, bet_amount: str):
        """
        Main entry point for Mississippi Stud Poker.
        """
        # 1) Validate the user's bet
        valid, response = await bet_checks(bet_amount, interaction)
        if not valid:
            await interaction.response.send_message(str(response))
            return

        game_state = {
            "original_bet": int(response),
            "bet_amount":   int(response),  # running total
            "folded":       False,
            "user_id":      str(interaction.user.id),
            "deck":         Deck()
        }

        # 2) Check if the user has enough bananas
        if not await self.validate_user_has_enough(game_state, interaction):
            return

        # 3) Prepare embed & shuffle deck
        game_state["deck"].shuffle_deck()
        embed = self.create_initial_embed(interaction, game_state)
        poker_msg = await interaction.channel.send(embed=embed)

        # 4) Deal initial cards (hole cards), update embed
        player_hand, streets_hand = self.deal_initial_cards(game_state, embed)

        # Show the updated hole cards
        embed.set_field_at(
            index=1,
            name="**Hole Cards**",
            value=str(player_hand),
            inline=False
        )
        await poker_msg.edit(embed=embed)

        # 5) Streets
        for _ in range(self.NUMBER_STREETS):
            user_folded = await self.prompt_street_bet(game_state, embed, poker_msg, interaction)
            if user_folded:
                break

            # Deal one street card
            streets_hand.add_card(game_state["deck"].deal_card())
            # Update embed with the new street
            self.update_streets_field(embed, streets_hand)
            # Re-evaluate best hand
            self.update_ranked_hand_field(embed, player_hand, streets_hand)

            # Update pot info in embed
            embed.description = (
                f"Ante: {game_state['original_bet']} {BANANA_COIN_EMOJI}\n"
                f"Playing for {game_state['bet_amount']} {BANANA_COIN_EMOJI}"
            )
            await poker_msg.edit(embed=embed)

            if game_state["folded"]:
                break

        # 6) Resolve final outcome
        await self.resolve_final_outcome(game_state, player_hand, streets_hand, embed)
        embed.set_footer(text="Game over!")
        await poker_msg.edit(embed=embed)

    # ================== Helper Methods ================== #

    async def validate_user_has_enough(self, gs: dict, interaction: discord.Interaction) -> bool:
        """Check if user can afford to play."""
        current_bananas = await get_bananas(gs["user_id"])
        if gs["original_bet"] * 3 > current_bananas:
            await interaction.response.send_message(
                "You don't have enough bananas to play this game."
            )
            return False

        # Deduct the ante from user
        await remove_bananas(gs["user_id"], gs["original_bet"])
        gs["bet_amount"] = gs["original_bet"]
        gs["remaining_bananas"] = current_bananas - gs["original_bet"]

        await interaction.response.send_message("Playing Mississippi Stud Poker...")
        return True

    def create_initial_embed(self, interaction: discord.Interaction, gs: dict) -> discord.Embed:
        """Set up the initial embed display."""
        embed = discord.Embed(
            title="Poker",
            description=(
                f"Ante: {gs['original_bet']} {BANANA_COIN_EMOJI}\n"
                f"Playing for {gs['bet_amount']} {BANANA_COIN_EMOJI}"
            ),
            color=self.IN_PROGRESS_COLOR
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
        embed.set_footer(text="Dealing cards...")

        # Add fields for Streets and Hole Cards
        embed.add_field(name="**Streets**", value="", inline=False)
        embed.add_field(name="**Hole Cards**", value="", inline=False)
        return embed

    def deal_initial_cards(self, gs: dict, _: discord.Embed):
        """Deal two hole cards to the player, return (player_hand, streets_hand)."""
        class Hand:
            def __init__(self):
                self.cards = []

            def add_card(self, card):
                self.cards.append(card)

            def __str__(self):
                return "[ " + ", ".join(f"**{c}**" for c in self.cards) + " ]"

        player_hand = Hand()
        streets_hand = Hand()

        # Deal 2 hole cards
        for _ in range(2):
            player_hand.add_card(gs["deck"].deal_card())

        return player_hand, streets_hand

    async def prompt_street_bet(self, gs: dict, embed: discord.Embed,
                                poker_msg: discord.Message, interaction: discord.Interaction) -> bool:
        """Prompt bet or fold. Returns True if user folded."""
        options_text = "Bet 1x (1️⃣) / 2x (2️⃣) / 3x (3️⃣) Ante, or Fold (❌)"
        possible_actions = ["1️⃣", "2️⃣", "3️⃣", "❌"]

        if gs["remaining_bananas"] < gs["original_bet"] * 3:
            options_text = "Bet 1x (1️⃣) / 2x (2️⃣) Ante, or Fold (❌)"
            possible_actions = ["1️⃣", "2️⃣", "❌"]
        if gs["remaining_bananas"] < gs["original_bet"] * 2:
            options_text = "Bet 1x (1️⃣) Ante, or Fold (❌)"
            possible_actions = ["1️⃣", "❌"]
        if gs["remaining_bananas"] < gs["original_bet"]:
            options_text = "Fold (❌)"
            possible_actions = ["❌"]

        embed.set_footer(text=options_text)
        await poker_msg.edit(embed=embed)

        # Add reactions
        for act in possible_actions:
            await poker_msg.add_reaction(act)

        # Wait for user choice
        try:
            def check(r, u):
                return (
                    u == interaction.user and
                    r.message.id == poker_msg.id and
                    str(r.emoji) in possible_actions
                )
            reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
        except asyncio.TimeoutError:
            embed.description = (
                f"YOU LOST YOUR BET OF {gs['bet_amount']+1} {BANANA_COIN_EMOJI}! "
                "The bot stole 1 banana for inactivity!"
            )
            embed.set_footer(text="Game abandoned!")
            embed.color = self.LOSE_COLOR
            await poker_msg.edit(embed=embed)
            await remove_bananas(gs["user_id"], gs["bet_amount"]+1)
            gs["folded"] = True
            return True

        # Remove reaction
        try:
            await poker_msg.remove_reaction(reaction, user)
        except:
            pass

        embed.set_footer(text="Please wait...")
        await poker_msg.edit(embed=embed)

        if str(reaction.emoji) == "❌":
            gs["folded"] = True
            return True

        # Note: After return, there's no need for elif → fix R1705
        if str(reaction.emoji) == "1️⃣":
            gs["bet_amount"] += gs["original_bet"]
            gs["remaining_bananas"] -= gs["original_bet"]
            return False

        if str(reaction.emoji) == "2️⃣":
            gs["bet_amount"] += gs["original_bet"] * 2
            gs["remaining_bananas"] -= gs["original_bet"] * 2
            return False

        if str(reaction.emoji) == "3️⃣":
            gs["bet_amount"] += gs["original_bet"] * 3
            gs["remaining_bananas"] -= gs["original_bet"] * 3
            return False

        return False

    def update_streets_field(self, embed: discord.Embed, streets_hand) -> None:
        """Update the 'Streets' field in the embed."""
        embed.set_field_at(
            0,
            name="**Streets**",
            value=str(streets_hand),
            inline=False
        )

    def update_ranked_hand_field(self, embed: discord.Embed, player_hand, streets_hand) -> None:
        """Show the current best 5-card hand in the embed."""
        ranked_hand = self.get_poker_hand(player_hand.cards + streets_hand.cards)
        best_cards = ranked_hand.get_ranked_cards() if ranked_hand else []
        best_str = "[ " + ", ".join(f"**{c}**" for c in best_cards) + " ]"
        field_name = f"**{ranked_hand.get_name()}**" if ranked_hand else "**No Hand**"

        if len(embed.fields) < 3:
            embed.add_field(name=field_name, value=best_str, inline=False)
        else:
            embed.set_field_at(index=2, name=field_name, value=best_str, inline=False)

    def get_poker_hand(self, cards):
        """Return the first matching PokerHand object or None."""
        # Build a list of possible hands
        possible = []
        for hand_type, data in self.POKER_HANDS.items():
            possible.append(hand_type(data['value']))
        possible.sort(key=lambda h: h.hand_type_value, reverse=True)

        for h in possible:
            if h.makes_hand(cards):
                return h
        return None

    async def resolve_final_outcome(self, gs: dict, player_hand, streets_hand, embed: discord.Embed) -> None:
        """Determine final outcome; add or remove bananas accordingly."""
        user_id = gs["user_id"]

        if gs["folded"]:
            embed.description = f"Fold, you lose {gs['bet_amount']} {BANANA_COIN_EMOJI}!"
            embed.color = self.LOSE_COLOR
            await remove_bananas(user_id, gs["bet_amount"])
            return

        # Evaluate final hand
        ranked_hand = self.get_poker_hand(player_hand.cards + streets_hand.cards)
        if not ranked_hand:
            embed.description = f"You lose {gs['bet_amount']} {BANANA_COIN_EMOJI}!"
            embed.color = self.LOSE_COLOR
            await remove_bananas(user_id, gs["bet_amount"])
            return

        # Pair logic
        if isinstance(ranked_hand, Pair):
            if card_rank_values[ranked_hand.rank] > 10:
                embed.description = f"You win {gs['bet_amount']} {BANANA_COIN_EMOJI}!"
                embed.color = self.WIN_COLOR
                await add_bananas(user_id, gs['bet_amount'])
            else:
                embed.description = "Push, no winnings or losses!"
                embed.color = self.PUSH_COLOR
            return

        # Other winning hands
        winnings = 0
        for hand_type, data in self.POKER_HANDS.items():
            if isinstance(ranked_hand, hand_type):
                winnings = gs["bet_amount"] * data['payout']
                break

        if winnings > 0:
            embed.description = f"You win {winnings} {BANANA_COIN_EMOJI}!"
            embed.color = self.WIN_COLOR
            await add_bananas(user_id, winnings)
        else:
            embed.description = f"You lose {gs['bet_amount']} {BANANA_COIN_EMOJI}!"
            embed.color = self.LOSE_COLOR
            await remove_bananas(user_id, gs["bet_amount"])

async def setup(bot):
    await bot.add_cog(PokerCommands(bot))
