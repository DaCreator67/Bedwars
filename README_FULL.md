# Bedwars 3D Game

**A feature-rich 3D Bedwars game with multiplayer support, advanced AI, progression system, and cosmetics.**

## 🎮 Features

### Game Modes
- **Classic**: Solos, Doubles, Squads, 5v5, 1v1, 2v2
- **Luckyblock**: Special blocks with random items - Squads and 5v5

### Core Features
✅ **Player Accounts** - Login/Sign up with encrypted passwords
✅ **Leveling System** - Level up to increase bot difficulty
✅ **Coin Economy** - Earn coins through performance (not wins)
✅ **Character Classes** - 10+ unique characters with special perks
✅ **Shop System** - Buy characters and cosmetics
✅ **Bot AI** - Intelligent bots that scale with player level
✅ **3D Graphics** - Immersive OpenGL rendering
✅ **Multiplayer** - Networked gameplay with server
✅ **Statistics** - Track wins, kills, stats
✅ **Cosmetics** - Skins, effects, and customization

### Characters (1000 coins each)
- **Vex** - Curse opponents (90 HP, poison damage)
- **Speedster** - 15% faster movement
- **Guardian** - 10% damage reduction
- **Archer** - 20% bow damage boost
- **Tank** - 120 max HP
- **Phantom** - Invisibility on damage
- **Berserker** - 50% damage boost when low health
- **Medic** - Heal teammates
- **Ninja** - Silent fast movement
- **Gladiator** - Damage reflection

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/DaCreator67/Sell.git
cd Sell
git checkout bedwars-game

# Install dependencies
pip install -r requirements.txt

# Run setup (creates database, demo account)
python setup.py
```

### Play the Game

```bash
# Start the game
python run.py

# Demo credentials:
# Username: demo
# Password: demo123
```

### Multiplayer (Optional)

```bash
# Terminal 1: Start server
python run_server.py

# Terminal 2+: Start clients
python run.py
```

## 📋 How to Play

1. **Login/Create Account** - Start with authentication screen
2. **Select Game Mode** - Choose from Classic or Luckyblock
3. **Pick Character** - Select your character or play without
4. **Enter Battle** - Fight enemy teams to be last standing
5. **Earn Coins** - Get coins based on performance
6. **Visit Shop** - Buy characters and cosmetics

### Controls
- **WASD** - Move
- **Space** - Jump
- **Shift** - Sprint
- **Mouse** - Look around
- **Left Click** - Melee attack
- **Right Click** - Shoot bow
- **ESC** - Return to menu

### Win Conditions
- **Solos/Doubles**: Be top 3 teams remaining
- **Squads**: Be top 2 teams remaining  
- **5v5/1v1/2v2**: Be last team standing

### Coin Rewards
- Base game: **50 coins**
- Per kill: **+100 coins**
- Bed destruction: **+200 coins**
- Victory bonus: **+500 coins**
- Good performance: ~**50 coins average**

## 🏗️ Project Structure

```
bedwars-game/
├── main.py                 # Game entry point
├── config.py              # Configuration settings
├── setup.py               # Setup script
├── run.py                 # Game launcher
├── run_server.py          # Server launcher
├── tests.py               # Test suite
├── DEVELOPMENT.md         # Developer guide
├── auth/                  # Authentication system
│   ├── database.py        # SQLite database
│   └── encryption.py      # Password encryption
├── game/                  # Core game logic
│   ├── game_manager.py    # Game controller
│   ├── entities.py        # Players, bots, items
│   ├── physics.py         # Physics engine
│   ├── game_modes.py      # Game mode definitions
│   ├── rendering.py       # 3D rendering
│   └── multiplayer.py     # Multiplayer sync
├── ai/                    # Bot AI system
│   ├── bot_ai.py          # Bot behavior
│   ├── pathfinding.py     # A* pathfinding
│   └── combat_ai.py       # Combat logic
├── shop/                  # Shop system
│   ├── shop_manager.py    # Shop logic
│   ├── characters.py      # Character definitions
│   └── cosmetics.py       # Cosmetic items
├── ui/                    # User interface
│   ├── menu.py            # Main menu
│   ├── screens.py         # Auth & mode select
│   ├── hud.py             # In-game HUD
│   └── shop_ui.py         # Shop interface
├── networking/            # Multiplayer networking
│   ├── server.py          # Game server
│   ├── client.py          # Client connection
│   └── protocol.py        # Network protocol
├── assets/                # Game assets
│   ├── models/
│   ├── textures/
│   └── sounds/
└── requirements.txt       # Dependencies
```

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Window
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
FPS = 60

# Player
PLAYER_MAX_HP = 100
PLAYER_SPEED = 5.0

# Combat
MELEE_DAMAGE = 25
BOW_DAMAGE = 30

# Economy
BASE_COIN_REWARD = 50
KILL_BONUS = 100
VICTORY_BONUS = 500

# Network
DEFAULT_PORT = 5000
MAX_PLAYERS = 20
```

## 🤖 Bot AI

Bots scale with player level:
- **Level 1-10** (Easy): 50% accuracy, 0.8s reaction
- **Level 11-20** (Medium): 70% accuracy, 0.5s reaction
- **Level 21-30** (Hard): 85% accuracy, 0.3s reaction
- **Level 31+** (Expert): 95% accuracy, 0.1s reaction

## 🧪 Testing

```bash
# Run all tests
python tests.py

# Test specific system
python -c "from tests import test_database; test_database()"
```

## 📊 Statistics Tracking

The game tracks:
- Total wins and losses
- Kills, deaths, assists
- Beds destroyed
- Performance scores
- Character preferences
- Cosmetic collection

## 🔐 Security

- Passwords hashed with PBKDF2-SHA256 (100,000 iterations)
- SQL injection prevention with parameterized queries
- Input validation on all user data
- Encrypted password storage

## 🌐 Multiplayer

- **Server**: Accepts up to 20 concurrent players
- **Protocol**: JSON-based messaging
- **Sync Rate**: 50ms updates
- **Latency**: Handles up to 500ms ping

## 🐛 Known Limitations

- Basic 3D models (simple cubes/spheres)
- No texture mapping (uses solid colors)
- No advanced graphics (shadows, particles)
- Single server instance
- No persistent multiplayer lobbies

## 🚀 Future Enhancements

- [ ] Advanced graphics (textures, normal maps)
- [ ] More game modes and maps
- [ ] Ranked matchmaking system
- [ ] Clan/team system
- [ ] Replays and spectating
- [ ] Voice chat
- [ ] Trading between players
- [ ] Battle pass system
- [ ] Custom games
- [ ] Mobile support

## 📝 License

This project is provided as-is for educational and entertainment purposes.

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## 📧 Support

For issues, questions, or suggestions, please open an issue on GitHub.

## 👨‍💻 Developer Guide

See `DEVELOPMENT.md` for detailed development documentation.

---

**Made with ❤️ by DaCreator67**

*Bedwars 3D - A fully-featured 3D game built with Python, Pygame, and OpenGL*
