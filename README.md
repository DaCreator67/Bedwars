# Bedwars 3D Game

A feature-rich 3D Bedwars game with multiplayer support, bot AI, progression system, and cosmetics.

## Features

### Game Modes
- **Classic Mode**
  - Solos
  - Doubles (2v2)
  - Squads (4v4)
  - 5v5
  - 1v1
  - 2v2

- **Luckyblock Mode**
  - Squads (4v4)
  - 5v5
  - Special blocks with random items and perks

### Core Features
- Player authentication (Login/Sign Up)
- Account persistence with SQLite
- Leveling system affecting bot difficulty
- Coin-based economy
- Character system with special perks
- Performance-based coin rewards
- Shop menu for cosmetics and characters
- Multiplayer and bot support
- 3D immersive gameplay

### Characters & Perks
- Vex: Curse Opponents, Reduce HP to 90, Apply Poison Damage
- Speedster: Move 15% Faster Throughout The Game
- Guardian: Take 10% Damage Reduction (stackable)
- Archer: Increase Bow Damage and Accuracy
- Tank: Have Extra Health (Regenerates)
- Phantom: Invisibility After Taking Damage For 2 Seconds (5 second cooldown)
- Berserker: Lower Health = Higher Damage Output
- Medic: Quickly Heal Nearby Teammates
- Ninja: Move Sneakily Throughout The Map Even While Crouched
- Gladiator: Reflect Damage Onto Enemies When Dealt Damage

## Installation

```bash
pip install -r requirements.txt
python main.py
```

## Project Structure

```
bedwars-game/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── config.py              # Game configuration
├── auth/
│   ├── __init__.py
│   ├── database.py        # Database setup and auth
│   └── encryption.py      # Password encryption
├── game/
│   ├── __init__.py
│   ├── game_manager.py    # Main game logic
│   ├── game_modes.py      # Game mode definitions
│   ├── map.py             # Game map and world
│   ├── entities.py        # Players, bots, items
│   ├── physics.py         # Physics system
│   ├── collision.py       # Collision detection
│   └── rendering.py       # 3D rendering
├── ai/
│   ├── __init__.py
│   ├── bot_ai.py          # Bot behavior
│   ├── pathfinding.py     # Pathfinding algorithms
│   └── combat_ai.py       # Combat logic
├── shop/
│   ├── __init__.py
│   ├── shop_manager.py    # Shop system
│   ├── characters.py      # Character definitions
│   └── cosmetics.py       # Cosmetic items
├── ui/
│   ├── __init__.py
│   ├── menu.py            # Main menu
│   ├── hud.py             # In-game HUD
│   ├── shop_ui.py         # Shop interface
│   └── screens.py         # Various UI screens
├── networking/
│   ├── __init__.py
│   ├── server.py          # Game server
│   ├── client.py          # Client networking
│   └── protocol.py        # Network protocol
└── assets/
    ├── models/            # 3D models
    ├── textures/          # Textures
    └── sounds/            # Audio files
```
