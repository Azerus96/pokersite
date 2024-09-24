import random
from collections import defaultdict
import pickle

class MCCFR:
    def __init__(self, iterations=1000):
        self.iterations = iterations
        self.strategy = defaultdict(lambda: [0, 0])  # [регреты, кумулятивная стратегия]

    def run_iterations(self, game_history):
        for _ in range(self.iterations):
            self.run_simulation(game_history)

    def run_simulation(self, game_history):
        actions = ['fold', 'call', 'raise']
        for action in actions:
            self.update_regret(game_history, action)

    def update_regret(self, game_history, action):
        action_probability = self.calculate_action_probability(action)
        regret = self.calculate_regret(game_history, action)
        self.strategy[action][0] += regret
        self.strategy[action][1] += action_probability

    def calculate_action_probability(self, action):
        cumulative = sum(max(self.strategy[a][0], 0) for a in self.strategy)
        return max(self.strategy[action][0], 0) / cumulative if cumulative > 0 else 1.0 / len(self.strategy)

    def calculate_regret(self, game_history, action):
        payoffs = self.get_payoffs_for_actions(game_history)
        expected_payoff = sum(payoffs[a] * self.calculate_action_probability(a) for a in ['fold', 'call', 'raise'])
        return payoffs[action] - expected_payoff

    def get_payoffs_for_actions(self, game_history):
        # Логика получения выгоды для действий
        return {
            'fold': -game_history[-1]["current_bet"],
            'call': random.randint(-game_history[-1]["current_bet"], game_history[-1]["current_bet"]),
            'raise': random.randint(game_history[-1]["current_bet"], 2 * game_history[-1]["current_bet"]),
        }

    def decide(self, game_state):
        self.run_iterations(game_state)
        return max(self.strategy, key=lambda x: self.strategy[x][1])

    def save_strategy(self, file_name='mccfr_strategy.pkl'):
        with open(file_name, 'wb') as f:
            pickle.dump(self.strategy, f)
        print(f"Стратегия MCCFR сохранена: {file_name}")

    def load_strategy(self, file_name='mccfr_strategy.pkl'):
        with open(file_name, 'rb') as f:
            self.strategy = pickle.load(f)
            print(f"Стратегия MCCFR загружена: {file_name}")
