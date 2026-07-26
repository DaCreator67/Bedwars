"""Game constants and utility functions."""
import math

# Game version
VERSION = "1.0.0"

# Physics constants
GRAVITY = 9.81
AIR_RESISTANCE = 0.99

# Item types
ITEM_TYPES = {
    'arrow': {'stackable': True, 'max_stack': 64, 'rarity': 'common'},
    'stone_sword': {'stackable': False, 'max_stack': 1, 'rarity': 'uncommon'},
    'wooden_pickaxe': {'stackable': False, 'max_stack': 1, 'rarity': 'uncommon'},
    'diamond_sword': {'stackable': False, 'max_stack': 1, 'rarity': 'rare'},
    'iron_pickaxe': {'stackable': False, 'max_stack': 1, 'rarity': 'rare'},
    'healing_potion': {'stackable': True, 'max_stack': 16, 'rarity': 'uncommon'},
    'strength_potion': {'stackable': True, 'max_stack': 16, 'rarity': 'rare'},
    'speed_potion': {'stackable': True, 'max_stack': 16, 'rarity': 'uncommon'},
    'invisibility_potion': {'stackable': True, 'max_stack': 16, 'rarity': 'rare'},
}

# Rarity colors (RGB)
RARITY_COLORS = {
    'common': (169, 169, 169),      # Gray
    'uncommon': (102, 204, 0),      # Green
    'rare': (0, 153, 255),          # Blue
    'epic': (153, 0, 255),          # Purple
    'legendary': (255, 204, 0),     # Gold
}

# Team colors (RGB)
TEAM_COLORS = [
    (255, 0, 0),        # Red
    (0, 0, 255),        # Blue
    (0, 255, 0),        # Green
    (255, 255, 0),      # Yellow
    (255, 128, 0),      # Orange
    (255, 0, 255),      # Magenta
    (0, 255, 255),      # Cyan
    (192, 192, 192),    # Silver
]

# Effect durations (seconds)
EFFECT_DURATIONS = {
    'strength': 20.0,
    'speed': 15.0,
    'weakness': 20.0,
    'slowness': 15.0,
    'poison': 10.0,
    'invisibility': 10.0,
    'regeneration': 5.0,
}

# Damage types
DAMAGE_TYPES = {
    'melee': {'source': 'melee_attack', 'bypass_armor': False},
    'arrow': {'source': 'projectile', 'bypass_armor': False},
    'poison': {'source': 'poison', 'bypass_armor': True},
    'fall': {'source': 'fall_damage', 'bypass_armor': False},
    'void': {'source': 'void', 'bypass_armor': True},
}

def clamp(value, min_val, max_val):
    """Clamp value between min and max."""
    return max(min_val, min(max_val, value))

def lerp(start, end, t):
    """Linear interpolation."""
    return start + (end - start) * t

def degrees_to_radians(degrees):
    """Convert degrees to radians."""
    return degrees * (math.pi / 180)

def radians_to_degrees(radians):
    """Convert radians to degrees."""
    return radians * (180 / math.pi)

def distance_2d(x1, y1, x2, y2):
    """Calculate 2D distance."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def distance_3d(x1, y1, z1, x2, y2, z2):
    """Calculate 3D distance."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
