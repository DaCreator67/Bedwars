"""Game server for multiplayer support."""
import socket
import threading
import time
from typing import Dict, List, Optional
from collections import defaultdict
from .protocol import NetworkMessage, MessageType, GameProtocol
import config
import json


class ClientConnection:
    """Represents a connected client."""
    
    def __init__(self, client_socket: socket.socket, address: tuple, client_id: str):
        self.socket = client_socket
        self.address = address
        self.client_id = client_id
        self.last_heartbeat = time.time()
        self.player_id = None
        self.is_active = True
        self.send_queue = []
        self.receive_buffer = ""
    
    def send_message(self, message: NetworkMessage):
        """Queue message for sending."""
        self.send_queue.append(message.to_json())
    
    def receive_data(self, buffer_size: int = 4096) -> Optional[str]:
        """Receive data from socket."""
        try:
            data = self.socket.recv(buffer_size).decode('utf-8')
            self.receive_buffer += data
            
            # Try to extract complete messages
            messages = []
            while '\n' in self.receive_buffer:
                line, self.receive_buffer = self.receive_buffer.split('\n', 1)
                msg = NetworkMessage.from_json(line)
                if msg:
                    messages.append(msg)
            
            return messages if messages else None
        except:
            return None


class GameServer:
    """Multiplayer game server."""
    
    def __init__(self, host: str = config.DEFAULT_HOST, port: int = config.DEFAULT_PORT):
        self.host = host
        self.port = port
        self.running = False
        self.server_socket = None
        self.clients: Dict[str, ClientConnection] = {}
        self.games = {}  # Active game sessions
        self.client_counter = 0
        self.lock = threading.Lock()
    
    def start(self):
        """Start the server."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(config.MAX_PLAYERS)
            self.running = True
            
            print(f"[Server] Started on {self.host}:{self.port}")
            
            # Start accept thread
            accept_thread = threading.Thread(target=self._accept_connections, daemon=True)
            accept_thread.start()
            
            # Start update thread
            update_thread = threading.Thread(target=self._update_loop, daemon=True)
            update_thread.start()
        
        except Exception as e:
            print(f"[Server] Failed to start: {e}")
            self.running = False
    
    def _accept_connections(self):
        """Accept incoming client connections."""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                self.client_counter += 1
                client_id = f"client_{self.client_counter}"
                
                connection = ClientConnection(client_socket, address, client_id)
                
                with self.lock:
                    self.clients[client_id] = connection
                
                print(f"[Server] Client connected: {client_id} from {address}")
                
                # Start client handler thread
                client_thread = threading.Thread(target=self._handle_client, args=(client_id,), daemon=True)
                client_thread.start()
            
            except:
                if self.running:
                    time.sleep(0.1)
    
    def _handle_client(self, client_id: str):
        """Handle a single client connection."""
        while self.running:
            if client_id not in self.clients:
                break
            
            connection = self.clients[client_id]
            
            try:
                messages = connection.receive_data()
                if messages:
                    for msg in messages:
                        self._handle_message(client_id, msg)
                
                # Send queued messages
                while connection.send_queue:
                    msg_json = connection.send_queue.pop(0)
                    connection.socket.send((msg_json + '\n').encode('utf-8'))
                
                # Check heartbeat
                if time.time() - connection.last_heartbeat > 10:
                    self._disconnect_client(client_id)
                    break
            
            except:
                self._disconnect_client(client_id)
                break
            
            time.sleep(0.01)
    
    def _handle_message(self, client_id: str, message: NetworkMessage):
        """Handle incoming message from client."""
        if message.type == MessageType.CONNECT:
            self._handle_connect(client_id, message)
        
        elif message.type == MessageType.HEARTBEAT:
            connection = self.clients.get(client_id)
            if connection:
                connection.last_heartbeat = time.time()
        
        elif message.type == MessageType.PLAYER_MOVE:
            self._broadcast_message(message, exclude=client_id)
        
        elif message.type == MessageType.PLAYER_ATTACK:
            self._broadcast_message(message, exclude=client_id)
        
        elif message.type == MessageType.CHAT_MESSAGE:
            self._broadcast_message(message)
    
    def _handle_connect(self, client_id: str, message: NetworkMessage):
        """Handle client connection request."""
        player_data = message.data
        connection = self.clients.get(client_id)
        
        if connection:
            connection.player_id = player_data.get('player_id')
            
            # Send acknowledgement
            ack = NetworkMessage(MessageType.ACK, {'status': 'connected', 'client_id': client_id})
            connection.send_message(ack)
            
            print(f"[Server] Player {player_data.get('player_id')} connected as {client_id}")
    
    def _broadcast_message(self, message: NetworkMessage, exclude: str = None):
        """Broadcast message to all connected clients."""
        with self.lock:
            for client_id, connection in self.clients.items():
                if exclude and client_id == exclude:
                    continue
                if connection.is_active:
                    connection.send_message(message)
    
    def _disconnect_client(self, client_id: str):
        """Disconnect a client."""
        with self.lock:
            if client_id in self.clients:
                connection = self.clients[client_id]
                connection.is_active = False
                try:
                    connection.socket.close()
                except:
                    pass
                del self.clients[client_id]
        
        print(f"[Server] Client disconnected: {client_id}")
    
    def _update_loop(self):
        """Server update loop."""
        while self.running:
            # Clean up inactive clients
            with self.lock:
                inactive = [cid for cid, conn in self.clients.items() if not conn.is_active]
                for client_id in inactive:
                    self._disconnect_client(client_id)
            
            time.sleep(0.1)
    
    def stop(self):
        """Stop the server."""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        print("[Server] Stopped")
