import os
import asyncio
from config import PokerTournamentConfig
from player import PokerPlayer
from poker_game import PokerGame, setup_tournament
from logging_system import Logger
from database import TournamentDatabase
from mccfr import MCCFR

async def main():
    num_players = 160 
    logger = Logger() 
    db = TournamentDatabase()  

    load_previous_state = False  

    mccfr_strategy = MCCFR()
    if load_previous_state and os.path.exists('mccfr_strategy.pkl'):
        mccfr_strategy.load_strategy('mccfr_strategy.pkl')
    
    game = setup_tournament(num_players=num_players, load_previous_state=load_previous_state, mccfr_strategy=mccfr_strategy)

    logger.log_event("Tournament started")

    try:
        await game.simulate_tournament()

        for player in game.players:
            logger.log_event(f"{player.name} закончил игру со стеком {player.stack}")
            player.save_state()

        mccfr_strategy.save_strategy('mccfr_strategy.pkl')
        logger.log_event("MCCFR стратегия сохранена.")

        logger.log_event("Tournament finished")

    except Exception as e:
        logger.log_event(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
