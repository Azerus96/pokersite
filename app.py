import os
import asyncio
from config import PokerTournamentConfig
from player import PokerPlayer
from poker_game import PokerGame, setup_tournament
from logging_system import Logger
from database import TournamentDatabase
from mccfr import MCCFR

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

if __name__ == "__main__":
    asyncio.run(main())
