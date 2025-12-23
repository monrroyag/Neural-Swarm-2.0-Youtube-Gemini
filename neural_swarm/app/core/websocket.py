import json
from datetime import datetime
from typing import List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str, type: str = "info", payload: dict = None):
        data = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "message": message,
            "type": type,
            "payload": payload
        }
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(data, ensure_ascii=False))
            except:
                pass

manager = ConnectionManager()
