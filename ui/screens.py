"""Authentication screens (login/signup)."""
import pygame
from enum import Enum
from typing import Optional, Tuple
from .menu import Button, TextInput


class AuthMode(Enum):
    """Auth screen modes."""
    LOGIN = "login"
    SIGNUP = "signup"


class AuthScreen:
    """Authentication screen for login/signup."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.mode = AuthMode.LOGIN
        self.error_message = ""
        self.error_timer = 0.0
        
        self.font_title = pygame.font.Font(None, 64)
        self.font_normal = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Input fields
        self.username_input = TextInput(width // 2 - 150, height // 2 - 50, 300, 40, "Username")
        self.password_input = TextInput(width // 2 - 150, height // 2 + 20, 300, 40, "Password")
        self.email_input = TextInput(width // 2 - 150, height // 2 + 90, 300, 40, "Email (Signup only)")
        
        # Buttons
        self.auth_button = Button(width // 2 - 100, height // 2 + 150, 200, 50, "LOGIN")
        self.toggle_button = Button(width // 2 - 100, height // 2 + 220, 200, 50, "Go to Signup")
        self.back_button = Button(50, height - 70, 150, 50, "BACK")
    
    def set_mode(self, mode: AuthMode):
        """Set auth mode."""
        self.mode = mode
        self.auth_button.text = "LOGIN" if mode == AuthMode.LOGIN else "SIGNUP"
        self.toggle_button.text = "Go to Signup" if mode == AuthMode.LOGIN else "Go to Login"
        self.email_input.active = False
        self.error_message = ""
    
    def update(self, mouse_pos: tuple, mouse_pressed: bool, events: list):
        """Update screen."""
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                self.username_input.update(mouse_pos, mouse_pressed, event)
                self.password_input.update(mouse_pos, mouse_pressed, event)
                if self.mode == AuthMode.SIGNUP:
                    self.email_input.update(mouse_pos, mouse_pressed, event)
        
        self.auth_button.update(mouse_pos, mouse_pressed)
        self.toggle_button.update(mouse_pos, mouse_pressed)
        self.back_button.update(mouse_pos, mouse_pressed)
        
        # Update error timer
        if self.error_timer > 0:
            self.error_timer -= 0.016  # Assuming 60 FPS
        else:
            self.error_message = ""
    
    def draw(self, surface: pygame.Surface):
        """Draw screen."""
        surface.fill((20, 20, 40))
        
        # Draw title
        title_text = "LOGIN" if self.mode == AuthMode.LOGIN else "SIGN UP"
        title = self.font_title.render(title_text, True, (100, 255, 150))
        title_rect = title.get_rect(center=(self.width // 2, 50))
        surface.blit(title, title_rect)
        
        # Draw inputs
        self.username_input.draw(surface, self.font_normal)
        self.password_input.draw(surface, self.font_normal)
        
        if self.mode == AuthMode.SIGNUP:
            self.email_input.draw(surface, self.font_normal)
        
        # Draw buttons
        self.auth_button.draw(surface, self.font_normal)
        self.toggle_button.draw(surface, self.font_small)
        self.back_button.draw(surface, self.font_small)
        
        # Draw error message
        if self.error_message:
            error_text = self.font_small.render(self.error_message, True, (255, 100, 100))
            error_rect = error_text.get_rect(center=(self.width // 2, height - 150))
            surface.blit(error_text, error_rect)
    
    def get_action(self) -> Optional[dict]:
        """Get auth action."""
        if self.auth_button.clicked:
            self.auth_button.clicked = False
            return {
                'action': 'authenticate',
                'mode': self.mode.value,
                'username': self.username_input.get_value(),
                'password': self.password_input.get_value(),
                'email': self.email_input.get_value() if self.mode == AuthMode.SIGNUP else None
            }
        
        if self.toggle_button.clicked:
            self.toggle_button.clicked = False
            new_mode = AuthMode.SIGNUP if self.mode == AuthMode.LOGIN else AuthMode.LOGIN
            self.set_mode(new_mode)
            return {'action': 'mode_change'}
        
        if self.back_button.clicked:
            self.back_button.clicked = False
            return {'action': 'back'}
        
        return None
    
    def show_error(self, message: str):
        """Show error message."""
        self.error_message = message
        self.error_timer = 3.0


class GameModeSelector:
    """Game mode selection screen."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.font_title = pygame.font.Font(None, 64)
        self.font_normal = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Classic mode buttons
        self.solos_button = Button(100, 150, 200, 60, "SOLOS")
        self.doubles_button = Button(350, 150, 200, 60, "DOUBLES")
        self.squads_button = Button(600, 150, 200, 60, "SQUADS")
        self.fivev5_button = Button(850, 150, 200, 60, "5v5")
        self.onev1_button = Button(225, 250, 200, 60, "1v1")
        self.twov2_button = Button(525, 250, 200, 60, "2v2")
        
        # Luckyblock mode buttons
        self.lucky_squads_button = Button(350, 400, 200, 60, "LUCKY SQUADS")
        self.lucky_fivev5_button = Button(650, 400, 200, 60, "LUCKY 5v5")
        
        # Bot option
        self.bot_checkbox = False
        self.bot_button = Button(width // 2 - 75, height - 100, 150, 40, "BOT MODE")
        self.back_button = Button(50, height - 70, 150, 50, "BACK")
    
    def update(self, mouse_pos: tuple, mouse_pressed: bool):
        """Update selector."""
        buttons = [self.solos_button, self.doubles_button, self.squads_button, self.fivev5_button,
                  self.onev1_button, self.twov2_button, self.lucky_squads_button, self.lucky_fivev5_button,
                  self.bot_button, self.back_button]
        
        for button in buttons:
            button.update(mouse_pos, mouse_pressed)
    
    def draw(self, surface: pygame.Surface):
        """Draw selector."""
        surface.fill((20, 20, 40))
        
        # Draw titles
        title = self.font_title.render("SELECT GAME MODE", True, (100, 255, 150))
        title_rect = title.get_rect(center=(self.width // 2, 20))
        surface.blit(title, title_rect)
        
        classic_label = self.font_normal.render("CLASSIC", True, (255, 200, 100))
        surface.blit(classic_label, (self.width // 2 - 50, 100))
        
        lucky_label = self.font_normal.render("LUCKY BLOCK", True, (255, 200, 100))
        surface.blit(lucky_label, (self.width // 2 - 100, 350))
        
        # Draw buttons
        self.solos_button.draw(surface, self.font_small)
        self.doubles_button.draw(surface, self.font_small)
        self.squads_button.draw(surface, self.font_small)
        self.fivev5_button.draw(surface, self.font_small)
        self.onev1_button.draw(surface, self.font_small)
        self.twov2_button.draw(surface, self.font_small)
        self.lucky_squads_button.draw(surface, self.font_small)
        self.lucky_fivev5_button.draw(surface, self.font_small)
        
        # Draw bot toggle
        bot_text = "BOT MODE: ON" if self.bot_checkbox else "BOT MODE: OFF"
        self.bot_button.text = bot_text
        self.bot_button.draw(surface, self.font_small)
        
        self.back_button.draw(surface, self.font_small)
    
    def get_action(self) -> Optional[dict]:
        """Get selected mode."""
        modes = {
            'solos': (self.solos_button, 'classic', 'solos'),
            'doubles': (self.doubles_button, 'classic', 'doubles'),
            'squads': (self.squads_button, 'classic', 'squads'),
            '5v5': (self.fivev5_button, 'classic', '5v5'),
            '1v1': (self.onev1_button, 'classic', '1v1'),
            '2v2': (self.twov2_button, 'classic', '2v2'),
            'lucky_squads': (self.lucky_squads_button, 'luckyblock', 'squads'),
            'lucky_5v5': (self.lucky_fivev5_button, 'luckyblock', '5v5'),
        }
        
        for name, (button, category, mode) in modes.items():
            if button.clicked:
                button.clicked = False
                return {
                    'action': 'start_game',
                    'game_mode_category': category,
                    'game_mode': mode,
                    'bot_mode': self.bot_checkbox
                }
        
        if self.bot_button.clicked:
            self.bot_button.clicked = False
            self.bot_checkbox = not self.bot_checkbox
            return {'action': 'toggle_bot'}
        
        if self.back_button.clicked:
            self.back_button.clicked = False
            return {'action': 'back'}
        
        return None
