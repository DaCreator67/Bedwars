"""Main game manager and controller."""
from typing import List, Dict, Optional
import time
from enum import Enum
from .entities import Player, Bot, Item, Projectile, EntityType
from .physics import PhysicsEngine
from .game_modes import GameMode, ClassicMode, LuckyblockMode
from .math_utils import Vector3
import config
from auth.database import DatabaseManager


class GameState(Enum):
    """Game state enumeration."""
    LOBBY = "lobby"
    STARTING = "starting"
    PLAYING = "playing"
    ENDING = "ending"
    FINISHED = "finished"


class GameManager:
    """Main game manager handling all game logic."""
    
    def __init__(self, game_mode: GameMode, db_manager: DatabaseManager):
        self.game_mode = game_mode
        self.db_manager = db_manager
        self.state = GameState.LOBBY
        self.entities: List = []
        self.players: Dict[int, Player] = {}
        self.physics_engine = PhysicsEngine()
        
        self.start_time = None
        self.game_duration = 0.0
        self.max_game_duration = 1800.0  # 30 minutes max
        
        self.game_stats = {}  # Track stats for all players
    
    def add_player(self, player: Player) -> bool:
        """Add player to game."""
        if self.state != GameState.LOBBY:
            return False
        
        # Try to add to game mode teams
        for team_id in range(self.game_mode.num_teams):
            if len(self.game_mode.teams[team_id]) < self.game_mode.team_size:
                if self.game_mode.add_player_to_team(player, team_id):
                    player.team_id = team_id
                    # Set spawn position
                    if team_id in self.game_mode.team_spawn_positions:
                        x, y, z = self.game_mode.team_spawn_positions[team_id]
                        player.position = Vector3(x, y, z)
                    
                    self.players[player.player_id] = player
                    self.entities.append(player)
                    self.game_stats[player.player_id] = {
                        'kills': 0,
                        'deaths': 0,
                        'assists': 0,
                        'beds_destroyed': 0,
                        'coins_earned': 0,
                        'damage_dealt': 0
                    }
                    return True
        
        return False
    
    def add_bot(self, bot_name: str, level: int) -> bool:
        """Add AI bot to game."""
        if self.state != GameState.LOBBY:
            return False
        
        # Create bot with negative ID
        bot_id = -(len([p for p in self.players if p.player_id < 0]) + 1)
        bot = Bot(bot_id, bot_name, -1, level)
        
        # Add to team
        for team_id in range(self.game_mode.num_teams):
            if len(self.game_mode.teams[team_id]) < self.game_mode.team_size:
                if self.game_mode.add_player_to_team(bot, team_id):
                    bot.team_id = team_id
                    # Set spawn position
                    if team_id in self.game_mode.team_spawn_positions:
                        x, y, z = self.game_mode.team_spawn_positions[team_id]
                        bot.position = Vector3(x, y, z)
                    
                    self.players[bot_id] = bot
                    self.entities.append(bot)
                    self.game_stats[bot_id] = {
                        'kills': 0,
                        'deaths': 0,
                        'assists': 0,
                        'beds_destroyed': 0,
                        'coins_earned': 0,
                        'damage_dealt': 0
                    }
                    return True
        
        return False
    
    def start_game(self) -> bool:
        """Start the game."""
        if self.state != GameState.LOBBY:
            return False
        
        # Check if teams are ready
        total_players = sum(len(team) for team in self.game_mode.teams.values())
        if total_players == 0:
            return False
        
        self.state = GameState.STARTING
        self.start_time = time.time()
        self.state = GameState.PLAYING
        return True
    
    def update(self, delta_time: float):
        """Update game state."""
        if self.state != GameState.PLAYING:
            return
        
        self.game_duration += delta_time
        
        # Update all entities
        for entity in self.entities:
            if entity.active:
                if isinstance(entity, Bot):
                    entity.update(delta_time, self.entities)
                else:
                    entity.update(delta_time)
        
        # Update physics
        self.physics_engine.update(self.entities, delta_time)
        
        # Check collisions
        collisions = self.physics_engine.check_collisions(self.entities)
        for entity1, entity2 in collisions:
            self._handle_collision(entity1, entity2)
        
        # Check if game should end
        if self._check_game_end():
            self.end_game()
    
    def _handle_collision(self, entity1, entity2):
        """Handle collision between two entities."""
        # Item pickup
        if isinstance(entity1, Player) and isinstance(entity2, Item):
            if entity2.pickup_cooldown <= 0:
                entity1.add_inventory_item(entity2.item_name, entity2.quantity)
                entity2.active = False
        
        elif isinstance(entity2, Player) and isinstance(entity1, Item):
            if entity1.pickup_cooldown <= 0:
                entity2.add_inventory_item(entity1.item_name, entity1.quantity)
                entity1.active = False
        
        # Projectile hit
        elif isinstance(entity1, Projectile) and isinstance(entity2, Player):
            if entity1.owner_id != entity2.player_id:
                self._handle_projectile_hit(entity1, entity2)
        
        elif isinstance(entity2, Projectile) and isinstance(entity1, Player):
            if entity2.owner_id != entity1.player_id:
                self._handle_projectile_hit(entity2, entity1)
    
    def _handle_projectile_hit(self, projectile: Projectile, player: Player):
        """Handle projectile hitting a player."""
        if projectile.projectile_type == "arrow":
            player.take_damage(config.BOW_DAMAGE, projectile.owner_id, "arrow")
        
        projectile.has_hit = True
    
    def player_attack_melee(self, attacker_id: int) -> bool:
        """Handle melee attack by player."""
        attacker = self.players.get(attacker_id)
        if not attacker or not attacker.can_attack_melee():
            return False
        
        attacker.last_melee_time = 0.0
        
        # Find nearby enemies
        for player_id, target in self.players.items():
            if target.team_id == attacker.team_id or not target.is_alive:
                continue
            
            distance = attacker.position.distance_to(target.position)
            if distance < config.PLAYER_REACH:
                damage = config.MELEE_DAMAGE
                
                # Apply character effects
                if attacker.character == "vex":
                    damage *= 1.1  # 10% bonus
                    target.apply_character_effect("vex_curse")
                
                target.take_damage(damage, attacker_id, "melee")
                self.game_stats[attacker_id]['damage_dealt'] += damage
                
                if not target.is_alive:
                    self.game_stats[attacker_id]['kills'] += 1
                    self.game_stats[target.player_id]['deaths'] += 1
        
        return True
    
    def player_shoot_arrow(self, attacker_id: int, direction: Vector3) -> bool:
        """Handle bow shot by player."""
        attacker = self.players.get(attacker_id)
        if not attacker or not attacker.can_shoot_bow():
            return False
        
        if not attacker.remove_inventory_item("arrow"):
            return False
        
        attacker.last_bow_time = 0.0
        
        # Create projectile
        projectile = Projectile(
            "arrow",
            attacker.position.copy(),
            direction.normalize() * 25.0,
            attacker_id
        )
        self.entities.append(projectile)
        return True
    
    def destroy_bed(self, team_id: int, destroyer_id: int) -> bool:
        """Destroy team bed."""
        if team_id in self.game_mode.team_beds:
            self.game_mode.team_beds[team_id] = False
            if destroyer_id in self.game_stats:
                self.game_stats[destroyer_id]['beds_destroyed'] += 1
            return True
        return False
    
    def _check_game_end(self) -> bool:
        """Check if game should end."""
        # Check time limit
        if self.game_duration >= self.max_game_duration:
            return True
        
        # Check if only one team has players alive
        teams_with_alive = 0
        for team_id, players in self.game_mode.teams.items():
            alive_count = sum(1 for p in players if p.is_alive)
            if alive_count > 0:
                teams_with_alive += 1
        
        return teams_with_alive <= 1
    
    def end_game(self) -> Dict:
        """End game and return results."""
        self.state = GameState.ENDING
        
        # Calculate placements
        placements = self.game_mode.get_team_placement()
        
        # Award coins based on performance
        results = {}
        for player_id, player in self.players.items():
            if player_id < 0:  # Skip bots
                continue
            
            team_placement = placements.get(player.team_id, len(placements) + 1)
            coins_earned = self._calculate_coin_reward(player, team_placement)
            
            self.game_stats[player_id]['coins_earned'] = coins_earned
            
            # Record stats in database
            stats_dict = self.game_stats[player_id].copy()
            stats_dict['placement'] = team_placement
            stats_dict['team_size'] = self.game_mode.team_size
            stats_dict['game_duration'] = int(self.game_duration)
            
            self.db_manager.record_game_stats(player_id, self.game_mode.mode_name, stats_dict)
            
            results[player_id] = stats_dict
        
        self.state = GameState.FINISHED
        return results
    
    def _calculate_coin_reward(self, player: Player, placement: int) -> int:
        """Calculate coin reward based on performance."""
        coins = config.BASE_COIN_REWARD
        
        # Add bonus for kills
        coins += player.kills * config.KILL_BONUS
        
        # Add bonus for bed destruction
        coins += player.beds_destroyed * config.BED_DESTROY_BONUS
        
        # Add bonus for placement
        if placement == 1:
            coins += config.VICTORY_BONUS
        elif placement <= 3:
            coins += int(config.VICTORY_BONUS * 0.5)
        
        return coins
    
    def get_game_info(self) -> dict:
        """Get current game information."""
        return {
            'mode': self.game_mode.mode_name,
            'state': self.state.value,
            'duration': self.game_duration,
            'total_players': len(self.players),
            'teams': {
                team_id: {
                    'players': len(players),
                    'alive': sum(1 for p in players if p.is_alive),
                    'bed_alive': self.game_mode.team_beds.get(team_id, False)
                }
                for team_id, players in self.game_mode.teams.items()
            }
        }
