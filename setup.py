"""Game setup and initialization utilities."""
import os
from pathlib import Path
from auth.database import DatabaseManager
import config


def setup_game():
    """Initialize game for first run."""
    print("\n" + "="*50)
    print("Bedwars 3D - Initial Setup")
    print("="*50 + "\n")
    
    # Create game directories
    dirs = ['assets/models', 'assets/textures', 'assets/sounds', 'saves', 'logs']
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {dir_path}")
    
    # Initialize database
    print("\nInitializing database...")
    db = DatabaseManager(config.DB_PATH)
    print(f"✓ Database created: {config.DB_PATH}")
    
    # Create demo account
    print("\nCreating demo account...")
    if db.create_account("demo", "demo123", "demo@bedwars.local"):
        print("✓ Demo account created")
        print("  Username: demo")
        print("  Password: demo123")
    else:
        print("✓ Demo account already exists")
    
    # Add starting coins to demo
    demo_player = db.authenticate_player("demo", "demo123")
    if demo_player:
        player_id = demo_player['id']
        db.update_player_coins(player_id, 5000)  # Start with 5000 coins
        print("✓ Demo account funded with 5000 coins")
    
    print("\n" + "="*50)
    print("Setup Complete!")
    print("="*50)
    print("\nYou can now run the game:")
    print("  python run.py")
    print("\nOr start a multiplayer server:")
    print("  python run_server.py")
    print()


def verify_installation():
    """Verify all dependencies are installed."""
    print("\nVerifying installation...\n")
    
    dependencies = [
        ('pygame', 'pygame'),
        ('OpenGL', 'PyOpenGL'),
        ('OpenGL.GL', 'PyOpenGL'),
        ('numpy', 'numpy'),
    ]
    
    all_ok = True
    for module_name, package_name in dependencies:
        try:
            __import__(module_name)
            print(f"✓ {package_name}")
        except ImportError:
            print(f"✗ {package_name} - NOT INSTALLED")
            all_ok = False
    
    if not all_ok:
        print("\nPlease install missing dependencies:")
        print("  pip install -r requirements.txt")
        return False
    
    print("\n✓ All dependencies installed!\n")
    return True


if __name__ == "__main__":
    if verify_installation():
        setup_game()
