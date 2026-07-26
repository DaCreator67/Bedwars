"""Physics system for the game."""
from typing import List
from .entities import Entity, Player, Item, Projectile
from .math_utils import Vector3
import config


class PhysicsEngine:
    """Handle physics simulation."""
    
    def __init__(self):
        self.gravity = config.DEFAULT_GRAVITY
        self.ground_level = 0.0
    
    def update(self, entities: List[Entity], delta_time: float):
        """Update physics for all entities."""
        for entity in entities:
            if not entity.active:
                continue
            
            # Apply physics
            entity.apply_physics(delta_time, self.gravity)
            
            # Ground collision
            if entity.position.y < self.ground_level:
                entity.position.y = self.ground_level
                if isinstance(entity, (Player, Item)):
                    entity.on_ground = True
                    entity.velocity.y = 0
                    entity.can_double_jump = True
            else:
                if isinstance(entity, Player):
                    entity.on_ground = False
    
    def check_collisions(self, entities: List[Entity]) -> List[tuple]:
        """Check for collisions between entities."""
        collisions = []
        
        for i, entity1 in enumerate(entities):
            if not entity1.active:
                continue
            
            for entity2 in entities[i+1:]:
                if not entity2.active:
                    continue
                
                if self._check_collision(entity1, entity2):
                    collisions.append((entity1, entity2))
        
        return collisions
    
    def _check_collision(self, entity1: Entity, entity2: Entity) -> bool:
        """Check if two entities are colliding (AABB)."""
        if not entity1.collision_box or not entity2.collision_box:
            return False
        
        box1 = entity1.collision_box
        box2 = entity2.collision_box
        
        # Get bounding box coordinates
        x1_min = entity1.position.x - box1['width'] / 2
        x1_max = entity1.position.x + box1['width'] / 2
        y1_min = entity1.position.y - box1['height'] / 2
        y1_max = entity1.position.y + box1['height'] / 2
        z1_min = entity1.position.z - box1['depth'] / 2
        z1_max = entity1.position.z + box1['depth'] / 2
        
        x2_min = entity2.position.x - box2['width'] / 2
        x2_max = entity2.position.x + box2['width'] / 2
        y2_min = entity2.position.y - box2['height'] / 2
        y2_max = entity2.position.y + box2['height'] / 2
        z2_min = entity2.position.z - box2['depth'] / 2
        z2_max = entity2.position.z + box2['depth'] / 2
        
        # AABB collision detection
        return (x1_min < x2_max and x1_max > x2_min and
                y1_min < y2_max and y1_max > y2_min and
                z1_min < z2_max and z1_max > z2_min)
    
    def get_distance(self, entity1: Entity, entity2: Entity) -> float:
        """Get distance between two entities."""
        return entity1.position.distance_to(entity2.position)
