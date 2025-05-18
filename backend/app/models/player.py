from __future__ import annotations
from typing import Optional
from fastapi import WebSocket

class Player:
    """WebSocket 1 本 = 1 Player or Spectator"""

    def __init__(self, name: str, websocket: WebSocket, role: str = "player", host: bool = False) -> None:
        self.name: str = name
        self.websocket: WebSocket = websocket
        self.role: str = role              # "player" | "spectator"
        self.ishost: bool = host
        self.room_id: Optional[str] = None

    # 便利ラッパ
    async def send(self, data: dict):
        await self.websocket.send_json(data)