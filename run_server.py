#!/usr/bin/env python3
"""Multiplayer server launcher."""
import sys
from pathlib import Path
import time
import signal

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    try:
        from networking.server import GameServer
        import config
        
        server = GameServer(config.DEFAULT_HOST, config.DEFAULT_PORT)
        server.start()
        
        print(f"\nBedwars Server started")
        print(f"Address: {config.DEFAULT_HOST}:{config.DEFAULT_PORT}")
        print(f"Max players: {config.MAX_PLAYERS}")
        print("\nPress Ctrl+C to stop...\n")
        
        def signal_handler(sig, frame):
            print("\nShutting down...")
            server.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        # Keep server running
        while True:
            time.sleep(1)
    
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Server error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
