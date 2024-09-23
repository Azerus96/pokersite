import sqlite3
import pickle  # Для сериализации сложных объектов (например, карт)

class TournamentDatabase:
    def __init__(self, db_name="tournament_results.db"):
        """Инициализация базы данных и создание таблиц, если они ещё не существуют."""
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        """Создание таблиц для игроков, игр и турниров."""
        with self.conn:
            # Таблица игроков
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    stack INTEGER NOT NULL,
                    hole_cards BLOB
                )
            ''')
            
            # Таблица решений игроков в играх
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER NOT NULL,
                    decision TEXT NOT NULL,
                    profit INTEGER NOT NULL,
                    FOREIGN KEY (player_id) REFERENCES players(id)
                )
            ''')
            
            # Таблица состояния турнира
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS tournaments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    round INTEGER NOT NULL,
                    pot INTEGER NOT NULL,
                    community_cards BLOB
                )
            ''')

    def save_player(self, player):
        """Сохранение игрока в базу данных."""
        with self.conn:
            # Сериализуем карты игрока
            hole_cards_blob = pickle.dumps(player.hole_cards)
            cur = self.conn.execute('''
                INSERT INTO players (name, stack, hole_cards) 
                VALUES (?, ?, ?)
            ''', (player.name, player.stack, hole_cards_blob))
            return cur.lastrowid  # Возвращаем ID вставленного игрока

    def save_game(self, player_id, decision, profit):
        """Сохранение решения игрока в конкретной игре."""
        with self.conn:
            self.conn.execute('''
                INSERT INTO games (player_id, decision, profit) 
                VALUES (?, ?, ?)
            ''', (player_id, decision, profit))

    def save_tournament_state(self, round_number, pot, community_cards):
        """Сохранение состояния турнира (раунд, банк, общие карты)."""
        with self.conn:
            community_cards_blob = pickle.dumps(community_cards)
            self.conn.execute('''
                INSERT INTO tournaments (round, pot, community_cards) 
                VALUES (?, ?, ?)
            ''', (round_number, pot, community_cards_blob))

    def fetch_player_stats(self, player_name):
        """Получение статистики игрока по имени."""
        with self.conn:
            player_stats = self.conn.execute('''
                SELECT * FROM players WHERE name=?
            ''', (player_name,)).fetchall()
        return player_stats if player_stats else None

    def load_players(self):
        """Загрузка всех игроков из базы данных."""
        with self.conn:
            players = []
            for row in self.conn.execute("SELECT id, name, stack, hole_cards FROM players"):
                player_id, name, stack, hole_cards_blob = row
                hole_cards = pickle.loads(hole_cards_blob)  # Десериализуем карты
                player = PokerPlayer(name=name, stack=stack)
                player.hole_cards = hole_cards
                players.append((player_id, player))
            return players

    def load_tournament_state(self):
        """Загрузка состояния последнего турнира из базы данных."""
        with self.conn:
            row = self.conn.execute('''
                SELECT round, pot, community_cards 
                FROM tournaments 
                ORDER BY id DESC LIMIT 1
            ''').fetchone()
            
            if row:
                round_number, pot, community_cards_blob = row
                community_cards = pickle.loads(community_cards_blob)  # Десериализуем общие карты
                return round_number, pot, community_cards
        return None

    def close(self):
        """Закрытие соединения с базой данных."""
        self.conn.close()
