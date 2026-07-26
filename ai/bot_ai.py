"""Bot AI behavior system."""
import random
import math
from enum import Enum
from typing import List, Optional
from game.entities import Player, Bot, Entity
from game.math_utils import Vector3
import config


class AIState(Enum):
    """AI behavior states."""
    IDLE = "idle"
    PATROLLING = "patrolling"
    PURSUING = "pursuing"
    ATTACKING = "attacking"
    FLEEING = "fleeing"
    DEFENDING_BED = "defending_bed"


class BotBrain:
    """AI brain for bot decision making."""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.state = AIState.IDLE
        self.state_timer = 0.0
        self.decision_interval = 0.5
        self.target = None
        self.patrol_target = None
        self.patrol_points = []
        self.current_patrol_index = 0
    
    def update(self, delta_time: float, game_state: dict, nearby_entities: List[Entity]):
        """Update AI decision and behavior."""
        self.state_timer += delta_time
        
        if self.state_timer >= self.decision_interval:
            self._make_decision(game_state, nearby_entities)
            self.state_timer = 0.0
        
        self._execute_behavior(nearby_entities)
    
    def _make_decision(self, game_state: dict, nearby_entities: List[Entity]):
        """Make strategic decision."""
        # Find nearby enemies
        enemies = [
            e for e in nearby_entities
            if isinstance(e, Player) and e.team_id != self.bot.team_id and e.is_alive
        ]
        
        if not enemies:
            # No enemies nearby, patrol
            if self.state != AIState.PATROLLING:
                self.state = AIState.PATROLLING
            return
        
        # Find nearest enemy
        nearest_enemy = min(enemies, key=lambda e: self.bot.position.distance_to(e.position))
        distance = self.bot.position.distance_to(nearest_enemy.position)
        
        # Decide action based on difficulty and health
        health_ratio = self.bot.health / self.bot.max_health
        
        if distance < 3 and health_ratio > 0.5:
            # Close range and healthy - attack
            self.state = AIState.ATTACKING
            self.target = nearest_enemy
        elif distance < 15:
            # Medium range - pursue
            self.state = AIState.PURSUING
            self.target = nearest_enemy
        elif health_ratio < 0.3:
            # Low health - flee
            self.state = AIState.FLEEING
            self.target = nearest_enemy
        else:
            # Patrol
            self.state = AIState.PATROLLING
            self.target = None
    
    def _execute_behavior(self, nearby_entities: List[Entity]):
        """Execute current behavior."""
        if self.state == AIState.ATTACKING and self.target:
            self._attack_target()
        elif self.state == AIState.PURSUING and self.target:
            self._pursue_target()
        elif self.state == AIState.FLEEING and self.target:
            self._flee_from_target()
        elif self.state == AIState.PATROLLING:
            self._patrol()
        elif self.state == AIState.IDLE:
            self._idle()
    
    def _attack_target(self):
        """Attack target enemy."""
        if not self.target or not self.target.is_alive:
            self.target = None
            return
        
        direction = (self.target.position - self.bot.position).normalize()
        self.bot.input_direction = direction
        
        distance = self.bot.position.distance_to(self.target.position)
        
        # Attack if in range
        if distance < config.PLAYER_REACH:
            if self.bot.can_attack_melee():
                self.bot.last_melee_time = 0.0
    
    def _pursue_target(self):
        """Pursue target enemy."""
        if not self.target or not self.target.is_alive:
            self.target = None
            return
        
        direction = (self.target.position - self.bot.position).normalize()
        self.bot.input_direction = direction
    
    def _flee_from_target(self):
        """Flee from target."""
        if not self.target:
            return
        
        # Run away from target
        direction = (self.bot.position - self.target.position).normalize()
        self.bot.input_direction = direction
        self.bot.is_sprinting = True
    
    def _patrol(self):
        """Patrol around spawn area."""
        if not self.patrol_points:
            # Generate patrol points around spawn
            self._generate_patrol_points()
        
        if self.patrol_points:
            target_point = self.patrol_points[self.current_patrol_index]
            direction = (target_point - self.bot.position).normalize()
            self.bot.input_direction = direction
            
            # Check if reached patrol point
            if self.bot.position.distance_to(target_point) < 2:
                self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
    
    def _idle(self):
        """Idle behavior."""
        self.bot.input_direction = Vector3(0, 0, 0)
    
    def _generate_patrol_points(self):
        """Generate patrol points around spawn."""
        spawn_x, spawn_y, spawn_z = 0, 65, 0  # Default spawn
        radius = 10
        num_points = 4
        
        self.patrol_points = []
        for i in range(num_points):
            angle = (2 * math.pi * i) / num_points
            x = spawn_x + radius * math.cos(angle)
            z = spawn_z + radius * math.sin(angle)
            self.patrol_points.append(Vector3(x, spawn_y, z))


class CombatAI:
    """Combat decision making system."""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.last_attack_time = 0.0
        self.combo_counter = 0
        self.block_cooldown = 0.0
    
    def choose_action(self, target: Player, delta_time: float) -> Optional[str]:
        """Decide which combat action to take."""
        distance = self.bot.position.distance_to(target.position)
        
        self.last_attack_time += delta_time
        self.block_cooldown = max(0, self.block_cooldown - delta_time)
        
        # Melee range
        if distance < config.PLAYER_REACH:
            if self.last_attack_time >= config.MELEE_COOLDOWN:
                self.last_attack_time = 0.0
                self.combo_counter += 1
                return "melee_attack"
        
        # Ranged range
        elif distance < 20 and "arrow" in self.bot.inventory:
            if random.random() < self.bot.difficulty['accuracy']:
                return "shoot_arrow"
        
        # Healing
        if self.bot.health < self.bot.max_health * 0.5 and "healing_potion" in self.bot.inventory:
            return "use_healing_potion"
        
        return None
    
    def predict_enemy_movement(self, target: Player) -> Vector3:
        """Predict where enemy will be."""
        # Simple prediction based on velocity
        prediction_time = 0.1  # 100ms ahead
        predicted_pos = target.position + target.velocity * prediction_time
        return predicted_pos


class PathfindingAI:
    """Pathfinding for AI navigation."""
    
    @staticmethod
    def calculate_path(start: Vector3, goal: Vector3, obstacles: List[Entity]) -> List[Vector3]:
        """Calculate simple path to goal."""
        # Simple straight-line pathfinding
        # In a full implementation, this would use A* or similar
        path = [start]
        
        direction = (goal - start).normalize()
        current = start.copy()
        step_size = 1.0
        
        while current.distance_to(goal) > step_size:
            current = current + direction * step_size
            path.append(current)
        
        path.append(goal)
        return path
    
    @staticmethod
    def avoid_obstacles(current_pos: Vector3, target_pos: Vector3, obstacles: List[Entity], avoid_radius: float = 2.0) -> Vector3:
        """Adjust movement to avoid obstacles."""
        # Check for nearby obstacles
        adjusted_target = target_pos.copy()
        
        for obstacle in obstacles:
            distance = current_pos.distance_to(obstacle.position)
            if distance < avoid_radius:
                # Push away from obstacle
                away_vector = (current_pos - obstacle.position).normalize()
                adjusted_target = adjusted_target + away_vector * 0.5
        
        return adjusted_target
