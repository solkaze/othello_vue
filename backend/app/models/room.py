from __future__ import annotations
from typing import Dict, List
from starlette.websockets import WebSocketState
from typing import Optional
import logging
logging.basicConfig(level=logging.INFO)

from app.models.player import Player

BLACK = "black"
WHITE = "white"

class Room:
    """対戦 1 つ分の状態（盤面はクライアント任せなので保持しない）"""

    def __init__(self, room_id: str, player1: Player):
        self.id: str = room_id
        # white はまだ入らないので Optional に
        self.players: Dict[str, Optional[Player]] = {BLACK: player1, WHITE: None}
        self.spectators: List[Player] = []
        self.turn: str = player1.name          # ここを "black" にしても OK

    def add_player(self, player: Player):
        logging.info(f"add_player: {player.name}")
        if self.players[WHITE] is None:
            self.players[WHITE] = player
        else:
            # すでに 2 人そろっている場合は上書きさせない
            raise ValueError("Both players are already set.")

    # opponent 取得
    def opponent_of(self, color: str) -> Player:
        return self.players[WHITE if color == BLACK else BLACK]

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

    async def close_all(self, *,code: int = 1000, reason: str = "player_left"):
        targets = [p.websocket for p in self.players.values() if p is not None] + self.spectators
        logging.info("close_all")
        logging.info(self.players)
        logging.info(targets)
        for ws in targets:
            try:
                logging.info(f"{ws}")
                reason = f"{ws} close"
                logging.info(f"code: {code}")
                await ws.close(code=code, reason=reason)
            except Exception:
                pass
        self.players.clear()
        self.spectators.clear()

    def swap_player_colors(self) -> None:
        """黒と白のプレイヤーを入れ替える。"""
        self.players[BLACK], self.players[WHITE] = self.players[WHITE], self.players[BLACK]
        if self.turn != self.players[BLACK]:
            self.turn = self.players[BLACK]
