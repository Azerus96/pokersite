import random
import asyncio
import pickle
from logging_system import Logger
from hand_evaluator import HandEvaluator
from config import PokerTournamentConfig

class PokerGame:
    def __init__(self, players, config, mccfr_strategy=None):
        self.players = players
        self.config = config
        self.current_round = 1
        self.pot = 0
        self.tables = self.create_tables()
        self.community_cards = []
        self.deck = self.create_deck()
        self.logger = Logger()
        self.mccfr_strategy = mccfr_strategy

    def create_tables(self):
        players_per_table = 8
        num_tables = len(self.players) // players_per_table
        tables = [self.players[i * players_per_table:(i + 1) * players_per_table] for i in range(num_tables)]
        return tables

    def create_deck(self):
        ranks = list(range(2, 11)) + ['J', 'Q', 'K', 'A']
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        deck = [(rank, suit) for rank in ranks for suit in suits]
        random.shuffle(deck)
        return deck

    def deal_hole_cards(self, table):
        for player in table:
            player.hole_cards = [self.deck.pop(), self.deck.pop()]
            self.logger.log_event(f"{player.name} получил карты {player.hole_cards}")

    def deal_community_cards(self, number):
        for _ in range(number):
            card = self.deck.pop()
            self.community_cards.append(card)
            self.logger.log_event(f"Добавлена общая карта: {card}")

    async def play_one_table(self, table, blinds):
        self.collect_blinds(table, blinds)
        self.deal_hole_cards(table)
        await self.conduct_betting_round(table, "Pre-Flop")
        self.deck.pop()

        self.deal_community_cards(3)
        await self.conduct_betting_round(table, "Flop")
        self.deck.pop()

        self.deal_community_cards(1)
        await self.conduct_betting_round(table, "Turn")
        self.deck.pop()

        self.deal_community_cards(1)
        await self.conduct_betting_round(table, "River")

        winner = self.showdown(table)
        if winner:
            self.award_pot_to_winner(winner)

    def collect_blinds(self, table, blinds):
        small_blind, big_blind = blinds['small_blind'], blinds['big_blind']
        table[0].stack -= small_blind
        table[1].stack -= big_blind
        self.pot += small_blind + big_blind

    async def conduct_betting_round(self, table, stage):
        for player in table:
            game_state = {
                "current_bet": random.randint(10, 100),
                "current_player": player,
                "community_cards": self.community_cards
            }

            decision = player.make_decision(game_state, mccfr_strategy=self.mccfr_strategy)
            self.logger.log_decision(player.name, decision, game_state)

            if decision == "call":
                self.pot += game_state["current_bet"]
            elif decision == "raise":
                raise_amount = random.randint(10, 100)
                self.pot += raise_amount

            await asyncio.sleep(0.1)

    def showdown(self, table):
        hands = {player: player.hole_cards + self.community_cards for player in table}

        best_hand_value = None
        best_player = None

        for player, hand in hands.items():
            hand_value = HandEvaluator.evaluate_hand(hand)
            if not best_hand_value or HandEvaluator.compare_hands(hand, best_hand_value[1]) > 0:
                best_hand_value = (player, hand)

        return best_hand_value[0] if best_hand_value else None

    def award_pot_to_winner(self, winner):
        winner.stack += self.pot
        self.pot = 0

    async def simulate_tournament(self):
        while len(self.players) > 1:
            await self.play_round()
            self.current_round += 1

        if len(self.players) == 1:
            self.logger.log_event(f"Победитель турнира: {self.players[0].name} со стеком {self.players[0].stack}")

        if self.mccfr_strategy:
            self.mccfr_strategy.save_strategy()

    async def play_round(self):
        self.deck = self.create_deck()
        blinds = self.config.get_blinds_for_round(self.current_round)

        await asyncio.gather(*[self.play_one_table(table, blinds) for table in self.tables])

        tournament_state = {
            'tables': self.get_table_state()
        }
        from web_server import update_tournament_state
        update_tournament_state(tournament_state)

    def get_table_state(self):
        tables_state = []
        for table in self.tables:
            table_info = {
                'players': [{'name': player.name, 'stack': player.stack, 'cards': player.hole_cards} for player in table]
            }
            tables_state.append(table_info)
        return tables_state

def setup_tournament(num_players=160, load_previous_state=False, mccfr_strategy=None):
    config = PokerTournamentConfig()

    players = []
    for i in range(num_players):
        player_name = f"Player_{i+1}"

        player = PokerPlayer(player_name, config.starting_stack, use_mccfr=True, mccfr_strategy=mccfr_strategy)

        if load_previous_state and os.path.exists(f"{player_name}_state.pkl"):
            player.load_state(f"{player_name}_state.pkl")

        players.append(player)

    return PokerGame(players, config)
