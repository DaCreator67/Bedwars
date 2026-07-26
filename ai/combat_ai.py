"""Combat AI system."""
from typing import Optional
from game.entities import Player, Bot
from game.math_utils import Vector3
import random
import config


class CombatAI:
    """Advanced combat decision making."""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.target = None
        self.target_update_timer = 0.0
        self.attack_timer = 0.0
        self.dodge_timer = 0.0
        self.combo_hits = 0
    
    def update(self, delta_time: float, nearby_enemies: list):
        """Update combat AI."""
        self.target_update_timer += delta_time
        self.attack_timer += delta_time
        self.dodge_timer = max(0, self.dodge_timer - delta_time)
        
        # Update target every 0.5 seconds
        if self.target_update_timer >= 0.5:
            self.target = self._select_target(nearby_enemies)
            self.target_update_timer = 0.0
        
        if self.target and self.target.is_alive:
            self._execute_combat()
        else:
            self.target = None
    
    def _select_target(self, enemies: list) -> Optional[Player]:
        """Select best target based on AI difficulty and strategy."""
        if not enemies:
            return None
        
        difficulty = self.bot.difficulty
        
        # Lower difficulty bots pick random targets
        if difficulty['aggression'] < 0.5:
            return random.choice(enemies)
        
        # Higher difficulty bots pick strategically
        # Prioritize low health, weak characters, or close enemies
        def score_target(enemy):
            score = 0
            
            # Distance (closer = higher priority)
            distance = self.bot.position.distance_to(enemy.position)
            score -= distance * 0.1
            
            # Health (lower = higher priority)
            health_ratio = enemy.health / enemy.max_health
            score -= health_ratio * 50
            
            # Team size (target isolated enemies)
            team_alive = sum(1 for p in self.bot.game_manager.game_mode.teams[enemy.team_id] if p.is_alive)
            if team_alive == 1:
                score -= 20  # Prefer isolated targets
            
            return score
        
        return max(enemies, key=score_target)
    
    def _execute_combat(self):
        """Execute combat moves."""
        distance = self.bot.position.distance_to(self.target.position)
        
        # Move towards target
        direction = (self.target.position - self.bot.position).normalize()
        self.bot.input_direction = direction
        
        # Melee attack
        if distance < config.PLAYER_REACH:
            if self.attack_timer >= config.MELEE_COOLDOWN * (1 - self.bot.difficulty['accuracy']):
                self.bot.last_melee_time = 0.0
                self.attack_timer = 0.0
                self.combo_hits += 1
        
        # Dodge if low health
        if self.bot.health < self.bot.max_health * 0.3 and self.dodge_timer <= 0:
            # Jump and move sideways
            self.bot.velocity.y = config.PLAYER_JUMP_FORCE
            side_direction = Vector3(-direction.z, 0, direction.x)  # Perpendicular
            self.bot.input_direction = side_direction
            self.dodge_timer = 1.0
    
    def get_combat_stats(self) -> dict:
        """Get combat statistics."""
        return {
            'current_target': self.target.username if self.target else None,
            'combo_hits': self.combo_hits,
            'difficulty_level': self.bot.level
        }
