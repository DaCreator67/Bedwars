"""Game client for multiplayer support."""
import socket
import threading
import time
from typing import Optional, Callable, Dict
from .protocol import NetworkMessage, MessageType, GameProtocol
import config


class GameClient:
    """Client for connecting to multiplayer server."""
    
    def __init__(self, host: str = config.DEFAULT_HOST, port: int = config.DEFAULT_PORT):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.client_id = None
        self.player_id = None
        self.receive_buffer = ""
        self.message_queue = []
        self.message_callbacks: Dict[MessageType, list] = {}
        self.lock = threading.Lock()
    
    def connect(self, player_id: int, username: str) -> bool:
        """Connect to server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.player_id = player_id
            
            # Send connect message
            connect_msg = NetworkMessage(
                MessageType.CONNECT,
                {'player_id': player_id, 'username': username}
            )
            self.send_message(connect_msg)
            
            # Start receive thread
            receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            receive_thread.start()
            
            # Start heartbeat thread
            heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
            heartbeat_thread.start()
            
            self.connected = True
            print(f"[Client] Connected to {self.host}:{self.port}")
            return True
        
        except Exception as e:
            print(f"[Client] Failed to connect: {e}")
            return False
    
    def send_message(self, message: NetworkMessage):
        """Send message to server."""
        if not self.connected or not self.socket:
            return
        
        try:
            message.client_id = self.client_id
            msg_json = message.to_json()
            self.socket.send((msg_json + '\n').encode('utf-8'))
        except Exception as e:
            print(f"[Client] Send error: {e}")
            self.connected = False
    
    def send_player_move(self, position: dict, rotation: dict):
        """Send player movement update."""
        msg = GameProtocol.create_player_move_message(self.player_id, position, rotation)
        self.send_message(msg)
    
    def send_player_attack(self, target_id: int, attack_type: str):
        """Send player attack."""
        msg = GameProtocol.create_player_attack_message(self.player_id, target_id, attack_type)
        self.send_message(msg)
    
    def send_chat_message(self, text: str):
        """Send chat message."""
        msg = NetworkMessage(MessageType.CHAT_MESSAGE, {'text': text, 'player_id': self.player_id})
        self.send_message(msg)
    
    def register_callback(self, msg_type: MessageType, callback: Callable):
        """Register callback for message type."""
        if msg_type not in self.message_callbacks:
            self.message_callbacks[msg_type] = []
        self.message_callbacks[msg_type].append(callback)
    
    def get_messages(self) -> list:
        """Get all received messages."""
        with self.lock:
            messages = self.message_queue[:]
            self.message_queue.clear()
        return messages
    
    def _receive_loop(self):
        """Receive messages from server."""
        while self.connected:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                self.receive_buffer += data
                
                # Extract complete messages
                while '\n' in self.receive_buffer:
                    line, self.receive_buffer = self.receive_buffer.split('\n', 1)
                    msg = NetworkMessage.from_json(line)
                    if msg:
                        if msg.type == MessageType.ACK and not self.client_id:
                            self.client_id = msg.data.get('client_id')
                        
                        # Add to queue
                        with self.lock:
                            self.message_queue.append(msg)
                        
                        # Call callbacks
                        if msg.type in self.message_callbacks:
                            for callback in self.message_callbacks[msg.type]:
                                try:
                                    callback(msg)
                                except:
                                    pass
            
            except Exception as e:
                if self.connected:
                    print(f"[Client] Receive error: {e}")
                    self.connected = False
                break
            
            time.sleep(0.01)
    
    def _heartbeat_loop(self):
        """Send heartbeat to server."""
        while self.connected:
            try:
                hb = NetworkMessage(MessageType.HEARTBEAT)
                self.send_message(hb)
                time.sleep(5)
            except:
                break
    
    def disconnect(self):
        """Disconnect from server."""
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        print("[Client] Disconnected")
