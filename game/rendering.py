"""3D rendering engine using OpenGL and Pygame."""
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from typing import List, Tuple
from game.entities import Player, Entity, EntityType
from game.math_utils import Vector3
import math


class Mesh:
    """Simple 3D mesh for rendering."""
    
    def __init__(self, vertices: List[Tuple], faces: List[Tuple], color: Tuple = (1, 1, 1)):
        self.vertices = vertices
        self.faces = faces
        self.color = color
        self.position = Vector3(0, 0, 0)
        self.rotation = (0, 0, 0)
        self.scale = (1, 1, 1)
    
    def render(self):
        """Render the mesh."""
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        glScalef(self.scale[0], self.scale[1], self.scale[2])
        
        glBegin(GL_TRIANGLES)
        glColor3f(*self.color)
        
        for face in self.faces:
            for vertex_id in face:
                glVertex3fv(self.vertices[vertex_id])
        
        glEnd()
        glPopMatrix()


class Cube(Mesh):
    """Simple cube mesh."""
    
    def __init__(self, size: float = 1.0, color: Tuple = (1, 1, 1)):
        half = size / 2
        vertices = [
            (-half, -half, half), (half, -half, half), (half, half, half), (-half, half, half),  # Front
            (-half, -half, -half), (half, -half, -half), (half, half, -half), (-half, half, -half),  # Back
        ]
        
        faces = [
            # Front
            (0, 1, 2), (0, 2, 3),
            # Back
            (4, 6, 5), (4, 7, 6),
            # Top
            (3, 2, 6), (3, 6, 7),
            # Bottom
            (4, 5, 1), (4, 1, 0),
            # Right
            (1, 5, 6), (1, 6, 2),
            # Left
            (4, 0, 3), (4, 3, 7),
        ]
        
        super().__init__(vertices, faces, color)


class Sphere(Mesh):
    """Simple sphere mesh (approximation)."""
    
    def __init__(self, radius: float = 1.0, subdivisions: int = 3, color: Tuple = (1, 1, 1)):
        vertices = []
        faces = []
        
        # Generate icosphere
        self._generate_icosphere(radius, subdivisions, vertices, faces)
        super().__init__(vertices, faces, color)
    
    def _generate_icosphere(self, radius, subdivisions, vertices, faces):
        """Generate icosphere vertices and faces."""
        # Simple sphere using latitude/longitude
        phi_segments = 16
        theta_segments = 8
        
        for i in range(theta_segments + 1):
            theta = (i / theta_segments) * math.pi
            for j in range(phi_segments):
                phi = (j / phi_segments) * 2 * math.pi
                x = radius * math.sin(theta) * math.cos(phi)
                y = radius * math.cos(theta)
                z = radius * math.sin(theta) * math.sin(phi)
                vertices.append((x, y, z))
        
        for i in range(theta_segments):
            for j in range(phi_segments):
                a = i * (phi_segments + 1) + j
                b = a + phi_segments + 1
                faces.append((a, a + 1, b))
                faces.append((a + 1, b + 1, b))


class Camera:
    """3D camera for rendering."""
    
    def __init__(self, fov: float = 45.0, near: float = 0.1, far: float = 500.0):
        self.position = Vector3(0, 2, 5)
        self.target = Vector3(0, 0, 0)
        self.up = Vector3(0, 1, 0)
        self.fov = fov
        self.near = near
        self.far = far
        self.yaw = 0.0
        self.pitch = 0.0
    
    def update_from_player(self, player: Player):
        """Update camera to follow player."""
        # Third-person camera
        distance = 3.0
        self.position = player.position + Vector3(
            math.sin(math.radians(player.yaw)) * distance,
            2.0,
            math.cos(math.radians(player.yaw)) * distance
        )
        self.target = player.position + Vector3(0, 1, 0)
    
    def setup_projection(self, width: int, height: int):
        """Setup camera projection."""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = width / height
        gluPerspective(self.fov, aspect, self.near, self.far)
        glMatrixMode(GL_MODELVIEW)
    
    def setup_view(self):
        """Setup camera view."""
        glLoadIdentity()
        gluLookAt(
            self.position.x, self.position.y, self.position.z,
            self.target.x, self.target.y, self.target.z,
            self.up.x, self.up.y, self.up.z
        )


class Light:
    """3D lighting."""
    
    def __init__(self, position: Tuple = (0, 5, 0), ambient: Tuple = (0.3, 0.3, 0.3),
                 diffuse: Tuple = (1, 1, 1), specular: Tuple = (1, 1, 1)):
        self.position = position
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
    
    def apply(self):
        """Apply lighting."""
        glLight(GL_LIGHT0, GL_POSITION, self.position + (1,))
        glLight(GL_LIGHT0, GL_AMBIENT, self.ambient + (1,))
        glLight(GL_LIGHT0, GL_DIFFUSE, self.diffuse + (1,))
        glLight(GL_LIGHT0, GL_SPECULAR, self.specular + (1,))


class GameRenderer:
    """Main 3D game renderer."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.camera = Camera()
        self.light = Light()
        self.meshes = {}
        self._setup_opengl()
    
    def _setup_opengl(self):
        """Initialize OpenGL settings."""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        glClearColor(0.1, 0.1, 0.2, 1.0)
        glShadeModel(GL_SMOOTH)
    
    def render_world(self, entities: List[Entity], player: Player):
        """Render the game world."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Setup camera
        self.camera.setup_projection(self.width, self.height)
        self.camera.update_from_player(player)
        self.camera.setup_view()
        
        # Apply lighting
        self.light.apply()
        
        # Render ground
        self._render_ground()
        
        # Render entities
        for entity in entities:
            if entity.active:
                self._render_entity(entity)
    
    def _render_ground(self):
        """Render ground plane."""
        glDisable(GL_LIGHTING)
        glBegin(GL_QUADS)
        glColor3f(0.2, 0.6, 0.2)
        size = 100
        glVertex3f(-size, 0, -size)
        glVertex3f(size, 0, -size)
        glVertex3f(size, 0, size)
        glVertex3f(-size, 0, size)
        glEnd()
        glEnable(GL_LIGHTING)
    
    def _render_entity(self, entity: Entity):
        """Render a single entity."""
        if entity.entity_type == EntityType.PLAYER or entity.entity_type == EntityType.BOT:
            self._render_player(entity)
        elif entity.entity_type == EntityType.ITEM:
            self._render_item(entity)
        elif entity.entity_type == EntityType.PROJECTILE:
            self._render_projectile(entity)
    
    def _render_player(self, player: Player):
        """Render player character."""
        glPushMatrix()
        glTranslatef(player.position.x, player.position.y, player.position.z)
        
        # Draw player body (cube)
        if player.is_alive:
            # Color based on team
            team_colors = [(1, 0, 0), (0, 0, 1), (0, 1, 0), (1, 1, 0)]  # RGBA
            color = team_colors[player.team_id % len(team_colors)]
            
            glColor3f(*color)
            cube = Cube(0.6, color)
            cube.render()
        
        glPopMatrix()
    
    def _render_item(self, item):
        """Render item in world."""
        glPushMatrix()
        glTranslatef(item.position.x, item.position.y, item.position.z)
        glColor3f(1, 1, 0)  # Yellow for items
        
        sphere = Sphere(0.3, color=(1, 1, 0))
        sphere.render()
        
        glPopMatrix()
    
    def _render_projectile(self, projectile):
        """Render projectile in world."""
        glPushMatrix()
        glTranslatef(projectile.position.x, projectile.position.y, projectile.position.z)
        glColor3f(1, 0, 0)  # Red for projectiles
        
        sphere = Sphere(0.15, color=(1, 0, 0))
        sphere.render()
        
        glPopMatrix()
    
    def render_ui(self, surface: pygame.Surface):
        """Switch to 2D rendering for UI."""
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        
        # Convert Pygame surface to OpenGL texture
        # This is simplified; full implementation would use texture mapping
    
    def restore_3d(self):
        """Restore 3D rendering mode."""
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
