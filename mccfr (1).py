import random
from collections import defaultdict
import pickle  # Для сохранения и загрузки стратегии


class MCCFR:
    def __init__(self, iterations=1000):
        """
        Инициализация MCCFR.
        iterations: количество итераций для тренировки (по умолчанию 1000)
        """
        self.iterations = iterations
        self.strategy = defaultdict(lambda: [0, 0])  # Хранение [регреты, кумулятивная стратегия]

    def run_iterations(self, game_history, iterations=None):
        """
        Запуск серии итераций MCCFR для улучшения стратегии.
        game_history: история игры
        iterations: количество итераций (если None, используется default)
        """
        if iterations is None:
            iterations = self.iterations

        for _ in range(iterations):
            self.run_simulation(game_history)

    def run_simulation(self, game_history):
        """
        Запуск симуляции решения.
        Проход по всем возможным действиям: fold, call, raise.
        """
        actions = ['fold', 'call', 'raise']
        for action in actions:
            self.update_regret(game_history, action)

    def update_regret(self, game_history, action):
        """
        Обновление регрета для выбранного действия.
        game_history: история игры
        action: действие (fold, call, raise)
        """
        action_probability = self.calculate_action_probability(action)
        regret = self.calculate_regret(game_history, action)
        self.strategy[action][0] += regret  # Обновление регретов
        self.strategy[action][1] += action_probability  # Обновление кумулятивной стратегии

    def calculate_action_probability(self, action):
        """
        Рассчитать вероятность выполнения действия на основе текущих регретов.
        action: действие (fold, call, raise)
        """
        cumulative = sum(max(self.strategy[a][0], 0) for a in self.strategy)
        if cumulative > 0:
            return max(self.strategy[action][0], 0) / cumulative
        return 1.0 / len(self.strategy)  # Равная вероятность, если нет регретов

    def calculate_regret(self, game_history, action):
        """
        Рассчитать регрет для данного действия.
        game_history: история игры
        action: действие (fold, call, raise)
        """
        payoffs = self.get_payoffs_for_actions(game_history)
        expected_payoff = sum(payoffs[a] * self.calculate_action_probability(a)
                              for a in ['fold', 'call', 'raise'])
        return payoffs[action] - expected_payoff

    def get_payoffs_for_actions(self, game_history):
        """
        Получение ожидаемой выгоды для каждого действия.
        game_history: история игры
        """
        current_bet = game_history[-1]["current_bet"]
        return {
            'fold': -current_bet,
            'call': random.randint(-current_bet, current_bet),
            'raise': random.randint(current_bet, 2 * current_bet),
        }

    def decide(self, game_state, dossier):
        """
        Принятие решения на основе выработанной MCCFR стратегии.
        game_state: текущее состояние игры
        dossier: данные о поведении оппонентов
        """
        self.run_iterations(game_state)  # Тренировка на основе текущего состояния игры.
        return max(self.strategy, key=lambda x: self.strategy[x][1])  # Наиболее вероятное действие

    def save_strategy(self, file_name='mccfr_strategy.pkl'):
        """
        Сохранение MCCFR стратегии в файл, чтобы загрузить позже или перенести на другой турнир.
        file_name: имя файла (по умолчанию 'mccfr_strategy.pkl')
        """
        with open(file_name, 'wb') as f:
            pickle.dump(self.strategy, f)
        print(f"Общая стратегия MCCFR сохранена в файл: {file_name}")

    def load_strategy(self, file_name='mccfr_strategy.pkl'):
        """
        Загрузка ранее сохранённой MCCFR стратегии из файла.
        file_name: имя файла для загрузки стратегии
        """
        with open(file_name, 'rb') as f:
            self.strategy = pickle.load(f)
        print(f"Общая стратегия MCCFR загружена из файла: {file_name}")