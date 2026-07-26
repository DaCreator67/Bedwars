"""Game configuration settings."""

# Window settings
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
WINDOW_TITLE = "Bedwars 3D"
FPS = 60

# Game settings
GAME_VERSION = "1.0.0"
DEFAULT_GRAVITY = 9.81
PLAYER_SPEED = 5.0
PLAYER_JUMP_FORCE = 15.0
PLAYER_MAX_HP = 100
PLAYER_REACH = 5.0

# Combat settings
MELEE_DAMAGE = 25
BOW_DAMAGE = 30
MELEE_COOLDOWN = 0.5
BOW_COOLDOWN = 1.0

# Economy
BASE_COIN_REWARD = 50
KILL_BONUS = 100
TEAM_KILL_BONUS = 50
BED_DESTROY_BONUS = 200
VICTORY_BONUS = 500

# Characters
CHARACTER_COST = 1000

# Database
DB_PATH = "game.db"

# Networking
DEFAULT_PORT = 5000
DEFAULT_HOST = "localhost"
MAX_PLAYERS = 20

# Bot settings
BOT_SPAWN_DELAY = 2.0
BOT_REACTION_TIME = 0.3
BOT_ACCURACY = 0.8

# Game modes
GAME_MODES = {
    "classic": {
        "solos": {"max_players": 16, "teams": 16, "team_size": 1},
        "doubles": {"max_players": 8, "teams": 4, "team_size": 2},
        "squads": {"max_players": 16, "teams": 4, "team_size": 4},
        "5v5": {"max_players": 10, "teams": 2, "team_size": 5},
        "1v1": {"max_players": 2, "teams": 2, "team_size": 1},
        "2v2": {"max_players": 4, "teams": 2, "team_size": 2},
    },
    "luckyblock": {
        "squads": {"max_players": 16, "teams": 4, "team_size": 4},
        "5v5": {"max_players": 10, "teams": 2, "team_size": 5},
    }
}

# Win conditions
WIN_CONDITION = {
    "solos": 3,      # 3rd place or higher
    "doubles": 3,
    "squads": 2,     # 2nd place or higher
    "5v5": 1,        # Last team standing
    "1v1": 1,
    "2v2": 1,
    "luckyblock_squads": 2,
    "luckyblock_5v5": 1,
}
