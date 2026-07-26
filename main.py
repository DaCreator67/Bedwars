"""Main application entry point and game loop."""
import pygame
import sys
import time
from enum import Enum
from pygame.locals import *
from OpenGL.GL import *

from config import *
from auth.database import DatabaseManager
from auth.encryption import PasswordEncryption
from game.game_manager import GameManager, GameState
from game.game_modes import ClassicMode, LuckyblockMode
from game.entities import Player, Bot
from game.math_utils import Vector3
from game.rendering import GameRenderer
from shop.shop_manager import ShopManager
from shop.characters import CharacterManager
from ui.menu import MainMenu, MenuState
from ui.screens import AuthScreen, AuthMode, GameModeSelector
from ui.hud import GameHUD
from ui.shop_ui import ShopUI


class AppState(Enum):
    """Main application states."""
    AUTH = "auth"
    MAIN_MENU = "main_menu"
    GAME_MODE_SELECT = "game_mode_select"
    SHOP = "shop"
    LOADING = "loading"
    PLAYING = "playing"
    GAME_OVER = "game_over"
    QUIT = "quit"


class BedwarsGame:
    """Main game application."""
    
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), DOUBLEBUF | OPENGL)
        pygame.display.set_caption(WINDOW_TITLE)
        
        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT
        self.running = True
        self.clock = pygame.time.Clock()
        self.current_state = AppState.AUTH
        self.current_player = None
        
        # Database
        self.db_manager = DatabaseManager(DB_PATH)
        
        # UI Screens
        self.auth_screen = AuthScreen(self.width, self.height)
        self.main_menu = MainMenu(self.width, self.height)
        self.game_mode_selector = GameModeSelector(self.width, self.height)
        self.shop_ui = ShopUI(self.width, self.height)
        
        # Game components
        self.game_manager = None
        self.game_renderer = None
        self.game_hud = None
        self.shop_manager = ShopManager(self.db_manager)
        self.character_manager = CharacterManager()
        
        # Temporary 2D surface for UI rendering
        self.ui_surface = pygame.Surface((self.width, self.height))
    
    def run(self):
        """Main game loop."""
        while self.running and self.current_state != AppState.QUIT:
            delta_time = self.clock.tick(FPS) / 1000.0
            
            self._handle_events()
            self._update(delta_time)
            self._render()
        
        self._cleanup()
    
    def _handle_events(self):
        """Handle input events."""
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        events = pygame.event.get()
        
        for event in events:
            if event.type == QUIT:
                self.running = False
            
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if self.current_state == AppState.PLAYING:
                        self.current_state = AppState.MAIN_MENU
            
            if self.current_state == AppState.AUTH:
                self.auth_screen.update(mouse_pos, mouse_pressed, events)
            elif self.current_state == AppState.MAIN_MENU:
                self.main_menu.update(mouse_pos, mouse_pressed, events)
            elif self.current_state == AppState.GAME_MODE_SELECT:
                self.game_mode_selector.update(mouse_pos, mouse_pressed)
            elif self.current_state == AppState.SHOP:
                self.shop_ui.update(mouse_pos, mouse_pressed)
            elif self.current_state == AppState.PLAYING:
                self._handle_game_input(event, mouse_pos, mouse_pressed)
    
    def _handle_game_input(self, event, mouse_pos, mouse_pressed):
        """Handle in-game input."""
        if not self.current_player:
            return
        
        # Keyboard input
        if event.type == KEYDOWN:
            if event.key == K_w:
                self.current_player.input_direction.z -= 1
            elif event.key == K_s:
                self.current_player.input_direction.z += 1
            elif event.key == K_a:
                self.current_player.input_direction.x -= 1
            elif event.key == K_d:
                self.current_player.input_direction.x += 1
            elif event.key == K_SPACE:
                if self.current_player.on_ground:
                    self.current_player.velocity.y = PLAYER_JUMP_FORCE
            elif event.key == K_LSHIFT:
                self.current_player.is_sprinting = True
        
        elif event.type == KEYUP:
            if event.key == K_w:
                self.current_player.input_direction.z += 1
            elif event.key == K_s:
                self.current_player.input_direction.z -= 1
            elif event.key == K_a:
                self.current_player.input_direction.x += 1
            elif event.key == K_d:
                self.current_player.input_direction.x -= 1
            elif event.key == K_LSHIFT:
                self.current_player.is_sprinting = False
        
        # Mouse input
        if event.type == MOUSEMOTION:
            # Update camera look
            rel_x, rel_y = event.rel
            self.current_player.yaw -= rel_x * 0.1
            self.current_player.pitch -= rel_y * 0.1
        
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click - melee
                self.game_manager.player_attack_melee(self.current_player.player_id)
            elif event.button == 3:  # Right click - bow
                direction = Vector3(
                    -math.sin(math.radians(self.current_player.yaw)),
                    -math.sin(math.radians(self.current_player.pitch)),
                    math.cos(math.radians(self.current_player.yaw))
                )
                self.game_manager.player_shoot_arrow(self.current_player.player_id, direction)
    
    def _update(self, delta_time: float):
        """Update game state."""
        if self.current_state == AppState.AUTH:
            action = self.auth_screen.get_action()
            if action:
                self._handle_auth_action(action)
        
        elif self.current_state == AppState.MAIN_MENU:
            action = self.main_menu.get_action()
            if action == "play":
                self.current_state = AppState.GAME_MODE_SELECT
            elif action == "shop":
                self.current_state = AppState.SHOP
            elif action == "quit":
                self.running = False
        
        elif self.current_state == AppState.GAME_MODE_SELECT:
            action = self.game_mode_selector.get_action()
            if action and action['action'] == "start_game":
                self._start_game(action)
            elif action and action['action'] == "back":
                self.current_state = AppState.MAIN_MENU
        
        elif self.current_state == AppState.SHOP:
            action = self.shop_ui.get_action()
            if action and action['action'] == "back":
                self.current_state = AppState.MAIN_MENU
        
        elif self.current_state == AppState.PLAYING:
            if self.game_manager:
                self.game_manager.update(delta_time)
                
                # Check if game ended
                if self.game_manager.state == GameState.FINISHED:
                    self._handle_game_end()
    
    def _render(self):
        """Render current state."""
        if self.current_state == AppState.AUTH:
            self._render_auth()
        elif self.current_state == AppState.MAIN_MENU:
            self._render_main_menu()
        elif self.current_state == AppState.GAME_MODE_SELECT:
            self._render_game_mode_select()
        elif self.current_state == AppState.SHOP:
            self._render_shop()
        elif self.current_state == AppState.PLAYING:
            self._render_game()
    
    def _render_auth(self):
        """Render auth screen."""
        self.auth_screen.draw(self.ui_surface)
        self._display_2d_surface()
    
    def _render_main_menu(self):
        """Render main menu."""
        self.main_menu.draw(self.ui_surface)
        self._display_2d_surface()
    
    def _render_game_mode_select(self):
        """Render game mode selection."""
        self.game_mode_selector.draw(self.ui_surface)
        self._display_2d_surface()
    
    def _render_shop(self):
        """Render shop."""
        if self.current_player:
            shop_data = self.shop_manager.get_shop_data(self.current_player['id'])
            self.shop_ui.draw(self.ui_surface, shop_data)
        self._display_2d_surface()
    
    def _render_game(self):
        """Render 3D game."""
        if not self.game_manager or not self.current_player:
            return
        
        # Render 3D world
        self.game_renderer.render_world(self.game_manager.entities, self.game_manager.players[self.current_player['id']])
        
        # Render HUD
        self.game_hud.draw_player_stats(self.ui_surface, self.game_manager.players[self.current_player['id']])
        self.game_hud.draw_inventory(self.ui_surface, self.game_manager.players[self.current_player['id']])
        self.game_hud.draw_team_info(self.ui_surface, self.game_manager.get_game_info())
        self.game_hud.draw_crosshair(self.ui_surface)
        
        pygame.display.flip()
    
    def _display_2d_surface(self):
        """Display 2D Pygame surface on OpenGL context."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        
        # Convert and display surface
        # Note: Full implementation would use texture mapping
        pygame.display.flip()
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_DEPTH_TEST)
    
    def _handle_auth_action(self, action: dict):
        """Handle authentication action."""
        if action['action'] == 'authenticate':
            if action['mode'] == 'login':
                player_data = self.db_manager.authenticate_player(action['username'], action['password'])
                if player_data:
                    self.current_player = player_data
                    self.current_state = AppState.MAIN_MENU
                else:
                    self.auth_screen.show_error("Invalid credentials")
            
            elif action['mode'] == 'signup':
                if len(action['username']) < 3:
                    self.auth_screen.show_error("Username too short")
                elif len(action['password']) < 6:
                    self.auth_screen.show_error("Password too short")
                else:
                    success = self.db_manager.create_account(action['username'], action['password'], action['email'])
                    if success:
                        self.auth_screen.show_error("Account created! Please login.")
                        self.auth_screen.set_mode(AuthMode.LOGIN)
                    else:
                        self.auth_screen.show_error("Username already taken")
        
        elif action['action'] == 'back':
            self.current_state = AppState.MAIN_MENU
    
    def _start_game(self, mode_action: dict):
        """Start a new game."""
        self.current_state = AppState.LOADING
        
        # Create game mode
        category = mode_action['game_mode_category']
        mode_name = mode_action['game_mode']
        
        if category == 'classic':
            game_mode = ClassicMode(mode_name)
        else:
            game_mode = LuckyblockMode(mode_name)
        
        # Create game manager
        self.game_manager = GameManager(game_mode, self.db_manager)
        self.game_renderer = GameRenderer(self.width, self.height)
        self.game_hud = GameHUD(self.width, self.height)
        
        # Add player
        player_entity = Player(
            self.current_player['id'],
            self.current_player['username'],
            -1  # Team will be assigned
        )
        
        # Apply selected character
        if self.current_player['current_character']:
            self.character_manager.apply_character_to_player(player_entity, self.current_player['current_character'])
        
        self.game_manager.add_player(player_entity)
        self.current_player['entity'] = player_entity
        
        # Add bots if in bot mode
        if mode_action.get('bot_mode'):
            num_bots = game_mode.max_players - 1
            bot_names = ['Bot_Alpha', 'Bot_Beta', 'Bot_Gamma', 'Bot_Delta', 'Bot_Epsilon',
                        'Bot_Zeta', 'Bot_Eta', 'Bot_Theta', 'Bot_Iota', 'Bot_Kappa']
            
            for i in range(num_bots):
                bot_name = bot_names[i % len(bot_names)]
                bot_level = min(30, self.current_player['level'])  # Bot level matches player
                self.game_manager.add_bot(bot_name, bot_level)
        
        # Start game
        self.game_manager.start_game()
        
        # Add starting items
        player_entity.add_inventory_item('arrow', 10)
        player_entity.add_inventory_item('stone_sword', 1)
        player_entity.add_inventory_item('wooden_pickaxe', 1)
        
        self.current_state = AppState.PLAYING
    
    def _handle_game_end(self):
        """Handle game end."""
        results = self.game_manager.end_game()
        
        # Show results
        player_id = self.current_player['id']
        if player_id in results:
            player_result = results[player_id]
            print(f"\nGame Over!")
            print(f"Placement: {player_result['placement']}")
            print(f"Kills: {player_result['kills']}")
            print(f"Deaths: {player_result['deaths']}")
            print(f"Coins Earned: {player_result['coins_earned']}")
        
        self.current_state = AppState.MAIN_MENU
    
    def _cleanup(self):
        """Cleanup before exit."""
        pygame.quit()


def main():
    """Main entry point."""
    try:
        game = BedwarsGame()
        game.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)


if __name__ == "__main__":
    import math
    main()
