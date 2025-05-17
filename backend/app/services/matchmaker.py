from __future__ import annotations
from typing import Dict, Optional, List
import uuid
from fastapi import HTTPException

from app.models.player import Player
from app.models.room import Room

class MatchMaker:
    """待機列 + ルーム管理 (singleton)"""

    def __init__(self):
        self.waiting_player: Optional[Player] = None
        self.rooms: Dict[str, Room] = {}
        self.players: Dict[str, Player] = {}

    # --- player 登録 ---
    async def add_player(self, p: Player):
        if p.name in self.players:
            raise HTTPException(400, "同名が接続中です")
        self.players[p.name] = p

        if p.role == "spectator":
            await p.send(self._rooms_payload())
            return

        # ---- player マッチング ----
        if self.waiting_player is None:
            self.waiting_player = p
            await p.send({"type": "wait", "message": "対戦相手を待機中..."})
            return

        # 既に待機者がいる → ルーム作成
        p1, p2 = self.waiting_player, p
        self.waiting_player = None

        room_id = str(uuid.uuid4())
        room = Room(room_id, black=p1, white=p2)
        self.rooms[room_id] = room

        p1.room_id = p2.room_id = room_id
        p1.color, p2.color = "black", "white"

        await room.broadcast({
            "type": "matched",
            "room": room_id,
            "black": p1.name,
            "white": p2.name,
        })

    # --- player 離脱 ---
    async def remove_player(self, p: Player):
        if self.waiting_player is p:
            self._unregister(p)
            return

        room = self.rooms.get(p.room_id)
        if not room:
            self._unregister(p)
            return

        # 部屋から外す
        if p.color in room.players:
            del room.players[p.color]
        elif p in room.spectators:
            room.spectators.remove(p)

        # 残りがいれば全員 close
        if room.players or room.spectators:
            await room.close_all(reason=f"{p.name} left")
            for q in list(room.players.values()) + room.spectators:
                self._unregister(q)

        self.rooms.pop(p.room_id, None)
        self._unregister(p)

    # ---------------------------------------------------------
    def _unregister(self, p: Player):
        self.players.pop(p.name, None)
        if self.waiting_player is p:
            self.waiting_player = None

    def _rooms_payload(self):
        return {
            "type": "rooms",
            "rooms": [
                {
                    "id": r.id,
                    "black": r.players["black"].name,
                    "white": r.players["white"].name,
                    "spectators": len(r.spectators),
                }
                for r in self.rooms.values()
            ],
        }

# singleton
matchmaker = MatchMaker()