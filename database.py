import sqlite3
import pickle

class TournamentDatabase:
    def __init__(self, db_name="tournament_results.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                stack INTEGER NOT NULL,
                hole_cards BLOB
            )''')
            self.conn.execute('''CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                decision TEXT NOT NULL,
                profit INTEGER NOT NULL,
                FOREIGN KEY (player_id) REFERENCES players(id)
            )''')
            self.conn.execute('''CREATE TABLE IF NOT EXISTS tournaments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                round INTEGER NOT NULL,
                pot INTEGER NOT NULL,
                community_cards BLOB
            )''')

    def save_player(self, player):
        with self.conn:
            hole_cards_blob = pickle.dumps(player.hole_cards)
            cur = self.conn.execute('''INSERT INTO players (name, stack, hole_cards) 
                                       VALUES (?, ?, ?)''', (player.name, player.stack, hole_cards_blob))
            return cur.lastrowid

    def fetch_player_stats(self, player_name):
        with self.conn:
            player_stats = self.conn.execute('SELECT * FROM players WHERE name=?', (player_name,)).fetchall()
        return player_stats if player_stats else None

    def close(self):
        self.conn.close()
