#!/usr/bin/env python3
"""Development/testing utilities."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from auth.database import DatabaseManager
from shop.shop_manager import ShopManager
import config


def test_database():
    """Test database operations."""
    print("\n=== Testing Database ===")
    db = DatabaseManager("test.db")
    
    # Create account
    print("Creating test account...")
    success = db.create_account("TestPlayer", "password123", "test@example.com")
    print(f"Account creation: {'Success' if success else 'Failed'}")
    
    # Authenticate
    print("Authenticating...")
    player = db.authenticate_player("TestPlayer", "password123")
    if player:
        print(f"Authentication success: {dict(player)}")
    else:
        print("Authentication failed")
    
    # Test shop
    print("\n=== Testing Shop ===")
    shop = ShopManager(db)
    shop_data = shop.get_shop_data(1)
    if shop_data:
        print(f"Shop data: {shop_data}")


def test_game_modes():
    """Test game mode configurations."""
    print("\n=== Testing Game Modes ===")
    from game.game_modes import ClassicMode, LuckyblockMode
    
    classic = ClassicMode('squads')
    print(f"Classic mode: {classic.mode_name}")
    print(f"Teams: {classic.num_teams}, Team size: {classic.team_size}")
    print(f"Max players: {classic.max_players}")
    
    lucky = LuckyblockMode('5v5')
    print(f"\nLucky block mode: {lucky.mode_name}")
    print(f"Teams: {lucky.num_teams}, Team size: {lucky.team_size}")
    print(f"Lucky items: {len(lucky.LUCKY_ITEMS)} available")


def test_characters():
    """Test character system."""
    print("\n=== Testing Characters ===")
    from shop.characters import CharacterManager, CHARACTERS
    
    manager = CharacterManager()
    print(f"Available characters: {len(CHARACTERS)}")
    
    for name, character in list(CHARACTERS.items())[:3]:
        print(f"\n{character.name}:")
        print(f"  Cost: {character.cost} coins")
        print(f"  Perks: {len(character.perks)}")
        for perk in character.perks:
            print(f"    - {perk.name}: {perk.description}")


def test_entities():
    """Test entity system."""
    print("\n=== Testing Entities ===")
    from game.entities import Player, Bot, Item
    from game.math_utils import Vector3
    
    player = Player(1, "TestPlayer", 0, Vector3(0, 64, 0))
    print(f"Player: {player.username} (HP: {player.health})")
    
    bot = Bot(1001, "TestBot", 1, level=15, spawn_pos=Vector3(10, 64, 10))
    print(f"Bot: {bot.username} (Level: {bot.level}, Difficulty: {bot.difficulty['accuracy']})")
    
    item = Item("diamond_sword", Vector3(5, 65, 5))
    print(f"Item: {item.item_name} x{item.quantity}")
    
    # Test physics
    print("\nTesting physics...")
    player.velocity.y = -5
    player.apply_physics(0.1)
    print(f"After physics: Position={player.position}, Velocity={player.velocity}")


def test_ai():
    """Test AI systems."""
    print("\n=== Testing AI ===")
    from ai.bot_ai import BotBrain, AIState
    from ai.pathfinding import PathFinder
    from game.entities import Bot
    from game.math_utils import Vector3
    
    bot = Bot(1001, "TestBot", 1, level=20)
    brain = BotBrain(bot)
    print(f"Bot brain created: State={brain.state.value}")
    
    pathfinder = PathFinder(grid_size=1.0)
    start = Vector3(0, 0, 0)
    goal = Vector3(10, 0, 10)
    path = pathfinder.find_path(start, goal, max_iterations=100)
    print(f"Pathfinding: {len(path)} waypoints from {start} to {goal}")


def test_network_protocol():
    """Test network protocol."""
    print("\n=== Testing Network Protocol ===")
    from networking.protocol import NetworkMessage, MessageType, GameProtocol
    
    # Test message serialization
    msg = GameProtocol.create_player_move_message(
        1, 
        {'x': 0, 'y': 64, 'z': 0},
        {'yaw': 45, 'pitch': 0}
    )
    json_str = msg.to_json()
    print(f"Serialized: {json_str[:80]}...")
    
    # Test deserialization
    msg2 = NetworkMessage.from_json(json_str)
    print(f"Deserialized: Type={msg2.type.value}, Player={msg2.data['player_id']}")


def main():
    """Run all tests."""
    print("\n" + "="*50)
    print("Bedwars Game - Development Tests")
    print("="*50)
    
    try:
        test_database()
        test_game_modes()
        test_characters()
        test_entities()
        test_ai()
        test_network_protocol()
        
        print("\n" + "="*50)
        print("All tests completed!")
        print("="*50 + "\n")
    
    except Exception as e:
        print(f"\nTest error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
