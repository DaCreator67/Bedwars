"""In-game HUD and UI elements."""
import pygame
from typing import Dict, List
from game.entities import Player


class GameHUD:
    """Heads-up display for gameplay."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.font_large = pygame.font.Font(None, 48)
        self.font_normal = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 18)
    
    def draw_player_stats(self, surface: pygame.Surface, player: Player):
        """Draw player stats in bottom left."""
        x, y = 20, self.height - 200
        
        # Health bar
        bar_width = 200
        bar_height = 20
        health_ratio = max(0, player.health / player.max_health)
        
        pygame.draw.rect(surface, (50, 50, 50), (x, y, bar_width, bar_height))
        pygame.draw.rect(surface, (100, 200, 100), (x, y, int(bar_width * health_ratio), bar_height))
        pygame.draw.rect(surface, (200, 200, 200), (x, y, bar_width, bar_height), 2)
        
        # Health text
        health_text = self.font_small.render(f"HP: {int(player.health)}/{int(player.max_health)}", True, (255, 255, 255))
        surface.blit(health_text, (x, y + 25))
        
        # Stats
        stats_y = y + 60
        kills_text = self.font_small.render(f"Kills: {player.kills}", True, (100, 255, 100))
        deaths_text = self.font_small.render(f"Deaths: {player.deaths}", True, (255, 100, 100))
        assists_text = self.font_small.render(f"Assists: {player.assists}", True, (255, 255, 100))
        
        surface.blit(kills_text, (x, stats_y))
        surface.blit(deaths_text, (x, stats_y + 25))
        surface.blit(assists_text, (x, stats_y + 50))
    
    def draw_inventory(self, surface: pygame.Surface, player: Player):
        """Draw inventory in bottom right."""
        x = self.width - 250
        y = self.height - 150
        
        # Inventory title
        inv_title = self.font_normal.render("INVENTORY", True, (100, 255, 150))
        surface.blit(inv_title, (x, y))
        
        # Inventory items
        item_y = y + 40
        for i, (item_name, quantity) in enumerate(player.inventory.items()):
            if i > 5:  # Show max 5 items
                more_text = self.font_small.render(f"... +{len(player.inventory) - 5} more", True, (200, 200, 200))
                surface.blit(more_text, (x, item_y))
                break
            
            item_text = self.font_small.render(f"{item_name}: {quantity}", True, (200, 200, 200))
            surface.blit(item_text, (x, item_y))
            item_y += 25
    
    def draw_team_info(self, surface: pygame.Surface, game_info: dict):
        """Draw team information."""
        x = self.width // 2 - 100
        y = 20
        
        # Game mode
        mode_text = self.font_normal.render(f"Mode: {game_info.get('mode', 'N/A')}", True, (100, 255, 150))
        surface.blit(mode_text, (x, y))
        
        # Game time
        duration = int(game_info.get('duration', 0))
        minutes = duration // 60
        seconds = duration % 60
        time_text = self.font_normal.render(f"Time: {minutes:02d}:{seconds:02d}", True, (100, 255, 150))
        surface.blit(time_text, (x, y + 40))
        
        # Teams info
        teams = game_info.get('teams', {})
        team_y = y + 90
        for team_id, team_data in teams.items():
            team_color = self._get_team_color(team_id)
            team_status = "BED: ✓" if team_data['bed_alive'] else "BED: ✗"
            team_text = f"Team {team_id + 1}: {team_data['alive']}/{team_data['players']} {team_status}"
            team_surf = self.font_tiny.render(team_text, True, team_color)
            surface.blit(team_surf, (x, team_y))
            team_y += 20
    
    def draw_crosshair(self, surface: pygame.Surface):
        """Draw aiming crosshair."""
        center_x = self.width // 2
        center_y = self.height // 2
        size = 10
        thickness = 2
        color = (100, 255, 100)
        
        # Horizontal line
        pygame.draw.line(surface, color, (center_x - size, center_y), (center_x + size, center_y), thickness)
        # Vertical line
        pygame.draw.line(surface, color, (center_x, center_y - size), (center_x, center_y + size), thickness)
    
    def draw_minimap(self, surface: pygame.Surface, player: Player, all_players: List[Player]):
        """Draw minimap in top right."""
        minimap_x = self.width - 200
        minimap_y = 20
        minimap_size = 180
        
        # Background
        pygame.draw.rect(surface, (30, 30, 50), (minimap_x, minimap_y, minimap_size, minimap_size))
        pygame.draw.rect(surface, (100, 100, 150), (minimap_x, minimap_y, minimap_size, minimap_size), 2)
        
        # Scale for minimap (100 units = 1 pixel)
        scale = minimap_size / 200
        
        # Draw player
        player_px = int(minimap_x + (player.position.x + 100) * scale)
        player_py = int(minimap_y + (player.position.z + 100) * scale)
        pygame.draw.circle(surface, (100, 255, 100), (player_px, player_py), 3)
        
        # Draw other players
        for other_player in all_players:
            if other_player.player_id == player.player_id:
                continue
            
            color = (100, 100, 255) if other_player.team_id == player.team_id else (255, 100, 100)
            other_px = int(minimap_x + (other_player.position.x + 100) * scale)
            other_py = int(minimap_y + (other_player.position.z + 100) * scale)
            pygame.draw.circle(surface, color, (other_px, other_py), 2)
    
    def draw_damage_indicator(self, surface: pygame.Surface, damage_direction: tuple, intensity: float):
        """Draw damage vignette effect."""
        # Create red vignette from damage direction
        vignette_color = (255, int(100 * intensity), int(100 * intensity))
        alpha = int(50 * intensity)
        
        # Create damage vignette surface
        vignette = pygame.Surface((self.width, self.height))
        vignette.fill(vignette_color)
        vignette.set_alpha(alpha)
        surface.blit(vignette, (0, 0))
    
    @staticmethod
    def _get_team_color(team_id: int) -> tuple:
        """Get color for team ID."""
        colors = [
            (255, 100, 100),  # Red
            (100, 150, 255),  # Blue
            (100, 255, 100),  # Green
            (255, 255, 100),  # Yellow
            (255, 150, 100),  # Orange
            (200, 100, 255),  # Purple
        ]
        return colors[team_id % len(colors)]
