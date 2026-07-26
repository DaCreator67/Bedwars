"""Multiplayer game manager."""
from typing import Dict, Optional
from networking.client import GameClient
from networking.protocol import MessageType
from game.game_manager import GameManager
from game.entities import Player


class MultiplayerGameManager:
    """Manages multiplayer game synchronization."""
    
    def __init__(self, game_manager: GameManager, client: GameClient = None):
        self.game_manager = game_manager
        self.client = client
        self.is_host = client is None
        self.last_update_time = 0.0
        self.update_interval = 0.05  # Send updates every 50ms
        self.remote_players: Dict[int, dict] = {}
    
    def update(self, delta_time: float):
        """Update multiplayer synchronization."""
        if self.client and self.client.connected:
            self.last_update_time += delta_time
            
            if self.last_update_time >= self.update_interval:
                self._send_updates()
                self._process_messages()
                self.last_update_time = 0.0
    
    def _send_updates(self):
        """Send game state updates to server."""
        for player_id, player in self.game_manager.players.items():
            if player.player_id < 0:  # Skip bots
                continue
            
            # Send player position/rotation
            position = {
                'x': player.position.x,
                'y': player.position.y,
                'z': player.position.z
            }
            rotation = {
                'yaw': player.yaw,
                'pitch': player.pitch
            }
            self.client.send_player_move(position, rotation)
    
    def _process_messages(self):
        """Process incoming messages."""
        if not self.client:
            return
        
        messages = self.client.get_messages()
        
        for msg in messages:
            if msg.type == MessageType.PLAYER_MOVE:
                self._handle_remote_player_move(msg.data)
            elif msg.type == MessageType.PLAYER_ATTACK:
                self._handle_remote_player_attack(msg.data)
            elif msg.type == MessageType.CHAT_MESSAGE:
                print(f"[Chat] {msg.data.get('text')}")
    
    def _handle_remote_player_move(self, data: dict):
        """Handle remote player movement."""
        player_id = data.get('player_id')
        position = data.get('position')
        rotation = data.get('rotation')
        
        if player_id in self.game_manager.players:
            player = self.game_manager.players[player_id]
            player.position.x = position['x']
            player.position.y = position['y']
            player.position.z = position['z']
            player.yaw = rotation['yaw']
            player.pitch = rotation['pitch']
    
    def _handle_remote_player_attack(self, data: dict):
        """Handle remote player attack."""
        attacker_id = data.get('player_id')
        attack_type = data.get('attack_type')
        
        if attack_type == 'melee':
            self.game_manager.player_attack_melee(attacker_id)
