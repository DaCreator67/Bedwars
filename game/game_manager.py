"""Main game manager and loop."""
from typing import List, Dict, Optional
from .entities import Player, Bot, Item, Structure, Vector3
from .game_modes import GameMode, GameModeType
from .physics import PhysicsEngine, BoundingBox
from auth.database import DatabaseManager
import config
import time


class GameManager:
    """Manages game state and logic."""
    
    def __init__(self, game_mode: GameMode, db_manager: DatabaseManager):
        """Initialize game manager.
        
        Args:
            game_mode: The game mode to play
            db_manager: Database manager instance
        """
        self.game_mode = game_mode
        self.db_manager = db_manager
        
        # Game state
        self.is_running = True
        self.is_paused = False
        self.game_started = False
        self.game_time = 0.0
        self.game_duration = 0.0
        
        # Entities
        self.players: List[Player] = []
        self.bots: List[Bot] = []
        self.items: List[Item] = []
        self.structures: List[Structure] = []
        
        # Team data
        self.teams: Dict[int, Dict] = {}
        self.initialize_teams()
        
        # Physics
        self.physics_engine = PhysicsEngine()
        
        # Entity ID counter
        self.next_entity_id = 0
        
        # Game stats
        self.total_kills = 0
        self.total_deaths = 0
    
    def initialize_teams(self):
        """Initialize teams for the game mode."""
        for team_id in range(self.game_mode.teams):
            self.teams[team_id] = {
                "id": team_id,
                "color": config.TEAM_COLORS[team_id % len(config.TEAM_COLORS)],
                "players": [],
                "alive_count": 0,
                "bed_destroyed": False,
                "score": 0,
            }
    
    def add_player(self, player_id: int, username: str, character: str = None) -> Player:
        """Add a player to the game.
        
        Args:
            player_id: Database player ID
            username: Player username
            character: Selected character
            
        Returns:
            Created Player entity
        """
        # Assign to team
        team_id = len(self.players) % self.game_mode.teams
        
        # Create spawn position (simple distribution)
        spawn_x = (team_id % 2) * 10.0
        spawn_z = (team_id // 2) * 10.0
        position = Vector3(spawn_x, 10.0, spawn_z)
        
        # Create player entity
        entity_id = self._get_next_entity_id()
        player = Player(entity_id, player_id, username, character, team_id, position)
        
        self.players.append(player)
        self.teams[team_id]["players"].append(player)
        self.teams[team_id]["alive_count"] += 1
        
        # Add to physics
        self.physics_engine.add_entity(player)
        bbox = BoundingBox(position, 0.6, 1.8, 0.6)
        self.physics_engine.add_collider(player, bbox)
        
        return player
    
    def add_bot(self, name: str = None, difficulty: int = 1) -> Bot:
        """Add a bot to the game.
        
        Args:
            name: Bot name
            difficulty: AI difficulty (1-5)
            
        Returns:
            Created Bot entity
        """
        # Assign to team
        team_id = len(self.bots) % self.game_mode.teams
        
        if name is None:
            name = f"Bot_{len(self.bots)+1}"
        
        # Create spawn position
        spawn_x = (team_id % 2) * 10.0
        spawn_z = (team_id // 2) * 10.0
        position = Vector3(spawn_x, 10.0, spawn_z)
        
        # Create bot entity
        entity_id = self._get_next_entity_id()
        bot = Bot(entity_id, len(self.bots), name, difficulty, team_id, position)
        
        self.bots.append(bot)
        self.teams[team_id]["players"].append(bot)
        self.teams[team_id]["alive_count"] += 1
        
        # Add to physics
        self.physics_engine.add_entity(bot)
        bbox = BoundingBox(position, 0.6, 1.8, 0.6)
        self.physics_engine.add_collider(bot, bbox)
        
        return bot
    
    def start_game(self):
        """Start the game."""
        self.game_started = True
        self.is_running = True
        
        # Initialize game structures (beds, generators, etc)
        self._initialize_game_structures()
    
    def _initialize_game_structures(self):
        """Initialize game structures like beds and generators."""
        for team_id in range(self.game_mode.teams):
            # Bed position
            bed_x = (team_id % 2) * 10.0 - 5.0
            bed_z = (team_id // 2) * 10.0 - 5.0
            bed_position = Vector3(bed_x, 5.0, bed_z)
            
            # Create bed
            entity_id = self._get_next_entity_id()
            bed = Structure(entity_id, "bed", team_id, bed_position)
            self.structures.append(bed)
            
            # Create generator (ore generator)
            gen_x = bed_x + 2.0
            gen_z = bed_z + 2.0
            gen_position = Vector3(gen_x, 5.0, gen_z)
            
            entity_id = self._get_next_entity_id()
            generator = Structure(entity_id, "generator", team_id, gen_position)
            self.structures.append(generator)
    
    def update(self, delta_time: float):
        """Update game state.
        
        Args:
            delta_time: Time step in seconds
        """
        if not self.game_started or self.is_paused:
            return
        
        self.game_time += delta_time
        
        # Update physics
        self.physics_engine.update(delta_time)
        
        # Update entities
        all_entities = self.players + self.bots + self.items
        
        for entity in self.players:
            entity.update(delta_time)
        
        for bot in self.bots:
            bot.update(delta_time, all_entities)
        
        for item in self.items:
            item.update(delta_time)
            if not item.active:
                self.items.remove(item)
        
        # Check win condition
        self._check_win_condition()
    
    def _check_win_condition(self) -> Optional[int]:
        """Check if game has a winner.
        
        Returns:
            Winning team ID or None if game ongoing
        """
        alive_teams = 0
        last_alive_team = None
        
        for team_id, team_data in self.teams.items():
            # Count alive players in team
            alive_count = sum(1 for p in team_data["players"] 
                            if getattr(p, 'is_alive', True))
            
            if alive_count > 0:
                alive_teams += 1
                last_alive_team = team_id
        
        # If only one team alive, they win
        if alive_teams == 1 and last_alive_team is not None:
            self._end_game(last_alive_team)
            return last_alive_team
        
        return None
    
    def _end_game(self, winning_team_id: int):
        """End the game."""
        self.is_running = False
        self.game_duration = self.game_time
        
        # Record stats for all players
        for player in self.players:
            placement = 1 if player.team_id == winning_team_id else 0
            
            # Award coins
            if placement == 1:
                coins = config.VICTORY_BONUS + config.BASE_COIN_REWARD
            else:
                coins = config.BASE_COIN_REWARD
            
            stats = {
                "kills": player.kills,
                "deaths": player.deaths,
                "assists": player.assists,
                "beds_destroyed": player.beds_destroyed,
                "coins_earned": coins,
                "placement": placement,
                "team_size": self.game_mode.team_size,
                "game_duration": int(self.game_duration),
            }
            
            self.db_manager.record_game_stats(
                player.player_id,
                self.game_mode.mode_type.value,
                stats
            )
    
    def get_team_info(self, team_id: int) -> Dict:
        """Get information about a team."""
        if team_id not in self.teams:
            return None
        
        team = self.teams[team_id]
        alive_count = sum(1 for p in team["players"] if getattr(p, 'is_alive', True))
        
        return {
            "team_id": team_id,
            "color": team["color"],
            "players": team["players"],
            "alive_count": alive_count,
            "total_members": len(team["players"]),
            "bed_destroyed": team["bed_destroyed"],
            "score": team["score"],
        }
    
    def get_game_status(self) -> Dict:
        """Get overall game status."""
        return {
            "mode": self.game_mode.get_full_name(),
            "is_running": self.is_running,
            "game_time": self.game_time,
            "total_players": len(self.players),
            "total_bots": len(self.bots),
            "teams": len(self.teams),
            "teams_data": [self.get_team_info(tid) for tid in sorted(self.teams.keys())],
        }
    
    def _get_next_entity_id(self) -> int:
        """Get next available entity ID."""
        entity_id = self.next_entity_id
        self.next_entity_id += 1
        return entity_id
