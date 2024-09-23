import os
import asyncio
from config import PokerTournamentConfig
from player import PokerPlayer
from poker_game import PokerGame
from logging_system import Logger
from database import TournamentDatabase
from utils import generate_player_name
from web_server import update_tournament_state  # Для обновления состояния через WebSocket
from mccfr import MCCFR  # Импорт MCCFR для использования

# Настройки турнира
def setup_tournament(num_players=160, load_previous_state=False, mccfr_strategy=None):
    """
    Инициализация турнира (создание игроков и настройка игры).
    Использование общего объекта MCCFR стратегии для всех ИИ-игроков.

    num_players: количество игроков
    load_previous_state: если True, загружаются прошлые состояния
    mccfr_strategy: общая MCCFR стратегия для ботов
    """
    config = PokerTournamentConfig()

    players = []
    for i in range(num_players):
        player_name = generate_player_name()

        # Бот использует MCCFR стратегию, если она передана
        player = PokerPlayer(player_name, config.starting_stack, use_mccfr=True, mccfr_strategy=mccfr_strategy)

        # Загружаем предыдущее состояние игроков, если это требуется
        if load_previous_state and os.path.exists(f"{player_name}_state.pkl"):
            player.load_state(f"{player_name}_state.pkl")

        players.append(player)

    return PokerGame(players, config)

# Основная функция турнира
async def main():
    num_players = 160  # Количество игроков
    logger = Logger()  # Запуск логгера
    db = TournamentDatabase()  # Инициализация базы данных для турнира

    load_previous_state = False  # Если True, загружаем прошлые состояния игроков

    # Создаем MCCFR стратегию и проверяем, была ли она сохранена ранее
    mccfr_strategy = MCCFR()
    if load_previous_state and os.path.exists('mccfr_strategy.pkl'):
        mccfr_strategy.load_strategy('mccfr_strategy.pkl')
    else:
        print("Создаётся новая MCCFR стратегия")

    # Настройка турнира: передаем стратегию MCCFR ботам
    game = setup_tournament(num_players=num_players, load_previous_state=load_previous_state, mccfr_strategy=mccfr_strategy)

    logger.log_event("Tournament started")

    try:
        # Запускаем симуляцию турнира (асинхронно)
        await game.simulate_tournament()

        # Логирование и сохранение данных игроков по завершении
        for player in game.players:
            logger.log_event(f"{player.name} закончил игру со стеком {player.stack}")
            player.save_state()

        # Сохранение MCCFR стратегии после завершения турнира
        mccfr_strategy.save_strategy('mccfr_strategy.pkl')
        logger.log_event("MCCFR стратегия сохранена.")

        logger.log_event("Tournament finished")

    except Exception as e:
        logger.log_event(f"An error occurred: {str(e)}")