"""Database management for player accounts and game data."""
import sqlite3
from datetime import datetime
from pathlib import Path
from .encryption import PasswordEncryption
import config

class DatabaseManager:
    """Manage all database operations."""
    
    def __init__(self, db_path: str = config.DB_PATH):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database tables."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Players table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                level INTEGER DEFAULT 1,
                total_coins INTEGER DEFAULT 0,
                total_wins INTEGER DEFAULT 0,
                total_games INTEGER DEFAULT 0,
                current_character TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Game stats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                game_mode TEXT NOT NULL,
                kills INTEGER DEFAULT 0,
                deaths INTEGER DEFAULT 0,
                assists INTEGER DEFAULT 0,
                beds_destroyed INTEGER DEFAULT 0,
                coins_earned INTEGER DEFAULT 0,
                placement INTEGER,
                team_size INTEGER,
                game_duration INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player_id) REFERENCES players(id)
            )
        """)
        
        # Owned characters table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS owned_characters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                character_name TEXT NOT NULL,
                purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player_id) REFERENCES players(id),
                UNIQUE(player_id, character_name)
            )
        """)
        
        # Cosmetics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS owned_cosmetics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                cosmetic_name TEXT NOT NULL,
                purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player_id) REFERENCES players(id),
                UNIQUE(player_id, cosmetic_name)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_account(self, username: str, password: str, email: str = None) -> bool:
        """Create a new player account."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            password_hash = PasswordEncryption.hash_password(password)
            cursor.execute("""
                INSERT INTO players (username, password_hash, email)
                VALUES (?, ?, ?)
            """, (username, password_hash, email))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def authenticate_player(self, username: str, password: str) -> dict:
        """Authenticate player and return player data."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM players WHERE username = ?", (username,))
        player = cursor.fetchone()
        conn.close()
        
        if player and PasswordEncryption.verify_password(password, player['password_hash']):
            return dict(player)
        return None
    
    def get_player(self, player_id: int) -> dict:
        """Get player by ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM players WHERE id = ?", (player_id,))
        player = cursor.fetchone()
        conn.close()
        return dict(player) if player else None
    
    def update_player_coins(self, player_id: int, coins: int) -> bool:
        """Add coins to player account."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE players SET total_coins = total_coins + ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (coins, player_id))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def purchase_character(self, player_id: int, character_name: str, cost: int) -> bool:
        """Purchase a character."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if player has enough coins
            cursor.execute("SELECT total_coins FROM players WHERE id = ?", (player_id,))
            player = cursor.fetchone()
            
            if not player or player['total_coins'] < cost:
                conn.close()
                return False
            
            # Deduct coins and add character
            cursor.execute("""
                UPDATE players SET total_coins = total_coins - ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (cost, player_id))
            
            cursor.execute("""
                INSERT INTO owned_characters (player_id, character_name)
                VALUES (?, ?)
            """, (player_id, character_name))
            
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def record_game_stats(self, player_id: int, game_mode: str, stats: dict) -> bool:
        """Record game statistics."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO game_stats 
                (player_id, game_mode, kills, deaths, assists, beds_destroyed, coins_earned, placement, team_size, game_duration)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                player_id,
                game_mode,
                stats.get('kills', 0),
                stats.get('deaths', 0),
                stats.get('assists', 0),
                stats.get('beds_destroyed', 0),
                stats.get('coins_earned', 0),
                stats.get('placement', 0),
                stats.get('team_size', 0),
                stats.get('game_duration', 0)
            ))
            
            # Update player stats
            if stats.get('placement', 0) == 1:
                cursor.execute("UPDATE players SET total_wins = total_wins + 1 WHERE id = ?", (player_id,))
            
            cursor.execute("UPDATE players SET total_games = total_games + 1 WHERE id = ?", (player_id,))
            cursor.execute("""
                UPDATE players SET total_coins = total_coins + ?
                WHERE id = ?
            """, (stats.get('coins_earned', 0), player_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error recording game stats: {e}")
            return False
    
    def get_player_stats(self, player_id: int) -> list:
        """Get all game stats for a player."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM game_stats WHERE player_id = ? ORDER BY created_at DESC", (player_id,))
        stats = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return stats
    
    def get_player_characters(self, player_id: int) -> list:
        """Get all characters owned by a player."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT character_name FROM owned_characters WHERE player_id = ?", (player_id,))
        characters = [row['character_name'] for row in cursor.fetchall()]
        conn.close()
        return characters
