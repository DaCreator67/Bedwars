"""Main entry point for Bedwars 3D Game."""
import sys
import os
from ui.menu import MainMenu
from auth.database import DatabaseManager


def main():
    """Initialize and run the game."""
    print("=" * 50)
    print("Bedwars 3D Game - Starting...")
    print("=" * 50)
    
    # Initialize database
    print("\n[*] Initializing database...")
    db_manager = DatabaseManager()
    print("[✓] Database initialized")
    
    # Initialize and run main menu
    print("[*] Starting UI...")
    try:
        menu = MainMenu(db_manager)
        menu.run()
    except ImportError as e:
        print(f"\n[ERROR] Missing dependency: {e}")
        print("Make sure you've run: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
