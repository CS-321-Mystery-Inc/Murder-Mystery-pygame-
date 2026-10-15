
import sqlite3

DB_NAME = "game.db"

def initialize_database():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS evidence (
                evidence_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                collected_by TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS game_state (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

def collect_evidence(id, name, description, player):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            INSERT OR IGNORE INTO evidence
            VALUES (?, ?, ?, ?)
        """, (id, name, description, player))

def get_evidence():
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute(
            "SELECT * FROM evidence"
        ).fetchall()

def update_game_state(key, value):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            INSERT OR REPLACE INTO game_state
            VALUES (?, ?)
        """, (key, value))
