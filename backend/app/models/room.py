from __future__ import annotations
from typing import Dict, List
from starlette.websockets import WebSocketState

from app.models.player import Player

class Room:
    """対戦 1 つ分の状態（盤面はクライアント任せなので保持しない）"""

    def __init__(self, room_id: str, black: Player, white: Player):
        self.id: str = room_id
        self.players: Dict[str, Player] = {"black": black, "white": white}
        self.spectators: List[Player] = []
        self.turn: str = "black"  # 'black' | 'white'

    # opponent 取得
    def opponent_of(self, color: str) -> Player:
        return self.players["white" if color == "black" else "black"]

    # ------- broadcast -------
    async def broadcast(self, payload: dict, *, include_players=True, include_spectators=True):
        targets = []
        if include_players:
            targets.extend(p.websocket for p in self.players.values())
        if include_spectators:
            targets.extend(s.websocket for s in self.spectators)

        for ws in targets:
            try:
                if ws.application_state == WebSocketState.DISCONNECTED:
                    continue
                await ws.send_json(payload)
            except Exception:
                import logging; logging.warning("broadcast failed", exc_info=True)

    async def close_all(self, *, reason: str = "player_left"):
        targets = [p.websocket for p in self.players.values()] + self.spectators
        for ws in targets:
            try:
                await ws.close(code=4000, reason=reason)
            except Exception:
                pass
        self.players.clear()
        self.spectators.clear()