"""Pathfinding algorithms."""
from typing import List, Dict, Tuple, Optional
from game.math_utils import Vector3
import heapq
import math


class Node:
    """Pathfinding node."""
    
    def __init__(self, position: Vector3):
        self.position = position
        self.g_cost = float('inf')  # Cost from start
        self.h_cost = 0  # Heuristic cost to goal
        self.f_cost = float('inf')  # Total cost
        self.parent = None
    
    def __lt__(self, other):
        return self.f_cost < other.f_cost
    
    def __eq__(self, other):
        return self.position.distance_to(other.position) < 0.1


class PathFinder:
    """A* pathfinding implementation."""
    
    def __init__(self, grid_size: float = 1.0):
        self.grid_size = grid_size
        self.nodes: Dict[str, Node] = {}
    
    def _get_key(self, pos: Vector3) -> str:
        """Get dictionary key for position."""
        return f"{int(pos.x)},{int(pos.y)},{int(pos.z)}"
    
    def _heuristic(self, pos1: Vector3, pos2: Vector3) -> float:
        """Calculate heuristic distance (Manhattan distance)."""
        return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y) + abs(pos1.z - pos2.z)
    
    def _get_neighbors(self, pos: Vector3) -> List[Vector3]:
        """Get neighboring positions."""
        neighbors = []
        for dx in [-self.grid_size, 0, self.grid_size]:
            for dy in [-self.grid_size, 0, self.grid_size]:
                for dz in [-self.grid_size, 0, self.grid_size]:
                    if dx == 0 and dy == 0 and dz == 0:
                        continue
                    neighbor = Vector3(pos.x + dx, pos.y + dy, pos.z + dz)
                    neighbors.append(neighbor)
        return neighbors
    
    def find_path(self, start: Vector3, goal: Vector3, max_iterations: int = 1000) -> List[Vector3]:
        """Find path from start to goal using A*."""
        start_key = self._get_key(start)
        goal_key = self._get_key(goal)
        
        # Initialize start node
        start_node = Node(start)
        start_node.g_cost = 0
        start_node.h_cost = self._heuristic(start, goal)
        start_node.f_cost = start_node.h_cost
        
        open_set = [start_node]
        closed_set = set()
        self.nodes = {start_key: start_node}
        
        iterations = 0
        while open_set and iterations < max_iterations:
            iterations += 1
            
            # Get node with lowest f_cost
            current = heapq.heappop(open_set)
            current_key = self._get_key(current.position)
            
            if current_key == goal_key:
                # Reconstruct path
                path = []
                node = current
                while node:
                    path.append(node.position)
                    node = node.parent
                return list(reversed(path))
            
            closed_set.add(current_key)
            
            # Check neighbors
            for neighbor_pos in self._get_neighbors(current.position):
                neighbor_key = self._get_key(neighbor_pos)
                
                if neighbor_key in closed_set:
                    continue
                
                # Calculate costs
                g_cost = current.g_cost + current.position.distance_to(neighbor_pos)
                h_cost = self._heuristic(neighbor_pos, goal)
                f_cost = g_cost + h_cost
                
                # Check if we've found a better path
                if neighbor_key in self.nodes:
                    neighbor = self.nodes[neighbor_key]
                    if g_cost < neighbor.g_cost:
                        neighbor.g_cost = g_cost
                        neighbor.h_cost = h_cost
                        neighbor.f_cost = f_cost
                        neighbor.parent = current
                else:
                    neighbor = Node(neighbor_pos)
                    neighbor.g_cost = g_cost
                    neighbor.h_cost = h_cost
                    neighbor.f_cost = f_cost
                    neighbor.parent = current
                    self.nodes[neighbor_key] = neighbor
                    heapq.heappush(open_set, neighbor)
        
        # No path found
        return [start, goal]  # Return direct line
    
    def clear(self):
        """Clear pathfinding cache."""
        self.nodes.clear()
