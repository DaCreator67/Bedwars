"""In-game UI and rendering."""
import pygame
from typing import Dict
from game.game_manager import GameManager
from game.game_modes import GameMode
from auth.database import DatabaseManager
import config


class GameUI:
    """Handles in-game UI and rendering."""
    
    def __init__(self, game_mode: GameMode, db_manager: DatabaseManager, 
                 player_data: Dict, character: str):
        """Initialize game UI.
        
        Args:
            game_mode: Game mode to play
            db_manager: Database manager
            player_data: Current player data from database
            character: Selected character
        """
        self.game_mode = game_mode
        self.db_manager = db_manager
        self.player_data = player_data
        self.character = character
        
        # Initialize game manager
        self.game_manager = GameManager(game_mode, db_manager)
        
        # Add player to game
        self.player = self.game_manager.add_player(
            player_data['id'],
            player_data['username'],
            character
        )
        
        # Add bots to fill teams
        self._add_bots()
        
        # Start game
        self.game_manager.start_game()
        
        # UI state
        self.show_debug_info = True
        self.paused = False
        
        # Initialize Pygame rendering (if not already done)
        if not pygame.display.get_surface():
            self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        else:
            self.screen = pygame.display.get_surface()
        
        pygame.display.set_caption(config.WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_large = pygame.font.Font(None, 48)
    
    def _add_bots(self):
        """Add AI bots to fill remaining team slots."""
        # Calculate how many bots needed
        total_slots = self.game_mode.max_players
        human_players = 1  # This player
        bots_needed = total_slots - human_players
        
        # Add bots distributed across teams
        for i in range(bots_needed):
            difficulty = (self.player_data.get('level', 1) // 10) + 1
            difficulty = min(max(difficulty, 1), 5)
            self.game_manager.add_bot(f"Bot_{i+1}", difficulty)
    
    def run(self):
        """Main game loop."""
        running = True
        
        while running:
            dt = self.clock.tick(config.FPS) / 1000.0
            
            # Handle input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_p:
                        self.paused = not self.paused
                    elif event.key == pygame.K_f:
                        self.show_debug_info = not self.show_debug_info
            
            # Update game
            if not self.paused:
                self.game_manager.update(dt)
            
            # Render
            self._render(dt)
        
        return self.game_manager.get_game_status()
    
    def _render(self, delta_time: float):
        """Render game screen."""
        self.screen.fill((20, 30, 40))
        
        # Draw game world (simplified)
        self._draw_world()
        
        # Draw HUD
        self._draw_hud()
        
        # Draw debug info
        if self.show_debug_info:
            self._draw_debug_info()
        
        # Draw pause screen
        if self.paused:
            self._draw_pause_screen()
        
        pygame.display.flip()
    
    def _draw_world(self):
        """Draw simplified game world."""
        # Draw a simple representation of each team
        team_size = 150
        team_spacing = 20
        start_x = 50
        start_y = 100
        
        for team_id, team_data in self.game_manager.teams.items():
            x = start_x + (team_id % 2) * (team_size + team_spacing)
            y = start_y + (team_id // 2) * (team_size + team_spacing)
            
            color = team_data["color"]
            
            # Draw team square
            pygame.draw.rect(self.screen, color, (x, y, team_size, team_size), 3)
            
            # Draw team info
            team_info = self.game_manager.get_team_info(team_id)
            alive_text = self.font_small.render(
                f"Alive: {team_info['alive_count']}/{team_info['total_members']}",
                True, color
            )
            self.screen.blit(alive_text, (x + 10, y + 10))
    
    def _draw_hud(self):
        """Draw in-game HUD."""
        # Player health bar
        health_y = config.WINDOW_HEIGHT - 60
        
        # Health bar background
        pygame.draw.rect(self.screen, (100, 100, 100), (20, health_y, 400, 30))
        
        # Health bar foreground
        health_ratio = self.player.health / self.player.max_hp
        health_width = int(400 * health_ratio)
        health_color = (0, 255, 0) if health_ratio > 0.3 else (255, 0, 0)
        pygame.draw.rect(self.screen, health_color, (20, health_y, health_width, 30))
        
        # Health text
        health_text = self.font_small.render(
            f"Health: {int(self.player.health)}/{int(self.player.max_hp)}",
            True, (255, 255, 255)
        )
        self.screen.blit(health_text, (30, health_y + 5))
        
        # Game mode info
        mode_text = self.font_small.render(
            f"Mode: {self.game_mode.get_full_name()}",
            True, (200, 200, 200)
        )
        self.screen.blit(mode_text, (20, 20))
        
        # Game time
        minutes = int(self.game_manager.game_time) // 60
        seconds = int(self.game_manager.game_time) % 60
        time_text = self.font_small.render(
            f"Time: {minutes:02d}:{seconds:02d}",
            True, (200, 200, 200)
        )
        self.screen.blit(time_text, (config.WINDOW_WIDTH - 200, 20))
        
        # Stats
        stats_y = 80
        stats = [
            f"Kills: {self.player.kills}",
            f"Deaths: {self.player.deaths}",
            f"Character: {self.character}",
        ]
        
        for i, stat in enumerate(stats):
            stat_text = self.font_small.render(stat, True, (200, 200, 200))
            self.screen.blit(stat_text, (20, stats_y + i * 30))
    
    def _draw_debug_info(self):
        """Draw debug information."""
        debug_y = config.WINDOW_HEIGHT - 150
        debug_info = [
            f"Entities: {len(self.game_manager.players) + len(self.game_manager.bots)}",
            f"Game Time: {self.game_manager.game_time:.1f}s",
            f"Position: ({self.player.position.x:.1f}, {self.player.position.y:.1f}, {self.player.position.z:.1f})",
            f"Velocity: ({self.player.velocity.x:.1f}, {self.player.velocity.y:.1f}, {self.player.velocity.z:.1f})",
            f"Press F to hide debug info",
            f"Press P to pause/unpause",
            f"Press ESC to exit",
        ]
        
        for i, info in enumerate(debug_info):
            info_text = self.font_small.render(info, True, (100, 200, 100))
            self.screen.blit(info_text, (20, debug_y + i * 25))
    
    def _draw_pause_screen(self):
        """Draw pause screen overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Pause text
        pause_text = self.font_large.render("PAUSED", True, (255, 255, 255))
        pause_rect = pause_text.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 - 100))
        self.screen.blit(pause_text, pause_rect)
        
        # Instructions
        resume_text = self.font_medium.render("Press P to resume", True, (200, 200, 200))
        resume_rect = resume_text.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 + 50))
        self.screen.blit(resume_text, resume_rect)
