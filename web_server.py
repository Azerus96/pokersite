from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO
import asyncio
from player import PokerPlayer
from poker_game import PokerGame, setup_tournament
from mccfr import MCCFR
from logging_system import Logger
import os

app = Flask(__name__)
socketio = SocketIO(app)

# Создаём объект турнира (глобальная переменная)
tournament = None
logger = Logger()

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Страница турнира
@app.route('/tournament')
def tournament_page():
    return render_template('tournament.html')

# Страница регистрации игрока
@app.route('/register', methods=['POST', 'GET'])
def register():
    global tournament
    if request.method == 'POST':
        player_name = request.form['player_name']
        new_player = PokerPlayer(name=player_name, stack=10000, use_mccfr=False)  # Реальный игрок
        tournament.players.append(new_player)  # Добавляем игрока к текущему турниру
        logger.log_event(f"Player {player_name} зарегистрирован.")
        return redirect('/tournament')

    return render_template('player.html')

# Функция для отправки состояния турнира через WebSockets
def update_tournament_state(state):
    socketio.emit('update_tournament', state)

# Событие, когда реальный игрок делает действие через WebSocket
@socketio.on('player_action')
def handle_player_action(data):
    global tournament
    player_name = data['player_name']
    action = data['action']
    raise_value = data.get('raise', 0)

    # Логика выполнения действий игрока
    for player in tournament.players:
        if player.name == player_name:
            if action == 'fold':
                logger.log_event(f"Player {player_name} folded.")
            elif action == 'call':
                logger.log_event(f"Player {player_name} called.")
            elif action == 'raise':
                logger.log_event(f"Player {player_name} raised by {raise_value}.")
            break

    # Обновление состояния игры через WebSocket
    update_tournament_state(tournament.get_table_state())

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
    tournament = setup_tournament(num_players=160, mccfr_strategy=mccfr_strategy)

    # Запускаем симуляцию турнира в отдельном асинхронном процессе
    asyncio.run(tournament.simulate_tournament())

    # Запускаем веб-сервер для взаимодействия через браузер
    start_flask()
