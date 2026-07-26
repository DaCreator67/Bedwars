"""Character definitions and perks system."""
from typing import Dict, List, Callable
from enum import Enum


class PerkType(Enum):
    """Types of character perks."""
    PASSIVE = "passive"
    ACTIVE = "active"
    ON_HIT = "on_hit"
    ON_DAMAGE = "on_damage"


class Perk:
    """Character perk definition."""
    
    def __init__(self, name: str, perk_type: PerkType, description: str, effect_func: Callable = None):
        self.name = name
        self.perk_type = perk_type
        self.description = description
        self.effect_func = effect_func
    
    def apply_effect(self, player, target=None, **kwargs):
        """Apply perk effect."""
        if self.effect_func:
            return self.effect_func(player, target, **kwargs)
        return None


class Character:
    """Character class with unique perks."""
    
    def __init__(self, name: str, cost: int, description: str, perks: List[Perk]):
        self.name = name
        self.cost = cost
        self.description = description
        self.perks = perks
        self.perk_map = {p.name: p for p in perks}
    
    def get_perk(self, perk_name: str) -> Perk:
        """Get perk by name."""
        return self.perk_map.get(perk_name)
    
    def get_passive_perks(self) -> List[Perk]:
        """Get all passive perks."""
        return [p for p in self.perks if p.perk_type == PerkType.PASSIVE]
    
    def get_active_perks(self) -> List[Perk]:
        """Get all active perks."""
        return [p for p in self.perks if p.perk_type == PerkType.ACTIVE]


# Perk effect functions
def vex_curse_effect(player, target, **kwargs):
    """Vex curse passive: reduce target's max HP and apply poison."""
    if target:
        target.max_health = 90
        if target.health > 90:
            target.health = 90
        target.poison_damage = 0.5  # Damage per second
    return True


def speedster_boost(player, target=None, **kwargs):
    """Speedster passive: increase movement speed."""
    player.speed_multiplier = 1.15  # 15% faster
    return True


def guardian_shield(player, target=None, **kwargs):
    """Guardian passive: reduce damage taken."""
    player.damage_reduction = 0.1  # 10% damage reduction
    return True


def archer_precision(player, target=None, **kwargs):
    """Archer passive: increased bow accuracy and damage."""
    player.bow_accuracy = 0.95
    player.bow_damage_multiplier = 1.2  # 20% more bow damage
    return True


def tank_fortitude(player, target=None, **kwargs):
    """Tank passive: increased max health."""
    player.max_health = 120
    player.health = 120
    return True


def phantom_invisibility(player, target=None, **kwargs):
    """Phantom passive: brief invisibility after taking damage."""
    player.invisibility_cooldown = 5.0
    player.invisibility_duration = 2.0
    return True


def berserker_rage(player, target=None, **kwargs):
    """Berserker passive: higher damage when low on health."""
    player.rage_threshold = 0.3  # Active when below 30% health
    player.rage_damage_multiplier = 1.5
    return True


def medic_support(player, target=None, **kwargs):
    """Medic passive: can heal teammates nearby."""
    player.healing_range = 10.0
    player.healing_per_second = 2.0
    return True


def ninja_stealth(player, target=None, **kwargs):
    """Ninja passive: reduced footstep sounds and faster crouch movement."""
    player.crouch_speed_multiplier = 1.3
    player.stealth_mode = True
    return True


def gladiator_riposte(player, target=None, **kwargs):
    """Gladiator passive: reflect small amount of damage."""
    player.damage_reflection = 0.15  # 15% of damage taken
    return True


# Character definitions
CHARACTERS = {
    'vex': Character(
        name='Vex',
        cost=1000,
        description='Curse opponents - reduce their max HP to 90 and apply poison damage on melee hits',
        perks=[
            Perk('curse', PerkType.PASSIVE, 'Passive: Cursed opponents take 90 max HP', vex_curse_effect),
            Perk('poison', PerkType.ON_HIT, 'On Hit: Apply poison damage', None)
        ]
    ),
    'speedster': Character(
        name='Speedster',
        cost=1000,
        description='Move 15% faster than other players - perfect for hit and run tactics',
        perks=[
            Perk('speed_boost', PerkType.PASSIVE, 'Passive: 15% increased movement speed', speedster_boost)
        ]
    ),
    'guardian': Character(
        name='Guardian',
        cost=1000,
        description='Reduce all incoming damage by 10% - excellent defender',
        perks=[
            Perk('shield', PerkType.PASSIVE, 'Passive: 10% damage reduction', guardian_shield)
        ]
    ),
    'archer': Character(
        name='Archer',
        cost=1000,
        description='Master of the bow - 20% increased bow damage and improved accuracy',
        perks=[
            Perk('precision', PerkType.PASSIVE, 'Passive: Increased bow accuracy', archer_precision)
        ]
    ),
    'tank': Character(
        name='Tank',
        cost=1000,
        description='Bulky fighter with 120 max health instead of 100',
        perks=[
            Perk('fortitude', PerkType.PASSIVE, 'Passive: 120 max health', tank_fortitude)
        ]
    ),
    'phantom': Character(
        name='Phantom',
        cost=1000,
        description='Become invisible for 2 seconds after taking damage (5 second cooldown)',
        perks=[
            Perk('invisibility', PerkType.ON_DAMAGE, 'On Damage: Brief invisibility', phantom_invisibility)
        ]
    ),
    'berserker': Character(
        name='Berserker',
        cost=1000,
        description='Gain 50% more damage when below 30% health',
        perks=[
            Perk('rage', PerkType.PASSIVE, 'Passive: Damage boost when low on health', berserker_rage)
        ]
    ),
    'medic': Character(
        name='Medic',
        cost=1000,
        description='Heal all teammates within 10 blocks by 2 HP per second',
        perks=[
            Perk('support', PerkType.PASSIVE, 'Passive: Heal nearby teammates', medic_support)
        ]
    ),
    'ninja': Character(
        name='Ninja',
        cost=1000,
        description='Move faster while crouching and make less noise',
        perks=[
            Perk('stealth', PerkType.PASSIVE, 'Passive: Silent movement and faster crouch', ninja_stealth)
        ]
    ),
    'gladiator': Character(
        name='Gladiator',
        cost=1000,
        description='Reflect 15% of damage taken back to attackers',
        perks=[
            Perk('riposte', PerkType.PASSIVE, 'Passive: Damage reflection', gladiator_riposte)
        ]
    ),
}


class CharacterManager:
    """Manage character selection and application."""
    
    def __init__(self):
        self.characters = CHARACTERS
    
    def get_character(self, character_name: str) -> Character:
        """Get character by name."""
        return self.characters.get(character_name.lower())
    
    def get_all_characters(self) -> Dict[str, Character]:
        """Get all available characters."""
        return self.characters.copy()
    
    def apply_character_to_player(self, player, character_name: str) -> bool:
        """Apply character effects to player."""
        character = self.get_character(character_name)
        if not character:
            return False
        
        player.character = character_name
        
        # Apply all passive perks
        for perk in character.get_passive_perks():
            perk.apply_effect(player)
        
        return True
    
    def apply_perk_effect(self, player, character_name: str, perk_name: str, target=None, **kwargs) -> bool:
        """Apply specific perk effect."""
        character = self.get_character(character_name)
        if not character:
            return False
        
        perk = character.get_perk(perk_name)
        if not perk:
            return False
        
        perk.apply_effect(player, target, **kwargs)
        return True
