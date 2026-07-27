"""Game entities: players, bots, items, and structures."""
import numpy as np
from typing import List, Optional, Dict
from dataclasses import dataclass
import config


@dataclass
class Vector3:
    """3D vector representation."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def __add__(self, other: 'Vector3') -> 'Vector3':
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other: 'Vector3') -> 'Vector3':
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar: float) -> 'Vector3':
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def distance_to(self, other: 'Vector3') -> float:
        """Calculate distance to another vector."""
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return np.sqrt(dx*dx + dy*dy + dz*dz)
    
    def to_tuple(self) -> tuple:
        return (self.x, self.y, self.z)


class Entity:
    """Base class for all game entities."""
    
    def __init__(self, entity_id: int, position: Vector3 = None, team_id: int = 0):
        """Initialize an entity.
        
        Args:
            entity_id: Unique identifier for this entity
            position: Starting position (default: origin)
            team_id: Team this entity belongs to
        """
        self.entity_id = entity_id
        self.position = position or Vector3(0, 0, 0)
        self.team_id = team_id
        self.velocity = Vector3(0, 0, 0)
        self.rotation = Vector3(0, 0, 0)  # Pitch, Yaw, Roll
        self.active = True
    
    def update(self, delta_time: float):
        """Update entity state."""
        # Apply gravity
        self.velocity.y -= config.DEFAULT_GRAVITY * delta_time
        
        # Update position
        self.position = self.position + self.velocity * delta_time
    
    def destroy(self):
        """Mark entity as destroyed."""
        self.active = False


class Player(Entity):
    """Represents a player character."""
    
    def __init__(self, entity_id: int, player_id: int, username: str, 
                 character: str = None, team_id: int = 0, position: Vector3 = None):
        """Initialize a player.
        
        Args:
            entity_id: Unique entity identifier
            player_id: Database player ID
            username: Player username
            character: Selected character name
            team_id: Team ID
            position: Starting position
        """
        super().__init__(entity_id, position, team_id)
        self.player_id = player_id
        self.username = username
        self.character = character or "default"
        
        # Health and status
        self.max_hp = config.PLAYER_MAX_HP
        self.health = self.max_hp
        self.is_alive = True
        
        # Statistics
        self.kills = 0
        self.deaths = 0
        self.assists = 0
        self.beds_destroyed = 0
        self.coins_earned = 0
        self.damage_dealt = 0
        
        # Inventory
        self.inventory: Dict[str, int] = {}
        self.selected_item = None
        
        # Status effects
        self.status_effects: Dict[str, float] = {}  # effect_name -> duration
        
        # Combat
        self.melee_cooldown = 0.0
        self.bow_cooldown = 0.0
        self.is_attacking = False
        self.in_combat = False
        
        # Character perks
        self._apply_character_perks()
    
    def _apply_character_perks(self):
        """Apply character-specific perk modifiers."""
        if self.character not in config.CHARACTERS:
            return
        
        char_config = config.CHARACTERS[self.character]
        
        if "speed_multiplier" in char_config:
            self.speed_multiplier = char_config["speed_multiplier"]
        else:
            self.speed_multiplier = 1.0
        
        if "extra_health" in char_config:
            self.max_hp += char_config["extra_health"]
            self.health = self.max_hp
        
        if "damage_reduction" in char_config:
            self.damage_reduction = char_config["damage_reduction"]
        else:
            self.damage_reduction = 0.0
    
    def take_damage(self, damage: float, attacker: Optional['Player'] = None) -> bool:
        """Apply damage to player.
        
        Args:
            damage: Amount of damage
            attacker: Player who dealt damage
            
        Returns:
            True if player died from this damage
        """
        if not self.is_alive:
            return False
        
        # Apply damage reduction
        actual_damage = damage * (1.0 - self.damage_reduction)
        
        self.health -= actual_damage
        self.in_combat = True
        
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
            if attacker:
                attacker.kills += 1
            self.deaths += 1
            return True
        
        return False
    
    def heal(self, amount: float):
        """Heal the player."""
        self.health = min(self.health + amount, self.max_hp)
    
    def add_item(self, item_name: str, quantity: int = 1):
        """Add item to inventory."""
        if item_name not in self.inventory:
            self.inventory[item_name] = 0
        self.inventory[item_name] += quantity
    
    def remove_item(self, item_name: str, quantity: int = 1) -> bool:
        """Remove item from inventory.
        
        Returns:
            True if item was removed, False if not enough items
        """
        if item_name not in self.inventory or self.inventory[item_name] < quantity:
            return False
        
        self.inventory[item_name] -= quantity
        if self.inventory[item_name] == 0:
            del self.inventory[item_name]
        
        return True
    
    def add_status_effect(self, effect_name: str, duration: float):
        """Add a status effect to player."""
        self.status_effects[effect_name] = duration
    
    def update(self, delta_time: float):
        """Update player state."""
        super().update(delta_time)
        
        # Update cooldowns
        if self.melee_cooldown > 0:
            self.melee_cooldown -= delta_time
        if self.bow_cooldown > 0:
            self.bow_cooldown -= delta_time
        
        # Update status effects
        effects_to_remove = []
        for effect_name, duration in self.status_effects.items():
            self.status_effects[effect_name] -= delta_time
            if self.status_effects[effect_name] <= 0:
                effects_to_remove.append(effect_name)
        
        for effect_name in effects_to_remove:
            del self.status_effects[effect_name]
        
        # Reset combat state
        if not self.in_combat:
            self.in_combat = False
    
    def get_stats(self) -> dict:
        """Get player statistics."""
        return {
            "player_id": self.player_id,
            "username": self.username,
            "character": self.character,
            "health": self.health,
            "max_hp": self.max_hp,
            "kills": self.kills,
            "deaths": self.deaths,
            "assists": self.assists,
            "beds_destroyed": self.beds_destroyed,
            "coins_earned": self.coins_earned,
            "damage_dealt": self.damage_dealt,
        }


class Bot(Entity):
    """AI-controlled bot player."""
    
    def __init__(self, entity_id: int, bot_id: int, name: str, 
                 difficulty: int = 1, team_id: int = 0, position: Vector3 = None):
        """Initialize a bot.
        
        Args:
            entity_id: Unique entity identifier
            bot_id: Bot identifier
            name: Bot name
            difficulty: AI difficulty level (1-5)
            team_id: Team ID
            position: Starting position
        """
        super().__init__(entity_id, position, team_id)
        self.bot_id = bot_id
        self.name = name
        self.difficulty = min(max(difficulty, 1), 5)
        
        # Health
        self.max_hp = config.PLAYER_MAX_HP
        self.health = self.max_hp
        self.is_alive = True
        
        # Statistics
        self.kills = 0
        self.deaths = 0
        self.assists = 0
        
        # AI state
        self.target: Optional[Entity] = None
        self.target_position: Optional[Vector3] = None
        self.decision_timer = 0.0
        self.decision_interval = 0.5 / self.difficulty  # More frequent decisions = higher difficulty
        
        # Combat
        self.melee_cooldown = 0.0
        self.attack_range = config.PLAYER_REACH
        
        # Accuracy based on difficulty
        self.accuracy = min(config.BOT_ACCURACY + (0.1 * (self.difficulty - 1)), 0.95)
    
    def take_damage(self, damage: float, attacker: Optional[Player] = None) -> bool:
        """Apply damage to bot."""
        self.health -= damage
        
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
            if attacker:
                attacker.kills += 1
            self.deaths += 1
            return True
        
        return False
    
    def find_nearest_enemy(self, entities: List[Entity], max_range: float = 50.0) -> Optional[Entity]:
        """Find nearest enemy entity."""
        nearest = None
        nearest_distance = max_range
        
        for entity in entities:
            if not isinstance(entity, (Player, Bot)):
                continue
            if entity.team_id == self.team_id or not getattr(entity, 'is_alive', True):
                continue
            
            distance = self.position.distance_to(entity.position)
            if distance < nearest_distance:
                nearest = entity
                nearest_distance = distance
        
        return nearest
    
    def update(self, delta_time: float, entities: List[Entity] = None):
        """Update bot state and AI."""
        super().update(delta_time)
        
        if not self.is_alive:
            return
        
        # Update cooldowns
        if self.melee_cooldown > 0:
            self.melee_cooldown -= delta_time
        
        # Make decisions at intervals
        self.decision_timer -= delta_time
        if self.decision_timer <= 0:
            self.decision_timer = self.decision_interval
            
            if entities:
                self.target = self.find_nearest_enemy(entities)
                if self.target:
                    self.target_position = self.target.position
        
        # Move towards target if within range
        if self.target_position:
            direction = self.target_position - self.position
            distance = direction.distance_to(Vector3(0, 0, 0))
            
            if distance > 0:
                direction = direction * (1.0 / distance)  # Normalize
                move_speed = config.PLAYER_SPEED * delta_time
                self.position = self.position + direction * move_speed


class Item(Entity):
    """Collectible item in the game world."""
    
    def __init__(self, entity_id: int, item_type: str, position: Vector3 = None):
        """Initialize an item.
        
        Args:
            entity_id: Unique entity identifier
            item_type: Type of item (e.g., "wood", "stone", "diamond")
            position: Position in world
        """
        super().__init__(entity_id, position, team_id=-1)  # Items don't belong to teams
        self.item_type = item_type
        self.quantity = 1
        self.collected = False
        self.despawn_timer = 300.0  # Despawn after 5 minutes
    
    def update(self, delta_time: float):
        """Update item state."""
        super().update(delta_time)
        
        if self.collected:
            return
        
        # Despawn timer
        self.despawn_timer -= delta_time
        if self.despawn_timer <= 0:
            self.active = False
    
    def collect(self):
        """Mark item as collected."""
        self.collected = True
        self.active = False


class Structure(Entity):
    """Game structure (bed, generator, etc)."""
    
    def __init__(self, entity_id: int, structure_type: str, team_id: int = 0, position: Vector3 = None):
        """Initialize a structure.
        
        Args:
            entity_id: Unique entity identifier
            structure_type: Type of structure ("bed", "generator", etc)
            team_id: Team that owns this structure
            position: Position in world
        """
        super().__init__(entity_id, position, team_id)
        self.structure_type = structure_type
        self.max_health = 100.0
        self.health = self.max_health
        self.is_destroyed = False
    
    def take_damage(self, damage: float, attacker: Optional[Player] = None) -> bool:
        """Apply damage to structure.
        
        Returns:
            True if structure is destroyed
        """
        self.health -= damage
        
        if self.health <= 0:
            self.health = 0
            self.is_destroyed = True
            if attacker:
                attacker.beds_destroyed += 1
            return True
        
        return False
    
    def repair(self, amount: float):
        """Repair the structure."""
        self.health = min(self.health + amount, self.max_health)
