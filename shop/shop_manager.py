"""Shop system for cosmetics and characters."""
from typing import Dict, List
from enum import Enum


class CosmeticType(Enum):
    """Cosmetic item types."""
    SKIN = "skin"
    EMOTE = "emote"
    PARTICLE = "particle"
    KILL_EFFECT = "kill_effect"


class Cosmetic:
    """Cosmetic item definition."""
    
    def __init__(self, name: str, cosmetic_type: CosmeticType, cost: int, description: str, rarity: str = "common"):
        self.name = name
        self.cosmetic_type = cosmetic_type
        self.cost = cost
        self.description = description
        self.rarity = rarity


class ShopManager:
    """Manage shop and purchases."""
    
    # Cosmetics catalog
    COSMETICS = {
        'fire_particles': Cosmetic('Fire Particles', CosmeticType.PARTICLE, 200, 'Flame particles around your player', 'uncommon'),
        'ice_particles': Cosmetic('Ice Particles', CosmeticType.PARTICLE, 200, 'Frost particles around your player', 'uncommon'),
        'lightning_particles': Cosmetic('Lightning Particles', CosmeticType.PARTICLE, 300, 'Electric particles effect', 'rare'),
        'blood_effect': Cosmetic('Blood Effect', CosmeticType.KILL_EFFECT, 250, 'Blood splash on kills', 'uncommon'),
        'explosion_effect': Cosmetic('Explosion Effect', CosmeticType.KILL_EFFECT, 350, 'Explosion on kills', 'rare'),
        'win_confetti': Cosmetic('Win Confetti', CosmeticType.KILL_EFFECT, 150, 'Confetti on victory', 'common'),
    }
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def get_cosmetic(self, cosmetic_name: str) -> Cosmetic:
        """Get cosmetic by name."""
        return self.COSMETICS.get(cosmetic_name)
    
    def get_all_cosmetics(self) -> Dict[str, Cosmetic]:
        """Get all available cosmetics."""
        return self.COSMETICS.copy()
    
    def purchase_cosmetic(self, player_id: int, cosmetic_name: str) -> bool:
        """Purchase a cosmetic item."""
        cosmetic = self.get_cosmetic(cosmetic_name)
        if not cosmetic:
            return False
        
        # Check if player already owns it
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM owned_cosmetics WHERE player_id = ? AND cosmetic_name = ?",
                (player_id, cosmetic_name)
            )
            if cursor.fetchone():
                conn.close()
                return False  # Already owned
            conn.close()
        except:
            return False
        
        # Attempt purchase
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Check coins
            cursor.execute("SELECT total_coins FROM players WHERE id = ?", (player_id,))
            player = cursor.fetchone()
            
            if not player or player['total_coins'] < cosmetic.cost:
                conn.close()
                return False
            
            # Deduct coins
            cursor.execute(
                "UPDATE players SET total_coins = total_coins - ? WHERE id = ?",
                (cosmetic.cost, player_id)
            )
            
            # Add cosmetic
            cursor.execute(
                "INSERT INTO owned_cosmetics (player_id, cosmetic_name) VALUES (?, ?)",
                (player_id, cosmetic_name)
            )
            
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def get_player_cosmetics(self, player_id: int) -> List[str]:
        """Get all cosmetics owned by player."""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT cosmetic_name FROM owned_cosmetics WHERE player_id = ?",
                (player_id,)
            )
            cosmetics = [row['cosmetic_name'] for row in cursor.fetchall()]
            conn.close()
            return cosmetics
        except:
            return []
    
    def get_shop_data(self, player_id: int) -> dict:
        """Get complete shop data for player."""
        player_data = self.db_manager.get_player(player_id)
        if not player_data:
            return None
        
        owned_cosmetics = self.get_player_cosmetics(player_id)
        owned_characters = self.db_manager.get_player_characters(player_id)
        
        # Import here to avoid circular imports
        from .characters import CHARACTERS
        
        cosmetic_data = []
        for name, cosmetic in self.COSMETICS.items():
            cosmetic_data.append({
                'name': name,
                'display_name': cosmetic.name,
                'cost': cosmetic.cost,
                'type': cosmetic.cosmetic_type.value,
                'description': cosmetic.description,
                'rarity': cosmetic.rarity,
                'owned': name in owned_cosmetics
            })
        
        character_data = []
        for name, character in CHARACTERS.items():
            character_data.append({
                'name': name,
                'display_name': character.name,
                'cost': character.cost,
                'description': character.description,
                'owned': name in owned_characters,
                'perks': [p.description for p in character.perks]
            })
        
        return {
            'username': player_data['username'],
            'level': player_data['level'],
            'coins': player_data['total_coins'],
            'cosmetics': cosmetic_data,
            'characters': character_data
        }
