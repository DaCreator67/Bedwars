"""Game mode definitions."""
from enum import Enum
from typing import Dict, List
import config


class GameModeType(Enum):
    """Game mode types."""
    CLASSIC = "classic"
    LUCKYBLOCK = "luckyblock"


class GameMode:
    """Base game mode class."""
    
    def __init__(self, mode_name: str, game_mode_type: GameModeType, team_size: int, max_players: int, num_teams: int):
        self.mode_name = mode_name
        self.game_mode_type = game_mode_type
        self.team_size = team_size
        self.max_players = max_players
        self.num_teams = num_teams
        self.teams = {i: [] for i in range(num_teams)}
        self.team_beds = {i: True for i in range(num_teams)}  # Track if bed is still alive
        self.team_spawn_positions = {}
    
    def add_player_to_team(self, player, team_id: int) -> bool:
        """Add player to team."""
        if team_id not in self.teams:
            return False
        
        if len(self.teams[team_id]) >= self.team_size:
            return False
        
        self.teams[team_id].append(player)
        return True
    
    def is_team_eliminated(self, team_id: int) -> bool:
        """Check if team is eliminated."""
        # Team is eliminated if bed is destroyed AND no players alive
        if not self.team_beds[team_id]:
            alive_players = sum(1 for p in self.teams[team_id] if p.is_alive)
            return alive_players == 0
        return False
    
    def get_team_placement(self) -> Dict[int, int]:
        """Get final placement for each team."""
        placements = {}
        active_teams = []
        
        for team_id, players in self.teams.items():
            alive_count = sum(1 for p in players if p.is_alive)
            if alive_count > 0:
                active_teams.append((team_id, alive_count))
        
        # Sort by number of alive players (descending)
        active_teams.sort(key=lambda x: x[1], reverse=True)
        
        for placement, (team_id, _) in enumerate(active_teams, 1):
            placements[team_id] = placement
        
        return placements


class ClassicMode(GameMode):
    """Classic Bedwars game mode."""
    
    MODES = {
        'solos': {'team_size': 1, 'max_players': 16, 'num_teams': 16},
        'doubles': {'team_size': 2, 'max_players': 8, 'num_teams': 4},
        'squads': {'team_size': 4, 'max_players': 16, 'num_teams': 4},
        '5v5': {'team_size': 5, 'max_players': 10, 'num_teams': 2},
        '1v1': {'team_size': 1, 'max_players': 2, 'num_teams': 2},
        '2v2': {'team_size': 2, 'max_players': 4, 'num_teams': 2},
    }
    
    def __init__(self, mode_name: str):
        mode_config = self.MODES[mode_name]
        super().__init__(
            mode_name=mode_name,
            game_mode_type=GameModeType.CLASSIC,
            **mode_config
        )
        self._setup_spawns()
    
    def _setup_spawns(self):
        """Setup spawn positions for teams."""
        # Positions arranged in a circle
        import math
        angle_step = 2 * math.pi / self.num_teams
        radius = 50
        
        for i in range(self.num_teams):
            angle = i * angle_step
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            self.team_spawn_positions[i] = (x, 65, z)  # y=65 (slightly above ground)


class LuckyblockMode(GameMode):
    """Luckyblock Bedwars game mode with special items."""
    
    MODES = {
        'squads': {'team_size': 4, 'max_players': 16, 'num_teams': 4},
        '5v5': {'team_size': 5, 'max_players': 10, 'num_teams': 2},
    }
    
    LUCKY_ITEMS = [
        # Good items
        {'name': 'diamond_sword', 'rarity': 'rare', 'effect': 'weapon_upgrade'},
        {'name': 'healing_potion', 'rarity': 'common', 'effect': 'heal_50'},
        {'name': 'invisibility_potion', 'rarity': 'uncommon', 'effect': 'invisibility_10s'},
        {'name': 'strength_potion', 'rarity': 'uncommon', 'effect': 'strength_20s'},
        {'name': 'speed_potion', 'rarity': 'common', 'effect': 'speed_15s'},
        {'name': 'respawn_anchor', 'rarity': 'legendary', 'effect': 'extra_life'},
        # Bad items
        {'name': 'poison_potion', 'rarity': 'uncommon', 'effect': 'poison_10s'},
        {'name': 'slowness_potion', 'rarity': 'uncommon', 'effect': 'slowness_15s'},
        {'name': 'weakness_potion', 'rarity': 'common', 'effect': 'weakness_20s'},
        {'name': 'harming_potion', 'rarity': 'rare', 'effect': 'damage_20'},
    ]
    
    def __init__(self, mode_name: str):
        mode_config = self.MODES[mode_name]
        super().__init__(
            mode_name=mode_name,
            game_mode_type=GameModeType.LUCKYBLOCK,
            **mode_config
        )
        self.lucky_blocks = []
        self._setup_spawns()
    
    def _setup_spawns(self):
        """Setup spawn positions for teams."""
        import math
        angle_step = 2 * math.pi / self.num_teams
        radius = 50
        
        for i in range(self.num_teams):
            angle = i * angle_step
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            self.team_spawn_positions[i] = (x, 65, z)
    
    def get_random_lucky_item(self):
        """Get a random lucky block item."""
        import random
        return random.choice(self.LUCKY_ITEMS)
