"""Physics system for collision detection and movement."""
import numpy as np
from typing import List, Optional, Tuple
from .entities import Entity, Vector3
import config


class BoundingBox:
    """3D bounding box for collision detection."""
    
    def __init__(self, center: Vector3, width: float, height: float, depth: float):
        """Initialize a bounding box.
        
        Args:
            center: Center position
            width: Width (X axis)
            height: Height (Y axis)
            depth: Depth (Z axis)
        """
        self.center = center
        self.width = width
        self.height = height
        self.depth = depth
    
    def get_bounds(self) -> Tuple[Vector3, Vector3]:
        """Get min and max corners of bounding box."""
        min_corner = Vector3(
            self.center.x - self.width / 2,
            self.center.y - self.height / 2,
            self.center.z - self.depth / 2
        )
        max_corner = Vector3(
            self.center.x + self.width / 2,
            self.center.y + self.height / 2,
            self.center.z + self.depth / 2
        )
        return min_corner, max_corner
    
    def intersects(self, other: 'BoundingBox') -> bool:
        """Check if this bounding box intersects with another."""
        min1, max1 = self.get_bounds()
        min2, max2 = other.get_bounds()
        
        # Check all axes
        return (min1.x <= max2.x and max1.x >= min2.x and
                min1.y <= max2.y and max1.y >= min2.y and
                min1.z <= max2.z and max1.z >= min2.z)
    
    def contains_point(self, point: Vector3) -> bool:
        """Check if point is inside this bounding box."""
        min_corner, max_corner = self.get_bounds()
        return (min_corner.x <= point.x <= max_corner.x and
                min_corner.y <= point.y <= max_corner.y and
                min_corner.z <= point.z <= max_corner.z)


class Sphere:
    """3D sphere for collision detection."""
    
    def __init__(self, center: Vector3, radius: float):
        """Initialize a sphere.
        
        Args:
            center: Center position
            radius: Radius
        """
        self.center = center
        self.radius = radius
    
    def intersects_box(self, bbox: BoundingBox) -> bool:
        """Check if sphere intersects with bounding box."""
        # Find closest point on box to sphere center
        min_corner, max_corner = bbox.get_bounds()
        
        closest = Vector3(
            max(min_corner.x, min(self.center.x, max_corner.x)),
            max(min_corner.y, min(self.center.y, max_corner.y)),
            max(min_corner.z, min(self.center.z, max_corner.z))
        )
        
        distance = self.center.distance_to(closest)
        return distance < self.radius
    
    def intersects_sphere(self, other: 'Sphere') -> bool:
        """Check if this sphere intersects with another."""
        distance = self.center.distance_to(other.center)
        return distance < (self.radius + other.radius)
    
    def contains_point(self, point: Vector3) -> bool:
        """Check if point is inside this sphere."""
        distance = self.center.distance_to(point)
        return distance < self.radius


class PhysicsEngine:
    """Handles physics simulation for the game."""
    
    def __init__(self):
        """Initialize physics engine."""
        self.gravity = config.DEFAULT_GRAVITY
        self.entities: List[Entity] = []
        self.colliders: List[Tuple[Entity, BoundingBox]] = []
        self.static_colliders: List[BoundingBox] = []
    
    def add_entity(self, entity: Entity):
        """Add entity to physics simulation."""
        if entity not in self.entities:
            self.entities.append(entity)
    
    def remove_entity(self, entity: Entity):
        """Remove entity from physics simulation."""
        if entity in self.entities:
            self.entities.remove(entity)
        
        # Remove associated collider
        self.colliders = [(e, b) for e, b in self.colliders if e != entity]
    
    def add_collider(self, entity: Entity, bbox: BoundingBox):
        """Add bounding box collider to entity."""
        # Remove old collider if exists
        self.colliders = [(e, b) for e, b in self.colliders if e != entity]
        self.colliders.append((entity, bbox))
    
    def add_static_collider(self, bbox: BoundingBox):
        """Add static collider (e.g., walls, floor)."""
        self.static_colliders.append(bbox)
    
    def update(self, delta_time: float):
        """Update physics simulation.
        
        Args:
            delta_time: Time step in seconds
        """
        # Apply gravity to all entities
        for entity in self.entities:
            entity.velocity.y -= self.gravity * delta_time
            entity.position = entity.position + entity.velocity * delta_time
        
        # Collision detection and response
        self._resolve_collisions()
    
    def _resolve_collisions(self):
        """Resolve entity collisions."""
        # Check entity-static collisions
        for entity, entity_bbox in self.colliders:
            entity_bbox.center = entity.position
            
            for static_bbox in self.static_colliders:
                if entity_bbox.intersects(static_bbox):
                    self._resolve_collision(entity, entity_bbox, static_bbox)
        
        # Check entity-entity collisions
        for i, (entity1, bbox1) in enumerate(self.colliders):
            for entity2, bbox2 in self.colliders[i+1:]:
                bbox1.center = entity1.position
                bbox2.center = entity2.position
                
                if bbox1.intersects(bbox2):
                    self._resolve_entity_collision(entity1, entity2, bbox1, bbox2)
    
    def _resolve_collision(self, entity: Entity, entity_bbox: BoundingBox, 
                          static_bbox: BoundingBox):
        """Resolve collision between entity and static object."""
        # Simple response: stop vertical movement if hitting ground
        if entity.velocity.y < 0:  # Falling
            min_e, max_e = entity_bbox.get_bounds()
            min_s, max_s = static_bbox.get_bounds()
            
            if max_e.y >= min_s.y and entity.position.y > static_bbox.center.y:
                entity.position.y = max_s.y + entity_bbox.height / 2
                entity.velocity.y = 0
    
    def _resolve_entity_collision(self, entity1: Entity, entity2: Entity,
                                  bbox1: BoundingBox, bbox2: BoundingBox):
        """Resolve collision between two entities (simple separation)."""
        # Calculate collision normal and depth
        center1 = bbox1.center
        center2 = bbox2.center
        
        direction = center2 - center1
        distance = direction.distance_to(Vector3(0, 0, 0))
        
        if distance == 0:
            return
        
        # Normalize direction
        direction = direction * (1.0 / distance)
        
        # Separate entities
        separation = 0.01  # Small separation distance
        entity1.position = entity1.position - direction * separation
        entity2.position = entity2.position + direction * separation
    
    def raycast(self, origin: Vector3, direction: Vector3, 
                max_distance: float) -> Optional[Tuple[Entity, float, Vector3]]:
        """Cast a ray and find first intersection.
        
        Args:
            origin: Ray origin
            direction: Ray direction (should be normalized)
            max_distance: Maximum ray distance
            
        Returns:
            Tuple of (entity, distance, intersection_point) or None
        """
        nearest_hit = None
        nearest_distance = max_distance
        
        for entity, bbox in self.colliders:
            distance = self._raycast_bbox(origin, direction, bbox, max_distance)
            if distance is not None and distance < nearest_distance:
                intersection = origin + direction * distance
                nearest_hit = (entity, distance, intersection)
                nearest_distance = distance
        
        return nearest_hit
    
    def _raycast_bbox(self, origin: Vector3, direction: Vector3, 
                      bbox: BoundingBox, max_distance: float) -> Optional[float]:
        """Raycast against a bounding box."""
        min_corner, max_corner = bbox.get_bounds()
        
        # Slab intersection algorithm
        t_min = 0.0
        t_max = max_distance
        
        for axis_idx in range(3):
            axis_origin = origin.to_tuple()[axis_idx]
            axis_dir = direction.to_tuple()[axis_idx]
            axis_min = min_corner.to_tuple()[axis_idx]
            axis_max = max_corner.to_tuple()[axis_idx]
            
            if abs(axis_dir) < 1e-6:
                if axis_origin < axis_min or axis_origin > axis_max:
                    return None
            else:
                t1 = (axis_min - axis_origin) / axis_dir
                t2 = (axis_max - axis_origin) / axis_dir
                
                if t1 > t2:
                    t1, t2 = t2, t1
                
                t_min = max(t_min, t1)
                t_max = min(t_max, t2)
                
                if t_min > t_max:
                    return None
        
        if t_min >= 0:
            return t_min
        
        return None
