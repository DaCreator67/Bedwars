# Installation and Running Instructions

## System Requirements

- Python 3.8 or higher
- 4GB RAM minimum
- OpenGL 2.1+ support
- Modern graphics card
- 500MB disk space

## Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/DaCreator67/Sell.git
cd Sell
git checkout bedwars-game
```

### 2. Install Python Dependencies

```bash
# Linux/Mac
pip3 install -r requirements.txt

# Windows
pip install -r requirements.txt
```

### 3. Run Setup

```bash
python setup.py
```

This will:
- Create necessary directories
- Initialize the database
- Create a demo account
- Fund demo account with starting coins

## Running the Game

### Single Player (with Bots)

```bash
python run.py
```

Login with:
- **Username**: demo
- **Password**: demo123

### Multiplayer Mode

**Terminal 1 - Start Server:**
```bash
python run_server.py
```

**Terminal 2+ - Start Clients:**
```bash
python run.py
```

Clients will automatically connect to localhost server.

## Troubleshooting

### "ModuleNotFoundError: No module named 'pygame'"

```bash
pip install pygame PyOpenGL numpy
```

### "OpenGL error" on startup

- Update your graphics drivers
- Install 32-bit Python libraries if needed:
  ```bash
  sudo apt-get install libgl1-mesa-glx  # Linux
  ```

### Database error ("database is locked")

```bash
# Delete and recreate database
rm game.db
python setup.py
```

### Low FPS / Performance Issues

1. Reduce bot count (set BOT_SPAWN_DELAY higher)
2. Lower graphics quality in config.py
3. Reduce window resolution
4. Close other applications

### Port already in use (server)

Change port in `config.py`:
```python
DEFAULT_PORT = 5001  # Use different port
```

## First Time Setup Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Setup completed (`python setup.py`)
- [ ] Game starts (`python run.py`)
- [ ] Can login with demo/demo123
- [ ] Can select game mode
- [ ] Can start game

## Performance Tips

1. **Close background apps** - Free up RAM and CPU
2. **Lower graphics quality** - Reduces render time
3. **Reduce player count** - Fewer entities to update
4. **Disable sound** - Saves CPU cycles
5. **Use wired connection** - For multiplayer

## Getting Started

1. Launch game: `python run.py`
2. Create new account or login to demo
3. View shop to see characters
4. Select game mode (recommend Solos first)
5. Play! Earn coins for performance
6. Buy characters to unlock perks

## Command Line Options

```bash
# Run with specific configuration
PLAYER_SPEED=7 python run.py

# Start server on specific port
DEFAULT_PORT=5001 python run_server.py

# Run tests
python tests.py

# Run specific test
python -c "from tests import test_database; test_database()"
```

## Need Help?

Check `DEVELOPMENT.md` for more detailed information on:
- Project architecture
- Adding new features
- Networking setup
- Performance optimization

## Next Steps

1. ✅ Installation complete!
2. Create your account or login with demo
3. Explore the shop
4. Play your first game
5. Earn coins and buy characters
6. Climb the ranks!

---

**Enjoy Bedwars 3D!** 🎮
