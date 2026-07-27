"""Game mode definitions and management."""
import config
from enum import Enum


class GameModeType(Enum):
    """Enumeration of available game modes."""
    SOLOS = "solos"
    DOUBLES = "doubles"
    SQUADS = "squads"
    FIVES = "5v5"
    ONE_VS_ONE = "1v1"
    TWO_VS_TWO = "2v2"
    LUCKYBLOCK_SQUADS = "luckyblock_squads"
    LUCKYBLOCK_FIVES = "luckyblock_5v5"


class GameMode:
    """Represents a game mode configuration."""
    
    def __init__(self, mode_type: GameModeType, is_luckyblock: bool = False):
        """Initialize a game mode.
        
        Args:
            mode_type: The type of game mode
            is_luckyblock: Whether this is a lucky block variant
        """
        self.mode_type = mode_type
        self.is_luckyblock = is_luckyblock
        
        # Get mode config
        if is_luckyblock:
            category = "luckyblock"
            mode_key = mode_type.value
        else:
            category = "classic"
            mode_key = mode_type.value
        
        self.config = config.GAME_MODES.get(category, {}).get(mode_key, {})
        
        if not self.config:
            raise ValueError(f"Unknown game mode: {category}/{mode_key}")
        
        self.max_players = self.config.get("max_players", 0)
        self.teams = self.config.get("teams", 1)
        self.team_size = self.config.get("team_size", 1)
        self.description = self.config.get("description", "")
        
    def get_full_name(self) -> str:
        """Get the full display name of the game mode."""
        mode_name = self.mode_type.value.replace("_", " ").title()
        if self.is_luckyblock:
            return f"{mode_name} (Lucky Block)"
        return mode_name
    
    def validate_player_count(self, player_count: int) -> bool:
        """Check if player count is valid for this mode."""
        return player_count > 0 and player_count <= self.max_players
    
    def get_team_assignment(self, player_index: int) -> int:
        """Assign a player to a team based on index.
        
        Args:
            player_index: 0-based player index in the game
            
        Returns:
            Team ID (0-based) for the player
        """
        return player_index % self.teams
    
    def __str__(self) -> str:
        return f"{self.get_full_name()} - {self.description}"
    
    def __repr__(self) -> str:
        return f"GameMode({self.mode_type.value}, luckyblock={self.is_luckyblock})"


class ModeSelector:
    """Helper class to select and list available game modes."""
    
    @staticmethod
    def get_classic_modes():
        """Get all classic game modes."""
        modes = []
        for mode_type in GameModeType:
            if "luckyblock" not in mode_type.value:
                modes.append(GameMode(mode_type, is_luckyblock=False))
        return modes
    
    @staticmethod
    def get_luckyblock_modes():
        """Get all lucky block game modes."""
        modes = []
        luckyblock_types = [
            GameModeType.LUCKYBLOCK_SQUADS,
            GameModeType.LUCKYBLOCK_FIVES,
        ]
        for mode_type in luckyblock_types:
            modes.append(GameMode(mode_type, is_luckyblock=True))
        return modes
    
    @staticmethod
    def get_all_modes():
        """Get all available game modes."""
        return ModeSelector.get_classic_modes() + ModeSelector.get_luckyblock_modes()
    
    @staticmethod
    def get_mode_by_name(name: str) -> 'GameMode':
        """Get a game mode by its name."""
        for mode in ModeSelector.get_all_modes():
            if mode.mode_type.value == name:
                return mode
        raise ValueError(f"Unknown game mode: {name}")
