from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tournament')
def tournament_page():
    return render_template('tournament.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    global tournament
    if request.method == 'POST':
        player_name = request.form['player_name']
        new_player = PokerPlayer(name=player_name, stack=10000)
        tournament.players.append(new_player)
        logger.log_event(f"Player {player_name} зарегистрирован.")
        return redirect('/tournament')

    return render_template('player.html')

def update_tournament_state(state):
    socketio.emit('update_tournament', state)

@socketio.on('player_action')
def handle_player_action(data):
    global tournament
    player_name = data['player_name']
    action = data['action']
    raise_value = data.get('raise', 0)

    for player in tournament.players:
        if player.name == player_name:
            if action == 'fold':
                logger.log_event(f"Player {player_name} folded.")
            elif action == 'call':
                logger.log_event(f"Player {player_name} called.")
            elif action == 'raise':
                logger.log_event(f"Player {player_name} raised by {raise_value}.")
            break

    update_tournament_state(tournament.get_table_state())

def start_flask():
    socketio.run(app, host='0.0.0.0', port=10000)

if __name__ == "__main__":
    mccfr_strategy = MCCFR()
    if os.path.exists('mccfr_strategy.pkl'):
        mccfr_strategy.load_strategy('mccfr_strategy.pkl')

    tournament = setup_tournament(num_players=160, mccfr_strategy=mccfr_strategy)

    # Запуск веб-сервера для взаимодействия через браузер
    start_flask()
