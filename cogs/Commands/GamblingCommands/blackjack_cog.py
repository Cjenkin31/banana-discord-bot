import asyncio
import math
import logging
from discord.ext import commands
from discord import app_commands
import discord

from config.config import SERVERS
from data.Currency.currency import get_bananas, add_bananas, remove_bananas
from game.shared_logic import bet_checks
from utils.emoji_helper import BANANA_COIN_EMOJI
from game.deck import Deck

# Create and configure a module-level logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Or adjust to INFO/ERROR depending on verbosity desired

black_jack_card_values = {
    '2': 2, '3': 3, '4': 5, '5': 5, '6': 6, '7': 7,
    '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11
}

class BlackjackCog(commands.Cog):
    """A Cog that handles Blackjack gameplay."""

    # ------------------ Class-Level Constants ------------------ #
    BLACKJACK_SCORE         = 21
    BLACKJACK_MULTIPLIER    = 1.5  # Payout multiplier for player Blackjack
    SPLIT_LIMIT             = 3    # Maximum splits
    DEALER_STAND_THRESHOLD  = 17   # Dealer draws until 17 or higher

    # Embed Colors
    INPROG_COLOR = 0xffff00
    WIN_COLOR    = 0x00ff00
    LOSE_COLOR   = 0xff0000
    PUSH_COLOR   = 0xff6400

    def __init__(self, bot):
        self.bot = bot
        logger.info("BlackjackCog initialized.")

    @app_commands.command(name="blackjack", description="Play blackjack")
    @app_commands.guilds(*SERVERS)
    @app_commands.describe(bet_amount="Amount of bananas to bet or 'all'")
    async def blackjack(self, interaction: discord.Interaction, bet_amount: str):
        """
        Main entry point for the Blackjack command.
        """
        logger.info("User %s invoked blackjack command with bet '%s'", interaction.user, bet_amount)

        # 1) Validate the bet
        valid, response = await bet_checks(bet_amount, interaction)
        if not valid:
            logger.warning("Bet validation failed for user %s. Response: %s", interaction.user, response)
            await interaction.response.send_message(str(response))
            return
        bet_amount_int = int(response)
        logger.debug("User %s bet validated: %d", interaction.user, bet_amount_int)

        user_id = str(interaction.user.id)
        current_bananas = await get_bananas(user_id)
        logger.debug("User %s has %d bananas before betting.", interaction.user, current_bananas)

        # 2) Quick notification
        await interaction.response.send_message("Playing Blackjack...")

        # 3) Check if user has enough bananas
        if bet_amount_int > current_bananas:
            logger.warning("User %s tried to bet %d, but only has %d.",
                           interaction.user, bet_amount_int, current_bananas)
            await interaction.followup.send("You don't have enough bananas to place that bet!")
            return

        # 4) Create embed & message
        embed = discord.Embed(
            title="Blackjack",
            description=f"Playing for {bet_amount_int} {BANANA_COIN_EMOJI}",
            color=self.INPROG_COLOR
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
        embed.set_footer(text="Dealing cards...")
        bj_msg = await interaction.channel.send(embed=embed)
        logger.debug("Initial Blackjack embed sent for user %s.", interaction.user)

        # 5) Create deck & hands
        deck = Deck()
        deck.shuffle_deck()
        logger.debug("Deck created and shuffled.")

        dealer_hand = self.Hand(field_idx=0)
        player_hand = self.Hand(bet=bet_amount_int, field_idx=1)

        # 6) Store game state
        game_state = {
            "user_id":         user_id,
            "current_bananas": current_bananas,
            "bet_amount":      bet_amount_int,  # total bet so far
            "deck":            deck,
            "bj_msg":          bj_msg,
            "embed":           embed,
            "interaction":     interaction,
            "player_hands":    [player_hand],
            "hands_to_calc":   []
        }

        logger.info("Starting Blackjack game for user %s with bet %d.", interaction.user, bet_amount_int)

        # 7) Deal initial cards
        await self.deal_initial_cards(game_state, dealer_hand, player_hand)

        # 8) Check immediate Blackjack
        if self.is_player_blackjack(player_hand):
            logger.info("User %s got a Blackjack immediately.", interaction.user)
            await self.handle_player_blackjack(game_state, player_hand)
            return

        # 9) Player turns
        logger.debug("Proceeding to player turns.")
        await self.handle_player_turns(game_state)

        # 10) Dealer turn (only if not all busted)
        all_busted = all(h.score > self.BLACKJACK_SCORE for h in game_state["hands_to_calc"])
        if not all_busted:
            logger.debug("At least one hand remains; dealer will take a turn.")
            await self.handle_dealer_turn(game_state, dealer_hand)
        else:
            logger.debug("All player hands busted; dealer turn skipped.")

        # 11) Calculate final outcome
        await self.calculate_winnings(game_state, dealer_hand)

    # ===================== Inner Class Hand ====================== #
    class Hand:
        """Represents a single hand in Blackjack."""
        def __init__(self, cards=None, bet=0, field_idx=-1):
            self.cards = cards if cards else []
            self.bet = bet
            self.field_idx = field_idx
            self.score = self.calculate_score()

        def add_card(self, card):
            self.cards.append(card)
            self.score = self.calculate_score()

        def remove_card(self):
            if not self.cards:
                return None
            card = self.cards.pop()
            self.score = self.calculate_score()
            return card

        def calculate_score(self):
            """Compute best score, counting Aces as 1 or 11."""
            score = sum(black_jack_card_values[c.rank] for c in self.cards)
            for c in self.cards:
                if score > BlackjackCog.BLACKJACK_SCORE and c.rank == 'A':
                    score -= 10
            return score

        def __str__(self):
            return "[ " + ", ".join(f"**{c}**" for c in self.cards) + " ]"

    # ===================== Helper Methods ====================== #

    def update_hand_display(self, embed: discord.Embed, hand: Hand,
                            active: bool = False, status: str = None):
        """Updates the embed field for a given hand."""
        value_text = str(hand)
        if status:
            value_text += f"\n{status}"

        active_text = "> " if active else ""

        if hand.field_idx == 0:
            player_text = f"**Dealer** `{hand.score}`"
        else:
            player_text = f"**You** `{hand.score}` ({hand.bet} {BANANA_COIN_EMOJI})"

        if hand.field_idx < 0 or hand.field_idx > len(embed.fields):
            logger.error("Invalid field index %s. Unable to update hand display.", hand.field_idx)
            raise ValueError(f"Invalid field index: {hand.field_idx}")

        if hand.field_idx == len(embed.fields):
            embed.add_field(
                name=f"{active_text}{player_text}",
                value=value_text,
                inline=False
            )
        else:
            embed.set_field_at(
                index=hand.field_idx,
                name=f"{active_text}{player_text}",
                value=value_text,
                inline=False
            )

    async def deal_initial_cards(self, gs: dict, dealer_hand: Hand, player_hand: Hand):
        """Deal initial 2 cards to player, 1 shown + 1 hidden to dealer."""
        bj_msg = gs["bj_msg"]
        embed = gs["embed"]
        deck  = gs["deck"]

        logger.debug("Dealing initial cards...")

        # Show empty dealer field
        self.update_hand_display(embed, dealer_hand)
        await bj_msg.edit(embed=embed)

        # Deal 2 to player
        for _ in range(2):
            card = deck.deal_card()
            player_hand.add_card(card)
            logger.debug("Dealt %s to player.", card)
            self.update_hand_display(embed, player_hand)
            await bj_msg.edit(embed=embed)
            await asyncio.sleep(0.5)

        # Dealer's shown card
        d_card_shown = deck.deal_card()
        dealer_hand.add_card(d_card_shown)
        logger.debug("Dealer shown card: %s", d_card_shown)
        self.update_hand_display(embed, dealer_hand)
        await bj_msg.edit(embed=embed)

        # Dealer's hidden card
        d_card_hidden = deck.deal_card()
        dealer_hand.add_card(d_card_hidden)  # Not shown yet
        logger.debug("Dealer hidden card: %s (Not displayed to players)", d_card_hidden)

    def is_player_blackjack(self, player_hand: Hand) -> bool:
        """Check if player got a Blackjack."""
        return (player_hand.score == self.BLACKJACK_SCORE and len(player_hand.cards) == 2)

    async def handle_player_blackjack(self, gs: dict, player_hand: Hand):
        """Handle immediate Blackjack scenario."""
        logger.info("Handling immediate Blackjack for player.")
        bj_msg = gs["bj_msg"]
        embed  = gs["embed"]
        user_id = gs["user_id"]

        bj_winnings = math.floor(player_hand.bet * self.BLACKJACK_MULTIPLIER)
        self.update_hand_display(embed, player_hand,
                                 status=f"Blackjack! +{bj_winnings} {BANANA_COIN_EMOJI}")
        embed.set_footer(text="Game over!")
        embed.description = f"You win {bj_winnings} {BANANA_COIN_EMOJI}!"
        embed.color = self.WIN_COLOR
        await bj_msg.edit(embed=embed)
        await add_bananas(user_id, bj_winnings)
        logger.info("Blackjack payout of %d bananas awarded to user %s.", bj_winnings, user_id)

    async def handle_player_turns(self, gs: dict):
        """
        Process turns for each player hand.
        """
        logger.debug("Beginning handle_player_turns for all hands.")
        while gs["player_hands"]:
            current_hand = gs["player_hands"].pop(0)
            gs["hands_to_calc"].append(current_hand)
            await self.play_single_hand(gs, current_hand)

    async def play_single_hand(self, gs: dict, hand):
        """
        Plays out a single hand until Stand/Bust/Blackjack.
        """
        logger.debug("Starting turn for hand with initial cards: %s", hand.cards)
        while hand.score <= self.BLACKJACK_SCORE:
            if hand.score == self.BLACKJACK_SCORE:
                logger.debug("Hand reached 21, ending turn.")
                self.update_hand_display(gs["embed"], hand)
                await gs["bj_msg"].edit(embed=gs["embed"])
                break

            # 1) Determine available actions
            actions, footer_text = self.get_available_actions(gs, hand)
            await self.ensure_reactions(gs["bj_msg"], actions)

            # 2) Update embed with the actions
            self.update_hand_display(gs["embed"], hand, active=True)
            gs["embed"].set_footer(text=footer_text)
            await gs["bj_msg"].edit(embed=gs["embed"])

            # 3) Wait for user reaction
            action_info = await self.wait_for_player_action(gs, actions)
            if not action_info:
                logger.warning("Player did not respond in time. Game was abandoned.")
                return

            # 4) Remove reaction and process
            try:
                await gs["bj_msg"].remove_reaction(action_info["react"], action_info["user"])
            except discord.DiscordException as e:
                logger.debug("Failed to remove reaction: %s", e)

            gs["embed"].set_footer(text="Please wait...")
            await gs["bj_msg"].edit(embed=gs["embed"])

            # Perform the chosen action
            stop_hand = await self.process_player_action(gs, hand, action_info["react"])
            if stop_hand:
                logger.debug("Hand ended after action %s.", action_info['react'])
                break

            # 5) Check bust or 21
            if hand.score > self.BLACKJACK_SCORE:
                logger.debug("Hand busted.")
                self.update_hand_display(gs["embed"], hand, status="Bust!")
            elif hand.score == self.BLACKJACK_SCORE:
                logger.debug("Hand reached 21.")
                self.update_hand_display(gs["embed"], hand, active=False)
            else:
                self.update_hand_display(gs["embed"], hand, active=True)

            await gs["bj_msg"].edit(embed=gs["embed"])

    async def process_player_action(self, gs: dict, hand, reaction: str) -> bool:
        """
        Applies the effect of the chosen reaction (Hit, Stand, Double, Split).
        Returns True if the hand should stop after this action, False otherwise.
        """
        logger.debug("Processing action %s for the hand: %s", reaction, hand.cards)
        deck = gs["deck"]
        embed = gs["embed"]

        if reaction == "👊":  # Hit
            card = deck.deal_card()
            hand.add_card(card)
            logger.debug("Player hit and received %s. New hand score: %d.", card, hand.score)
            return False

        if reaction == "🛑":  # Stand
            logger.debug("Player stands.")
            self.update_hand_display(embed, hand)
            await gs["bj_msg"].edit(embed=embed)
            return True

        if reaction == "⏬":  # Double
            gs["bet_amount"] += hand.bet
            hand.bet *= 2
            card = deck.deal_card()
            hand.add_card(card)
            logger.debug("Player doubles down. Dealt %s. New bet: %d.", card, hand.bet)
            embed.description = f"Playing for {gs['bet_amount']} {BANANA_COIN_EMOJI}"
            self.update_hand_display(embed, hand)
            await gs["bj_msg"].edit(embed=embed)
            return True

        if reaction == "🔀":  # Split
            gs["bet_amount"] += hand.bet
            logger.debug("Player splits hand.")
            split_hand = self.Hand(
                [hand.remove_card()],
                bet=hand.bet,
                field_idx=len(embed.fields)
            )
            gs["player_hands"].append(split_hand)

            embed.description = f"Playing for {gs['bet_amount']} {BANANA_COIN_EMOJI}"
            self.update_hand_display(embed, hand, active=True)
            self.update_hand_display(embed, split_hand)
            await gs["bj_msg"].edit(embed=embed)

            hand.add_card(deck.deal_card())
            split_hand.add_card(deck.deal_card())
            logger.debug("Dealt new cards to split hands: %s | %s", hand.cards, split_hand.cards)
            await asyncio.sleep(0.5)

            self.update_hand_display(embed, hand, active=True)
            await gs["bj_msg"].edit(embed=embed)

        # By default, do not stop the hand
        return False

    def get_available_actions(self, gs: dict, hand) -> tuple:
        """
        Determine which actions (hit, stand, double, split) are available.
        Return (actions_list, footer_text).
        """
        actions_list = ["👊", "🛑"]
        footer_text = "Hit (👊) or Stand (🛑)?"

        # Check if we have enough bananas to double or split
        can_double = gs["bet_amount"] + hand.bet <= gs["current_bananas"]
        if can_double:
            actions_list.append("⏬")
            footer_text = "Hit (👊), Stand (🛑), or Double Down (⏬)?"

        # Check if we can split
        if (
            can_double
            and len(gs["player_hands"]) + len(gs["hands_to_calc"]) <= self.SPLIT_LIMIT
            and len(hand.cards) == 2
            and all(
                black_jack_card_values[c.rank] ==
                black_jack_card_values[hand.cards[0].rank]
                for c in hand.cards
            )
        ):
            actions_list.append("🔀")
            footer_text = "Hit (👊), Stand (🛑), Double Down (⏬), or Split (🔀)?"

        return actions_list, footer_text

    async def ensure_reactions(self, bj_msg: discord.Message, actions: list):
        """Ensure the message has the correct reaction buttons."""
        logger.debug("Ensuring reaction buttons for %s", actions)
        existing_reacts = {str(r.emoji) for r in bj_msg.reactions}
        for act in actions:
            if act not in existing_reacts:
                try:
                    await bj_msg.add_reaction(act)
                except discord.DiscordException as e:
                    logger.warning("Failed to add reaction %s: %s", act, e)

    async def wait_for_player_action(self, gs: dict, available_actions: list):
        """
        Wait for the user to pick an action via reaction.
        Return a dict {"react": str, "user": discord.User} or None if timed out.
        """
        bj_msg = gs["bj_msg"]
        user_id = gs["user_id"]
        bet_amt = gs["bet_amount"]
        embed = gs["embed"]
        interaction_user = gs["interaction"].user

        logger.debug("Waiting for player action reaction.")

        try:
            def check(r, u):
                return (
                    u == interaction_user
                    and r.message.id == bj_msg.id
                    and str(r.emoji) in available_actions
                )
            reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
            logger.debug("Player chose reaction %s", reaction.emoji)
            return {"react": str(reaction.emoji), "user": user}
        except asyncio.TimeoutError:
            # Abandon game
            logger.warning("Player reaction timed out. Game abandoned.")
            embed.description = (
                f"YOU LOST YOUR BET OF {bet_amt+1} {BANANA_COIN_EMOJI}! "
                "The bot stole 1 banana for inactivity!"
            )
            embed.set_footer(text="Game abandoned!")
            embed.color = self.LOSE_COLOR
            await bj_msg.edit(embed=embed)
            await remove_bananas(user_id, bet_amt+1)
            return None

    async def handle_dealer_turn(self, gs: dict, dealer_hand: Hand):
        """Dealer draws until reaching stand threshold."""
        logger.debug("Dealer's turn: drawing cards.")
        bj_msg = gs["bj_msg"]
        embed  = gs["embed"]
        deck   = gs["deck"]

        embed.set_footer(text="Dealer's turn...")
        self.update_hand_display(embed, dealer_hand, active=True)
        await bj_msg.edit(embed=embed)

        while dealer_hand.score < self.DEALER_STAND_THRESHOLD:
            await asyncio.sleep(1)
            card = deck.deal_card()
            dealer_hand.add_card(card)
            logger.debug("Dealer drew %s. Dealer score: %d", card, dealer_hand.score)
            if dealer_hand.score > self.BLACKJACK_SCORE:
                self.update_hand_display(embed, dealer_hand, status="Bust!")
            else:
                self.update_hand_display(embed, dealer_hand, active=True)
            await bj_msg.edit(embed=embed)

        self.update_hand_display(embed, dealer_hand, active=False)
        await bj_msg.edit(embed=embed)

    async def calculate_winnings(self, gs: dict, dealer_hand: Hand):
        """Compare each player's hand to the dealer and compute net gain/loss."""
        logger.debug("Calculating final winnings.")
        bj_msg  = gs["bj_msg"]
        embed   = gs["embed"]
        user_id = gs["user_id"]
        hands_to_calc = gs["hands_to_calc"]

        winnings = 0
        for hand in hands_to_calc:
            if hand.score > self.BLACKJACK_SCORE:
                winnings -= hand.bet
                status = f"Bust! -{hand.bet} {BANANA_COIN_EMOJI}"
                logger.debug("Hand bust. Bet lost: %d.", hand.bet)
            elif dealer_hand.score > self.BLACKJACK_SCORE:
                winnings += hand.bet
                status = f"Win! +{hand.bet} {BANANA_COIN_EMOJI}"
                logger.debug("Dealer bust. Player wins bet: %d.", hand.bet)
            elif hand.score > dealer_hand.score:
                winnings += hand.bet
                status = f"Win! +{hand.bet} {BANANA_COIN_EMOJI}"
                logger.debug("Player wins against dealer. Gains: %d.", hand.bet)
            elif hand.score < dealer_hand.score:
                winnings -= hand.bet
                status = f"Loss! -{hand.bet} {BANANA_COIN_EMOJI}"
                logger.debug("Player loses against dealer. Loses: %d.", hand.bet)
            else:
                status = "Push!"
                logger.debug("Push with dealer. No change for bet %d.", hand.bet)

            self.update_hand_display(embed, hand, status=status)

        if winnings > 0:
            embed.color = self.WIN_COLOR
            embed.description = f"You win {winnings} {BANANA_COIN_EMOJI}!"
            await add_bananas(user_id, winnings)
            logger.info("User %s wins %d bananas.", user_id, winnings)
        elif winnings < 0:
            embed.color = self.LOSE_COLOR
            embed.description = f"You lose {abs(winnings)} {BANANA_COIN_EMOJI}!"
            await remove_bananas(user_id, abs(winnings))
            logger.info("User %s loses %d bananas.", user_id, abs(winnings))
        else:
            embed.description = "No winnings or losses!"
            embed.color = self.PUSH_COLOR
            logger.info("User %s ends in a push with no net change.", user_id)

        embed.set_footer(text="Game over!")
        await bj_msg.edit(embed=embed)


async def setup(bot):
    await bot.add_cog(BlackjackCog(bot))
