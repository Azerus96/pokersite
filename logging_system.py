import logging
import logging.handlers

class Logger:
    def __init__(self, log_file="tournament_log.txt", max_log_size=10 * 1024 * 1024, backup_count=5):
        handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=max_log_size, backupCount=backup_count)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.hasHandlers():
            self.logger.addHandler(handler)

    def log_event(self, message):
        self.logger.info(message)

    def log_decision(self, player_name, decision, game_state):
        current_bet = game_state.get("current_bet", 0)
        stack = game_state.get("current_player").stack if game_state.get("current_player") else "-"
        community_cards = ', '.join([f"{rank} of {suit}" for rank, suit in game_state.get("community_cards", [])])
        self.logger.debug(f"{player_name} принимает решение {decision}, текущая ставка: {current_bet}, общие карты: {community_cards}")

    def log_result(self, winner_name, pot):
        self.logger.info(f"{winner_name} выиграл банк в {pot}")
