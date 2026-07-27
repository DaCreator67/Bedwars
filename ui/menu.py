"""Main menu and UI navigation."""
import pygame
from typing import Optional
from auth.database import DatabaseManager
from game.game_modes import ModeSelector, GameMode
from .game_ui import GameUI
import config


class MainMenu:
    """Main menu interface."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize main menu.
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self.running = True
        self.current_player = None
        
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        pygame.display.set_caption(config.WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        
        # Menu state
        self.menu_state = "main"  # main, auth, mode_select, character_select
        self.selected_mode: Optional[GameMode] = None
        self.available_modes = []
    
    def run(self):
        """Main menu loop."""
        while self.running:
            self._handle_events()
            self._update()
            self._render()
            self.clock.tick(config.FPS)
        
        pygame.quit()
    
    def _handle_events(self):
        """Handle input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_key_press(event.key)
    
    def _handle_key_press(self, key):
        """Handle keyboard input."""
        if self.menu_state == "main":
            if key == pygame.K_1:
                self.menu_state = "auth"
                self._show_auth_menu()
            elif key == pygame.K_2:
                self.running = False
        
        elif self.menu_state == "mode_select":
            if key == pygame.K_ESCAPE:
                self.menu_state = "main"
            elif key == pygame.K_1:
                # Classic modes
                self.available_modes = ModeSelector.get_classic_modes()
                self._show_mode_selection()
            elif key == pygame.K_2:
                # Lucky Block modes
                self.available_modes = ModeSelector.get_luckyblock_modes()
                self._show_mode_selection()
    
    def _show_auth_menu(self):
        """Show authentication menu."""
        print("\n" + "="*50)
        print("BEDWARS 3D - AUTHENTICATION")
        print("="*50)
        
        choice = input("\n1. Login\n2. Sign Up\nChoice: ").strip()
        
        if choice == "1":
            self._login()
        elif choice == "2":
            self._signup()
        else:
            print("Invalid choice")
        
        if self.current_player:
            self.menu_state = "mode_select"
    
    def _login(self):
        """Handle player login."""
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        
        player = self.db_manager.authenticate_player(username, password)
        
        if player:
            self.current_player = player
            print(f"\n✓ Welcome back, {username}!")
        else:
            print("\n✗ Login failed. Invalid username or password.")
    
    def _signup(self):
        """Handle player signup."""
        username = input("Username: ").strip()
        email = input("Email: ").strip()
        password = input("Password: ").strip()
        password_confirm = input("Confirm Password: ").strip()
        
        if password != password_confirm:
            print("✗ Passwords do not match")
            return
        
        if self.db_manager.create_account(username, password, email):
            # Now login
            player = self.db_manager.authenticate_player(username, password)
            self.current_player = player
            print(f"\n✓ Account created! Welcome, {username}!")
        else:
            print("✗ Account creation failed. Username may already exist.")
    
    def _show_mode_selection(self):
        """Show game mode selection."""
        print("\n" + "="*50)
        print("SELECT GAME MODE")
        print("="*50 + "\n")
        
        for i, mode in enumerate(self.available_modes, 1):
            print(f"{i}. {mode.get_full_name()}")
            print(f"   {mode.description}\n")
        
        choice = input("Select mode (number): ").strip()
        
        try:
            mode_index = int(choice) - 1
            if 0 <= mode_index < len(self.available_modes):
                self.selected_mode = self.available_modes[mode_index]
                self.menu_state = "character_select"
                self._show_character_selection()
        except ValueError:
            print("Invalid choice")
    
    def _show_character_selection(self):
        """Show character selection."""
        print("\n" + "="*50)
        print("SELECT CHARACTER")
        print("="*50 + "\n")
        
        owned_characters = self.db_manager.get_player_characters(self.current_player['id'])
        
        characters_to_show = list(config.CHARACTERS.keys())
        
        for i, char_key in enumerate(characters_to_show, 1):
            char_info = config.CHARACTERS[char_key]
            owned = "✓" if char_key in owned_characters else "✗"
            print(f"{i}. [{owned}] {char_info['name']}")
            print(f"   {char_info['description']}\n")
        
        choice = input("Select character (number): ").strip()
        
        try:
            char_index = int(choice) - 1
            if 0 <= char_index < len(characters_to_show):
                selected_char = characters_to_show[char_index]
                self._start_game(selected_char)
        except ValueError:
            print("Invalid choice")
    
    def _start_game(self, character: str):
        """Start a game with selected mode and character."""
        print(f"\n[*] Starting {self.selected_mode.get_full_name()}...")
        print(f"[*] Character: {config.CHARACTERS[character]['name']}")
        
        # Launch game UI
        game_ui = GameUI(
            self.selected_mode,
            self.db_manager,
            self.current_player,
            character
        )
        game_ui.run()
        
        # Return to menu
        self.menu_state = "main"
    
    def _update(self):
        """Update menu state."""
        pass
    
    def _render(self):
        """Render main menu."""
        self.screen.fill((20, 20, 30))
        
        if self.menu_state == "main":
            self._render_main_menu()
        
        pygame.display.flip()
    
    def _render_main_menu(self):
        """Render main menu screen."""
        # Title
        title = self.font_large.render("BEDWARS 3D", True, (255, 100, 0))
        title_rect = title.get_rect(center=(config.WINDOW_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Menu options
        option1 = self.font_medium.render("1. Play Game", True, (200, 200, 200))
        option1_rect = option1.get_rect(center=(config.WINDOW_WIDTH // 2, 300))
        self.screen.blit(option1, option1_rect)
        
        option2 = self.font_medium.render("2. Exit", True, (200, 200, 200))
        option2_rect = option2.get_rect(center=(config.WINDOW_WIDTH // 2, 400))
        self.screen.blit(option2, option2_rect)
        
        # Version
        version = self.font_small.render(f"v{config.GAME_VERSION}", True, (100, 100, 100))
        version_rect = version.get_rect(bottomright=(config.WINDOW_WIDTH - 20, config.WINDOW_HEIGHT - 20))
        self.screen.blit(version, version_rect)
