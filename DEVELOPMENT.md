"""Development and deployment documentation."""

# Bedwars 3D Game - Development Guide

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python tests.py

# Start the game
python main.py

# Start multiplayer server (optional)
python -c "from networking.server import GameServer; s = GameServer(); s.start(); import time; time.sleep(3600)"
```

## Project Architecture

### Core Systems

1. **Authentication** (`auth/`)
   - Password encryption using PBKDF2
   - SQLite database for player accounts
   - Account persistence

2. **Game Logic** (`game/`)
   - Entity system (Player, Bot, Item, Projectile)
   - Physics engine with gravity and collision
   - Game modes (Classic and Luckyblock)
   - Game manager for state management

3. **AI System** (`ai/`)
   - Bot AI with multiple difficulty levels
   - Pathfinding using A* algorithm
   - Combat decision making
   - State-based behavior

4. **Shop System** (`shop/`)
   - Character purchasing and management
   - Cosmetic items
   - Coin economy
   - Performance-based rewards

5. **UI** (`ui/`)
   - Login/Signup screens
   - Main menu
   - Game mode selector
   - In-game HUD
   - Shop interface

6. **Networking** (`networking/`)
   - Server for multiplayer
   - Client for connecting
   - Protocol definition
   - Message handling

7. **Rendering** (`game/rendering.py` and `main.py`)
   - OpenGL 3D rendering
   - Camera system
   - Lighting
   - Entity rendering

## Game Features

### Characters
- **Vex**: Curse opponents (90 HP, poison damage)
- **Speedster**: 15% faster movement
- **Guardian**: 10% damage reduction
- **Archer**: 20% bow damage boost
- **Tank**: 120 max HP
- **Phantom**: 2s invisibility on damage
- **Berserker**: 50% more damage when low health
- **Medic**: Heal teammates
- **Ninja**: Faster crouch movement
- **Gladiator**: 15% damage reflection

All cost 1000 coins.

### Game Modes

**Classic:**
- Solos (16 players, 1v1v1...)
- Doubles (8 players, 2v2v2v2)
- Squads (16 players, 4v4v4v4)
- 5v5 (10 players)
- 1v1 (2 players)
- 2v2 (4 players)

**Luckyblock:**
- Squads (16 players)
- 5v5 (10 players)

Win conditions vary by mode.

### Economy
- Base reward: 50 coins
- Kill bonus: +100 coins
- Bed destruction: +200 coins
- Victory bonus: +500 coins
- Good game average: ~50 coins
- Characters: 1000 coins each

## Configuration

Edit `config.py` to adjust:
- Window size and FPS
- Player stats (speed, health, reach)
- Combat settings (damage, cooldowns)
- AI difficulty scaling
- Network settings

## Multiplayer

To run with multiplayer:

1. Start server on one machine
2. Connect clients to server IP:port
3. Game state synchronizes across network
4. Players can play together

## Extending the Game

### Adding New Characters

```python
# In shop/characters.py
new_character = Character(
    name='NewChar',
    cost=1000,
    description='Description',
    perks=[
        Perk('perk_name', PerkType.PASSIVE, 'Description', effect_function)
    ]
)
CHARACTERS['new_char'] = new_character
```

### Adding New Game Modes

```python
# In game/game_modes.py
class NewMode(GameMode):
    def __init__(self):
        super().__init__(
            mode_name='new_mode',
            game_mode_type=GameModeType.CLASSIC,
            team_size=4,
            max_players=16,
            num_teams=4
        )
```

### Adding New Items

```python
# In game/entities.py
class Item(Entity):
    # Add item type handling in pickup logic
    def on_pickup(self, player):
        # Custom logic here
        pass
```

## Performance Tips

1. **Reduce bot count** - Each bot needs AI updates
2. **Lower graphics quality** - Reduce vertex count in meshes
3. **Disable networking** - Single-player is faster
4. **Adjust FPS** - Lower FPS in config.py
5. **Clear unused entities** - Remove despawned items

## Troubleshooting

**Game won't start:**
- Check OpenGL support
- Verify Pygame installation
- Ensure Python 3.8+

**Performance issues:**
- Reduce MAX_PLAYERS in config
- Lower BOT_SPAWN_DELAY
- Disable bot pathfinding

**Database errors:**
- Delete game.db to reset
- Check file permissions
- Verify SQLite is installed

**Network issues:**
- Check firewall settings
- Verify server IP/port
- Check network connection

## Future Enhancements

- [ ] Advanced graphics (textures, shaders)
- [ ] More characters and cosmetics
- [ ] Ranked matchmaking
- [ ] Clan system
- [ ] Custom maps
- [ ] Replays and spectating
- [ ] Voice chat
- [ ] Mobile app
- [ ] Trading system
- [ ] Battle pass

## License

This game is provided as-is for educational purposes.
