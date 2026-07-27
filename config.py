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

# Game modes - restructured for multiple teams
GAME_MODES = {
    "classic": {
        "solos": {
            "max_players": 8,
            "teams": 8,
            "team_size": 1,
            "description": "1v1v1v1v1v1v1v1 - 8 individual players"
        },
        "doubles": {
            "max_players": 16,
            "teams": 8,
            "team_size": 2,
            "description": "2v2v2v2v2v2v2v2 - 8 teams of 2"
        },
        "squads": {
            "max_players": 16,
            "teams": 4,
            "team_size": 4,
            "description": "4v4v4v4 - 4 teams of 4"
        },
        "5v5": {
            "max_players": 10,
            "teams": 2,
            "team_size": 5,
            "description": "5v5 - 2 teams of 5"
        },
        "1v1": {
            "max_players": 2,
            "teams": 2,
            "team_size": 1,
            "description": "1v1 - Head to head"
        },
        "2v2": {
            "max_players": 4,
            "teams": 2,
            "team_size": 2,
            "description": "2v2 - Head to head teams"
        },
    },
    "luckyblock": {
        "squads": {
            "max_players": 16,
            "teams": 4,
            "team_size": 4,
            "description": "4v4v4v4 Lucky Block - Special items and perks"
        },
        "5v5": {
            "max_players": 10,
            "teams": 2,
            "team_size": 5,
            "description": "5v5 Lucky Block"
        },
    }
}

# Win conditions (placement needed to win)
WIN_CONDITION = {
    "solos": 1,          # Last player standing
    "doubles": 1,        # Last team standing
    "squads": 1,         # Last team standing
    "5v5": 1,            # Last team standing
    "1v1": 1,            # Last player standing
    "2v2": 1,            # Last team standing
    "luckyblock_squads": 1,
    "luckyblock_5v5": 1,
}

# Team colors for rendering
TEAM_COLORS = [
    (255, 0, 0),      # Red
    (0, 0, 255),      # Blue
    (0, 255, 0),      # Green
    (255, 255, 0),    # Yellow
    (255, 165, 0),    # Orange
    (128, 0, 128),    # Purple
    (0, 255, 255),    # Cyan
    (255, 192, 203),  # Pink
]

# Character definitions with unique perks
CHARACTERS = {
    "vex": {
        "name": "Vex",
        "description": "Curse Opponents, Reduce HP to 90",
        "perks": ["curse_opponents", "hp_reduction"],
        "cost": 1000
    },
    "speedster": {
        "name": "Speedster",
        "description": "Move 15% Faster Throughout The Game",
        "perks": ["speed_boost"],
        "cost": 1000,
        "speed_multiplier": 1.15
    },
    "guardian": {
        "name": "Guardian",
        "description": "Take 10% Damage Reduction (stackable)",
        "perks": ["damage_reduction"],
        "cost": 1000,
        "damage_reduction": 0.1
    },
    "archer": {
        "name": "Archer",
        "description": "Increase Bow Damage and Accuracy",
        "perks": ["bow_damage", "bow_accuracy"],
        "cost": 1000,
        "bow_damage_bonus": 1.2
    },
    "tank": {
        "name": "Tank",
        "description": "Have Extra Health (Regenerates)",
        "perks": ["extra_health", "regeneration"],
        "cost": 1000,
        "extra_health": 25
    },
    "phantom": {
        "name": "Phantom",
        "description": "Invisibility After Taking Damage For 2 Seconds",
        "perks": ["invisibility"],
        "cost": 1000,
        "invisibility_duration": 2.0
    },
    "berserker": {
        "name": "Berserker",
        "description": "Lower Health = Higher Damage Output",
        "perks": ["damage_scaling"],
        "cost": 1000
    },
    "medic": {
        "name": "Medic",
        "description": "Quickly Heal Nearby Teammates",
        "perks": ["heal_teammates"],
        "cost": 1000,
        "heal_radius": 10.0
    },
    "ninja": {
        "name": "Ninja",
        "description": "Move Sneakily Throughout The Map",
        "perks": ["stealth_movement"],
        "cost": 1000,
        "stealth_multiplier": 0.7
    },
    "gladiator": {
        "name": "Gladiator",
        "description": "Reflect Damage Onto Enemies",
        "perks": ["damage_reflection"],
        "cost": 1000,
        "reflection_percentage": 0.25
    }
}
