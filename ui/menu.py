"""Main menu and navigation UI."""
import pygame
from enum import Enum
from typing import Callable, Optional


class MenuState(Enum):
    """Menu states."""
    MAIN_MENU = "main_menu"
    AUTH_MENU = "auth_menu"
    GAME_MODE_SELECT = "game_mode_select"
    PLAYING = "playing"
    SHOP = "shop"


class Button:
    """UI Button."""
    
    def __init__(self, x: float, y: float, width: float, height: float, text: str, callback: Callable = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.hovered = False
        self.clicked = False
    
    def update(self, mouse_pos: tuple, mouse_pressed: bool):
        """Update button state."""
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.hovered and mouse_pressed:
            self.clicked = True
        else:
            self.clicked = False
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        """Draw button."""
        color = (100, 200, 255) if self.hovered else (70, 140, 200)
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)
        
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def handle_click(self):
        """Handle button click."""
        if self.clicked and self.callback:
            self.callback()


class TextInput:
    """Text input field."""
    
    def __init__(self, x: float, y: float, width: float, height: float, placeholder: str = ""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.max_length = 32
    
    def update(self, mouse_pos: tuple, mouse_pressed: bool, event: Optional[pygame.event.Event] = None):
        """Update text input state."""
        if mouse_pressed:
            self.active = self.rect.collidepoint(mouse_pos)
        
        if self.active and event:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key == pygame.K_RETURN:
                    self.active = False
                elif len(self.text) < self.max_length and event.unicode.isprintable():
                    self.text += event.unicode
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        """Draw text input."""
        color = (100, 200, 255) if self.active else (70, 140, 200)
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)
        
        display_text = self.text if self.text else self.placeholder
        text_surface = font.render(display_text, True, (200, 200, 200) if not self.text else (255, 255, 255))
        text_rect = text_surface.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        surface.blit(text_surface, text_rect)
    
    def get_value(self) -> str:
        """Get input value."""
        return self.text.strip()
    
    def clear(self):
        """Clear input."""
        self.text = ""


class MainMenu:
    """Main menu interface."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.state = MenuState.MAIN_MENU
        self.font_title = pygame.font.Font(None, 72)
        self.font_large = pygame.font.Font(None, 48)
        self.font_normal = pygame.font.Font(None, 32)
        
        # Main menu buttons
        self.play_button = Button(width // 2 - 100, height // 2 - 50, 200, 50, "PLAY")
        self.shop_button = Button(width // 2 - 100, height // 2 + 20, 200, 50, "SHOP")
        self.settings_button = Button(width // 2 - 100, height // 2 + 90, 200, 50, "SETTINGS")
        self.quit_button = Button(width // 2 - 100, height // 2 + 160, 200, 50, "QUIT")
    
    def update(self, mouse_pos: tuple, mouse_pressed: bool, events: list):
        """Update menu."""
        self.play_button.update(mouse_pos, mouse_pressed)
        self.shop_button.update(mouse_pos, mouse_pressed)
        self.settings_button.update(mouse_pos, mouse_pressed)
        self.quit_button.update(mouse_pos, mouse_pressed)
    
    def draw(self, surface: pygame.Surface):
        """Draw menu."""
        surface.fill((20, 20, 40))
        
        # Draw title
        title = self.font_title.render("BEDWARS", True, (100, 255, 150))
        title_rect = title.get_rect(center=(self.width // 2, 100))
        surface.blit(title, title_rect)
        
        # Draw version
        version = self.font_normal.render("v1.0.0", True, (150, 150, 150))
        version_rect = version.get_rect(center=(self.width // 2, 180))
        surface.blit(version, version_rect)
        
        # Draw buttons
        self.play_button.draw(surface, self.font_normal)
        self.shop_button.draw(surface, self.font_normal)
        self.settings_button.draw(surface, self.font_normal)
        self.quit_button.draw(surface, self.font_normal)
    
    def get_action(self) -> Optional[str]:
        """Get menu action."""
        if self.play_button.clicked:
            self.play_button.clicked = False
            return "play"
        elif self.shop_button.clicked:
            self.shop_button.clicked = False
            return "shop"
        elif self.settings_button.clicked:
            self.settings_button.clicked = False
            return "settings"
        elif self.quit_button.clicked:
            self.quit_button.clicked = False
            return "quit"
        return None
