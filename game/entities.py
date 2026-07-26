"""Entity definitions for players, bots, and items."""
import uuid
from enum import Enum
from typing import Optional, List
from .math_utils import Vector3, Quaternion
import config


class EntityType(Enum):
    """Entity types."""
    PLAYER = "player"
    BOT = "bot"
    ITEM = "item"
    PROJECTILE = "projectile"
    BLOCK = "block"


class Entity:
    """Base entity class."""
    
    def __init__(self, entity_type: EntityType, position: Vector3 = None):
        self.id = str(uuid.uuid4())
        self.entity_type = entity_type
        self.position = position or Vector3(0, 0, 0)
        self.rotation = Quaternion()
        self.velocity = Vector3(0, 0, 0)
        self.active = True
        self.collision_box = None  # Will be set by subclasses
    
    def update(self, delta_time: float):
        """Update entity state."""
        pass
    
    def apply_physics(self, delta_time: float, gravity: float = config.DEFAULT_GRAVITY):
        """Apply physics (gravity, velocity)."""
        # Apply gravity
        self.velocity.y -= gravity * delta_time
        
        # Update position
        self.position += self.velocity * delta_time


class Player(Entity):
    """Player entity."""
    
    def __init__(self, player_id: int, username: str, team_id: int, spawn_pos: Vector3 = None):
        super().__init__(EntityType.PLAYER, spawn_pos or Vector3(0, 64, 0))
        self.player_id = player_id
        self.username = username
        self.team_id = team_id
        
        # Stats
        self.health = config.PLAYER_MAX_HP
        self.max_health = config.PLAYER_MAX_HP
        self.kills = 0
        self.deaths = 0
        self.assists = 0
        self.beds_destroyed = 0
        self.coins_earned = 0
        self.damage_dealt = 0
        
        # Equipment
        self.character = None
        self.held_item = None
        self.inventory = {}
        self.is_alive = True
        self.on_ground = False
        self.can_double_jump = True
        
        # Combat
        self.last_melee_time = 0.0
        self.last_bow_time = 0.0
        self.last_damage_by = None
        self.last_damage_time = 0.0
        
        # Movement
        self.input_direction = Vector3(0, 0, 0)
        self.is_sprinting = False
        self.pitch = 0.0  # Up/down look
        self.yaw = 0.0    # Left/right look
        
        # Collision
        self.collision_box = {
            'width': 0.6,
            'height': 1.8,
            'depth': 0.6
        }
    
    def take_damage(self, damage: float, attacker_id: str = None, damage_type: str = "physical"):
        """Take damage."""
        self.health -= damage
        self.last_damage_by = attacker_id
        self.last_damage_time = 0.0
        
        if self.health <= 0:
            self.is_alive = False
            self.health = 0
    
    def heal(self, amount: float):
        """Heal player."""
        self.health = min(self.health + amount, self.max_health)
    
    def apply_character_effect(self, effect: str, value: any = None):
        """Apply character-specific effect."""
        if effect == "vex_curse":
            # Reduce max HP to 90
            self.max_health = 90
            if self.health > 90:
                self.health = 90
    
    def add_inventory_item(self, item_name: str, quantity: int = 1):
        """Add item to inventory."""
        if item_name not in self.inventory:
            self.inventory[item_name] = 0
        self.inventory[item_name] += quantity
    
    def remove_inventory_item(self, item_name: str, quantity: int = 1) -> bool:
        """Remove item from inventory."""
        if item_name in self.inventory and self.inventory[item_name] >= quantity:
            self.inventory[item_name] -= quantity
            return True
        return False
    
    def update(self, delta_time: float):
        """Update player state."""
        if not self.is_alive:
            return
        
        # Update movement
        speed = config.PLAYER_SPEED * (1.5 if self.is_sprinting else 1.0)
        movement = self.input_direction.normalize() * speed
        self.velocity.x = movement.x
        self.velocity.z = movement.z
        
        # Apply physics
        self.apply_physics(delta_time)
        
        # Update timers
        self.last_melee_time += delta_time
        self.last_bow_time += delta_time
        self.last_damage_time += delta_time
    
    def can_attack_melee(self) -> bool:
        """Check if can perform melee attack."""
        return self.last_melee_time >= config.MELEE_COOLDOWN
    
    def can_shoot_bow(self) -> bool:
        """Check if can shoot bow."""
        return self.last_bow_time >= config.BOW_COOLDOWN and self.remove_inventory_item("arrow", 1) == False
    
    def get_stats(self) -> dict:
        """Get player statistics."""
        return {
            'health': self.health,
            'kills': self.kills,
            'deaths': self.deaths,
            'assists': self.assists,
            'beds_destroyed': self.beds_destroyed,
            'coins_earned': self.coins_earned
        }


class Bot(Player):
    """AI-controlled bot player."""
    
    def __init__(self, bot_id: int, name: str, team_id: int, level: int = 1, spawn_pos: Vector3 = None):
        super().__init__(bot_id, name, team_id, spawn_pos)
        self.is_bot = True
        self.level = level  # Affects difficulty
        self.difficulty = self._calculate_difficulty(level)
        
        # AI state
        self.current_target = None
        self.ai_state = "idle"  # idle, patrolling, fighting, fleeing
        self.state_timer = 0.0
        self.decision_interval = 0.5  # Update AI decisions every 0.5s
        self.target_pos = None
        
    def _calculate_difficulty(self, level: int) -> dict:
        """Calculate bot difficulty based on level."""
        # Level 1-10: Easy, 11-20: Medium, 21-30: Hard, 31+: Expert
        if level <= 10:
            return {
                'accuracy': 0.5,
                'reaction_time': 0.8,
                'aggression': 0.3,
                'health_multiplier': 1.0
            }
        elif level <= 20:
            return {
                'accuracy': 0.7,
                'reaction_time': 0.5,
                'aggression': 0.6,
                'health_multiplier': 1.1
            }
        elif level <= 30:
            return {
                'accuracy': 0.85,
                'reaction_time': 0.3,
                'aggression': 0.8,
                'health_multiplier': 1.2
            }
        else:
            return {
                'accuracy': 0.95,
                'reaction_time': 0.1,
                'aggression': 1.0,
                'health_multiplier': 1.5
            }
    
    def update(self, delta_time: float, all_entities: List[Entity] = None):
        """Update bot AI and state."""
        if not self.is_alive:
            return
        
        self.state_timer += delta_time
        
        # Make AI decisions periodically
        if self.state_timer >= self.decision_interval:
            self._make_ai_decision(all_entities or [])
            self.state_timer = 0.0
        
        # Execute current action
        self._execute_ai_action()
        
        # Apply physics
        super().update(delta_time)
    
    def _make_ai_decision(self, all_entities: List[Entity]):
        """Make AI decision based on environment."""
        # Find nearest enemy
        enemies = [e for e in all_entities if isinstance(e, Player) and e.team_id != self.team_id and e.is_alive]
        
        if enemies:
            nearest_enemy = min(enemies, key=lambda e: self.position.distance_to(e.position))
            distance = self.position.distance_to(nearest_enemy.position)
            
            if distance < 20:
                self.ai_state = "fighting"
                self.current_target = nearest_enemy
            else:
                self.ai_state = "patrolling"
                self.target_pos = nearest_enemy.position.copy()
        else:
            self.ai_state = "patrolling"
            self.current_target = None
    
    def _execute_ai_action(self):
        """Execute current AI action."""
        if self.ai_state == "fighting" and self.current_target:
            # Move toward target and attack
            direction = (self.current_target.position - self.position).normalize()
            self.input_direction = direction
            
            # Attack if in range
            distance = self.position.distance_to(self.current_target.position)
            if distance < config.PLAYER_REACH and self.can_attack_melee():
                self._perform_melee_attack()
        
        elif self.ai_state == "patrolling" and self.target_pos:
            # Move toward target position
            direction = (self.target_pos - self.position).normalize()
            self.input_direction = direction
            
            if self.position.distance_to(self.target_pos) < 2:
                self.target_pos = None
    
    def _perform_melee_attack(self):
        """Perform melee attack."""
        self.last_melee_time = 0.0
        # Actual damage is handled by game manager


class Item(Entity):
    """Item entity in the world."""
    
    def __init__(self, item_name: str, position: Vector3 = None, quantity: int = 1):
        super().__init__(EntityType.ITEM, position or Vector3(0, 64, 0))
        self.item_name = item_name
        self.quantity = quantity
        self.pickup_cooldown = 0.5  # Can't be picked up immediately
        self.lifetime = 300.0  # Despawn after 5 minutes
        self.time_alive = 0.0
        
        self.collision_box = {
            'width': 0.25,
            'height': 0.25,
            'depth': 0.25
        }
    
    def update(self, delta_time: float):
        """Update item state."""
        self.pickup_cooldown = max(0, self.pickup_cooldown - delta_time)
        self.time_alive += delta_time
        
        if self.time_alive >= self.lifetime:
            self.active = False
        
        # Apply physics
        self.apply_physics(delta_time)


class Projectile(Entity):
    """Projectile entity (arrows, etc)."""
    
    def __init__(self, projectile_type: str, position: Vector3, velocity: Vector3, owner_id: str):
        super().__init__(EntityType.PROJECTILE, position)
        self.projectile_type = projectile_type
        self.velocity = velocity
        self.owner_id = owner_id
        self.lifetime = 10.0  # Despawn after 10 seconds
        self.time_alive = 0.0
        self.has_hit = False
        
        self.collision_box = {
            'width': 0.1,
            'height': 0.1,
            'depth': 0.1
        }
    
    def update(self, delta_time: float):
        """Update projectile state."""
        if self.has_hit:
            self.active = False
            return
        
        self.time_alive += delta_time
        
        if self.time_alive >= self.lifetime:
            self.active = False
        
        # Apply physics
        self.apply_physics(delta_time)
