import random
import asyncio
import pickle
from logging_system import Logger
from hand_evaluator import HandEvaluator
from web_server import update_tournament_state  # Для обновления данных в реальном времени

class PokerGame:
    def __init__(self, players, config, mccfr_strategy=None):
        """
        Инициализация покерного турнира.

        players: список объектов игроков
        config: конфигурации турнира
        mccfr_strategy: общая стратегия MCCFR для всех игроков
        """
        self.players = players
        self.config = config
        self.current_round = 1
        self.pot = 0
        self.tables = self.create_tables()
        self.community_cards = []
        self.deck = self.create_deck()
        self.logger = Logger()
        self.mccfr_strategy = mccfr_strategy  # Использование единой стратегии MCCFR

    def create_tables(self):
        """Создание столов для турнира"""
        players_per_table = 8
        num_tables = len(self.players) // players_per_table

        tables = []
        for i in range(num_tables):
            table = self.players[i * players_per_table:(i + 1) * players_per_table]
            tables.append(table)
        return tables

    def create_deck(self):
        """Создание новой колоды"""
        ranks = list(range(2, 11)) + ['J', 'Q', 'K', 'A']
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        deck = [(rank, suit) for rank in ranks for suit in suits]
        random.shuffle(deck)
        return deck

    def deal_hole_cards(self, table):
        """Раздача карт каждому игроку за столом"""
        for player in table:
            player.hole_cards = [self.deck.pop(), self.deck.pop()]
            self.logger.log_event(f"{player.name} получил карты {player.hole_cards}")

    def deal_community_cards(self, number):
        """Выкладка общих карт на стол"""
        for _ in range(number):
            card = self.deck.pop()
            self.community_cards.append(card)
            self.logger.log_event(f"Добавлена общая карта: {card}")

    async def play_one_table(self, table, blinds):
        """Игровой процесс для одного стола"""
        self.collect_blinds(table, blinds)
        self.deal_hole_cards(table)
        await self.conduct_betting_round(table, "Pre-Flop")
        self.deck.pop()  # "Сжигание" карты

        # Флоп: три общие карты
        self.deal_community_cards(3)
        await self.conduct_betting_round(table, "Flop")
        self.deck.pop()

        # Терн: четвёртая общая карта
        self.deal_community_cards(1)
        await self.conduct_betting_round(table, "Turn")
        self.deck.pop()

        # Ривер: пятая общая карта
        self.deal_community_cards(1)
        await self.conduct_betting_round(table, "River")

        winner = self.showdown(table)
        if winner:
            self.award_pot_to_winner(winner)

    def collect_blinds(self, table, blinds):
        """Сбор блайндов от игроков за столом"""
        small_blind, big_blind = blinds['small_blind'], blinds['big_blind']
        table[0].stack -= small_blind
        table[1].stack -= big_blind
        self.pot += small_blind + big_blind

    async def conduct_betting_round(self, table, stage):
        """Проведение одного круга ставок каждого игрока"""
        for player in table:
            game_state = {
                "current_bet": random.randint(10, 100),
                "current_player": player,
                "community_cards": self.community_cards
            }

            # Игрок использует общую стратегию MCCFR
            decision = player.make_decision(game_state, mccfr_strategy=self.mccfr_strategy)
            self.logger.log_decision(player.name, decision, game_state)

            if decision == "call":
                self.pot += game_state["current_bet"]
            elif decision == "raise":
                raise_amount = random.randint(10, 100)
                self.pot += raise_amount

            await asyncio.sleep(0)

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
        """Передача выигрыша победителю"""
        winner.stack += self.pot
        self.pot = 0

    async def simulate_tournament(self):
        """Запуск симуляции турнира"""
        while len(self.players) > 1:
            await self.play_round()
            self.current_round += 1

        # Определение победителя
        if len(self.players) == 1:
            self.logger.log_event(f"Победитель турнира: {self.players[0].name} со стеком {self.players[0].stack}")

        # Сохранение стратегии MCCFR после завершения турнира
        if self.mccfr_strategy:
            self.mccfr_strategy.save_strategy()

    async def play_round(self):
        """Один полный раунд игры"""
        self.deck = self.create_deck()
        blinds = self.config.get_blinds_for_round(self.current_round)

        await asyncio.gather(*[self.play_one_table(table, blinds) for table in self.tables])

        # Определение новых столов после окончания раунда (если кто-то вылетел)
        self.reorganize_tables()

        # Обновление состояния турнира на фронте
        tournament_state = {
            'tables': self.get_table_state()
        }
        update_tournament_state(tournament_state)

    def get_table_state(self):
        """Получение текущего состояния стола для отображения на фронте"""
        tables_state = []
        for table in self.tables:
            table_info = {
                'players': [{'name': player.name, 'stack': player.stack, 'cards': player.hole_cards} for player in table]
            }
            tables_state.append(table_info)
        return tables_state
