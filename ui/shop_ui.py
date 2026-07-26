"""Shop UI for purchasing items and characters."""
import pygame
from typing import Optional
from .menu import Button


class ShopUI:
    """Shop interface for cosmetics and characters."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.font_title = pygame.font.Font(None, 64)
        self.font_large = pygame.font.Font(None, 48)
        self.font_normal = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        self.current_tab = "characters"  # characters or cosmetics
        self.scroll_offset = 0
        self.selected_item = None
        
        # Buttons
        self.characters_tab = Button(50, 100, 200, 50, "CHARACTERS")
        self.cosmetics_tab = Button(300, 100, 200, 50, "COSMETICS")
        self.back_button = Button(self.width - 150, 20, 100, 40, "BACK")
        
        self.purchase_button = Button(self.width - 200, self.height - 100, 150, 50, "BUY")
    
    def update(self, mouse_pos: tuple, mouse_pressed: bool, scroll_direction: int = 0):
        """Update shop UI."""
        self.characters_tab.update(mouse_pos, mouse_pressed)
        self.cosmetics_tab.update(mouse_pos, mouse_pressed)
        self.back_button.update(mouse_pos, mouse_pressed)
        self.purchase_button.update(mouse_pos, mouse_pressed)
        
        # Handle scrolling
        self.scroll_offset = max(0, self.scroll_offset + scroll_direction * 50)
    
    def draw(self, surface: pygame.Surface, shop_data: dict):
        """Draw shop UI."""
        surface.fill((20, 20, 40))
        
        # Draw title
        title = self.font_title.render("SHOP", True, (100, 255, 150))
        title_rect = title.get_rect(center=(self.width // 2, 30))
        surface.blit(title, title_rect)
        
        # Draw player info
        player_text = self.font_normal.render(f"Level {shop_data.get('level', 1)} | Coins: {shop_data.get('coins', 0)}", 
                                             True, (255, 255, 100))
        surface.blit(player_text, (50, 20))
        
        # Draw tabs
        self.characters_tab.draw(surface, self.font_normal)
        self.cosmetics_tab.draw(surface, self.font_normal)
        
        # Handle tab switching
        if self.characters_tab.clicked:
            self.characters_tab.clicked = False
            self.current_tab = "characters"
            self.scroll_offset = 0
        
        if self.cosmetics_tab.clicked:
            self.cosmetics_tab.clicked = False
            self.current_tab = "cosmetics"
            self.scroll_offset = 0
        
        # Draw items based on current tab
        if self.current_tab == "characters":
            self._draw_characters(surface, shop_data.get('characters', []))
        else:
            self._draw_cosmetics(surface, shop_data.get('cosmetics', []))
        
        self.back_button.draw(surface, self.font_small)
        self.purchase_button.draw(surface, self.font_small)
    
    def _draw_characters(self, surface: pygame.Surface, characters: list):
        """Draw character items."""
        item_y = 200
        item_height = 120
        
        for i, character in enumerate(characters):
            if i * item_height < self.scroll_offset:
                continue
            
            if item_y > self.height - 150:
                break
            
            self._draw_character_item(surface, character, 50, item_y)
            item_y += item_height
    
    def _draw_character_item(self, surface: pygame.Surface, character: dict, x: int, y: int):
        """Draw single character item."""
        item_rect = pygame.Rect(x, y, self.width - 100, 100)
        
        # Background
        color = (100, 150, 200) if character.get('owned') else (70, 100, 150)
        pygame.draw.rect(surface, color, item_rect)
        pygame.draw.rect(surface, (200, 200, 200), item_rect, 2)
        
        # Name
        name_text = self.font_normal.render(character['display_name'], True, (255, 255, 255))
        surface.blit(name_text, (x + 20, y + 10))
        
        # Description
        desc_text = self.font_small.render(character['description'], True, (200, 200, 200))
        surface.blit(desc_text, (x + 20, y + 45))
        
        # Cost or "Owned" badge
        if character.get('owned'):
            badge_text = self.font_small.render("✓ OWNED", True, (100, 255, 100))
        else:
            badge_text = self.font_small.render(f"{character['cost']} coins", True, (255, 255, 100))
        
        badge_rect = badge_text.get_rect()
        badge_rect.topright = (item_rect.right - 20, item_rect.top + 10)
        surface.blit(badge_text, badge_rect)
    
    def _draw_cosmetics(self, surface: pygame.Surface, cosmetics: list):
        """Draw cosmetic items."""
        cols = 3
        item_width = (self.width - 100) // cols
        item_height = 150
        
        item_index = 0
        for i, cosmetic in enumerate(cosmetics):
            col = i % cols
            row = i // cols
            
            if row * item_height < self.scroll_offset:
                continue
            
            y = 200 + row * item_height - self.scroll_offset
            if y > self.height - 150:
                break
            
            x = 50 + col * (item_width + 20)
            self._draw_cosmetic_item(surface, cosmetic, x, y, item_width)
    
    def _draw_cosmetic_item(self, surface: pygame.Surface, cosmetic: dict, x: int, y: int, width: int):
        """Draw single cosmetic item."""
        item_rect = pygame.Rect(x, y, width, 120)
        
        # Background with rarity color
        rarity_colors = {
            'common': (100, 100, 100),
            'uncommon': (100, 200, 100),
            'rare': (100, 150, 255),
            'legendary': (255, 215, 0),
        }
        color = rarity_colors.get(cosmetic.get('rarity'), (100, 100, 100))
        
        pygame.draw.rect(surface, color, item_rect)
        pygame.draw.rect(surface, (200, 200, 200), item_rect, 2)
        
        # Name
        name_text = self.font_small.render(cosmetic['display_name'], True, (255, 255, 255))
        surface.blit(name_text, (x + 10, y + 10))
        
        # Type
        type_text = self.font_tiny.render(cosmetic['type'], True, (200, 200, 200))
        surface.blit(type_text, (x + 10, y + 35))
        
        # Cost or owned
        if cosmetic.get('owned'):
            badge_text = self.font_small.render("✓", True, (100, 255, 100))
        else:
            badge_text = self.font_small.render(f"{cosmetic['cost']}", True, (255, 255, 100))
        
        badge_rect = badge_text.get_rect()
        badge_rect.bottomright = (item_rect.right - 5, item_rect.bottom - 5)
        surface.blit(badge_text, badge_rect)
    
    def get_action(self) -> Optional[dict]:
        """Get shop action."""
        if self.back_button.clicked:
            self.back_button.clicked = False
            return {'action': 'back'}
        
        if self.purchase_button.clicked:
            self.purchase_button.clicked = False
            if self.selected_item:
                return {'action': 'purchase', 'item': self.selected_item}
        
        return None
    
    @staticmethod
    def _get_team_color(team_id: int) -> tuple:
        """Get color for team."""
        colors = [(255, 100, 100), (100, 150, 255), (100, 255, 100), (255, 255, 100)]
        return colors[team_id % len(colors)]
