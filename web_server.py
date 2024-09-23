from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO
import asyncio
from app import main  # Импорт основной логики игры (турнир и MCCFR)
from poker_game import PokerGame
from player import PokerPlayer
from mccfr import MCCFR  # Импорт MCCFR для использования

import os

app = Flask(__name__)
socketio = SocketIO(app)

# Создаём объект турнира (глобальная переменная для примера)
current_game = None

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Лобби турнира
@app.route('/tournament')
def tournament():
    return render_template('tournament.html')

# Страница регистрации игрока (реальный игрок)
@app.route('/register', methods=['POST', 'GET'])
def register():
    global current_game

    if request.method == 'POST':
        player_name = request.form['player_name']
        new_player = PokerPlayer(name=player_name, stack=10000, use_mccfr=False)  # Реальный игрок
        current_game.add_player(new_player)  # Добавляем игрока к текущему турниру
        return redirect('/tournament')

    return render_template('player.html')

# Функция для отправки состояния турнира через WebSockets
def update_tournament_state(state):
    socketio.emit('update_tournament', state)

# Событие, когда реальный игрок делает действие (например, fold, call, raise)
@socketio.on('player_action')
def handle_player_action(data):
    action = data['action']
    raise_value = data.get('raise', 0)

    # Логика выполнения действий игрока
    if action == 'fold':
        print(f"Player folded.")
        # current_game.fold(player)  # Пример вызова метода игры
    elif action == 'call':
        print(f"Player called.")
    elif action == 'raise':
        print(f"Player raised by {raise_value}.")

    # Обновление состояния игры (передача через WebSocket)
    update_tournament_state(current_game.get_table_state())

# Асинхронный запуск Flask
def start_flask():
    socketio.run(app, host='0.0.0.0', port=10000)

# Основной запуск турнира и веб-сервера
if __name__ == "__main__":
    # Создаём общий объект стратегии MCCFR для всех ботов
    mccfr_strategy = MCCFR()

    # Загрузка MCCFR стратегии, если она существует
    if os.path.exists('mccfr_strategy.pkl'):
        mccfr_strategy.load_strategy('mccfr_strategy.pkl')

    # Создаём новый турнир с MCCFR стратегией
    current_game = PokerGame(setup_tournament(num_players=160, mccfr_strategy=mccfr_strategy),
                             PokerTournamentConfig())

    # Запускаем симуляцию турнира в отдельном асинхронном процессе
    asyncio.run(main())

    # Запускаем веб-сервер для взаимодействия через браузер
    start_flask()