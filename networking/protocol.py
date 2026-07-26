"""Network protocol definitions."""
from enum import Enum
import json
from typing import Any, Dict


class MessageType(Enum):
    """Network message types."""
    # Connection
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    HEARTBEAT = "heartbeat"
    
    # Game state
    GAME_START = "game_start"
    GAME_UPDATE = "game_update"
    GAME_END = "game_end"
    
    # Player actions
    PLAYER_MOVE = "player_move"
    PLAYER_ATTACK = "player_attack"
    PLAYER_DEATH = "player_death"
    PLAYER_SPAWN = "player_spawn"
    
    # Item interactions
    ITEM_PICKUP = "item_pickup"
    ITEM_DROP = "item_drop"
    ITEM_USE = "item_use"
    
    # Chat
    CHAT_MESSAGE = "chat_message"
    
    # Acknowledgement
    ACK = "ack"
    ERROR = "error"


class NetworkMessage:
    """Network message packet."""
    
    def __init__(self, msg_type: MessageType, data: Dict[str, Any] = None, client_id: str = None):
        self.type = msg_type
        self.data = data or {}
        self.client_id = client_id
        self.timestamp = 0
    
    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps({
            'type': self.type.value,
            'data': self.data,
            'client_id': self.client_id,
            'timestamp': self.timestamp
        })
    
    @staticmethod
    def from_json(json_str: str) -> 'NetworkMessage':
        """Deserialize from JSON."""
        try:
            data = json.loads(json_str)
            msg = NetworkMessage(
                MessageType(data['type']),
                data.get('data', {}),
                data.get('client_id')
            )
            msg.timestamp = data.get('timestamp', 0)
            return msg
        except:
            return None


class GameProtocol:
    """Game-specific protocol handlers."""
    
    @staticmethod
    def create_player_move_message(player_id: int, position: dict, rotation: dict) -> NetworkMessage:
        """Create player move message."""
        return NetworkMessage(
            MessageType.PLAYER_MOVE,
            {
                'player_id': player_id,
                'position': position,
                'rotation': rotation
            }
        )
    
    @staticmethod
    def create_player_attack_message(player_id: int, target_id: int, attack_type: str) -> NetworkMessage:
        """Create player attack message."""
        return NetworkMessage(
            MessageType.PLAYER_ATTACK,
            {
                'player_id': player_id,
                'target_id': target_id,
                'attack_type': attack_type
            }
        )
    
    @staticmethod
    def create_game_update_message(game_state: dict) -> NetworkMessage:
        """Create game state update message."""
        return NetworkMessage(
            MessageType.GAME_UPDATE,
            {'state': game_state}
        )
    
    @staticmethod
    def create_player_death_message(player_id: int, killer_id: int = None) -> NetworkMessage:
        """Create player death message."""
        return NetworkMessage(
            MessageType.PLAYER_DEATH,
            {
                'player_id': player_id,
                'killer_id': killer_id
            }
        )
