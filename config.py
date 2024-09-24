class PokerTournamentConfig:
    def __init__(self):
        self.round_duration_minutes = 6
        self.initial_blinds_structure = {
            1: {'small_blind': 50, 'big_blind': 100, 'ante': 10},
            2: {'small_blind': 100, 'big_blind': 200, 'ante': 20},
            # ... (остальные раунды)
        }
        self.blinds_structure = self.initial_blinds_structure.copy()
        self.starting_stack = 10000
        self.payout_structure = {1: 0.5, 2: 0.3, 3: 0.2}
        self.additional_rounds = 0

    def get_blinds_for_round(self, round_number):
        if round_number in self.blinds_structure:
            return self.blinds_structure[round_number]
        
        last_round = max(self.blinds_structure.keys())
        if round_number > last_round:
            self.additional_rounds += 1
            new_blinds = {key: value * 2 for key, value in self.blinds_structure[last_round].items()}
            self.blinds_structure[round_number] = new_blinds
            return new_blinds
        else:
            raise ValueError(f"Round {round_number} out of range!")

    def get_payouts(self, prize_pool):
        return {position: prize_pool * percentage for position, percentage in self.payout_structure.items()}

    def validate_configuration(self):
        if not isinstance(self.blinds_structure, dict) or not self.blinds_structure:
            raise ValueError("Некорректная структура блайндов")
        if not isinstance(self.starting_stack, int) or self.starting_stack <= 0:
            raise ValueError("Начальный стек должен быть положительным целым числом")

    def dynamic_adjustment(self, current_round):
        if current_round > 5:
            self.mccfr_iterations = int(self.mccfr_iterations * 1.5)  # Увеличением итераций на 50%
