from __future__ import annotations
from typing import Dict, Optional, List
import uuid
import hashlib
from fastapi import HTTPException
import logging
logging.basicConfig(level=logging.INFO)

from app.models.player import Player
from app.models.room import Room

class MatchMaker:
    """待機列 + ルーム管理 (singleton)"""

    def __init__(self):
        self.waiting_player: Optional[Player] = None
        self.rooms: Dict[str, Room] = {}
        self.players: Dict[str, Player] = {}

    # --- player 登録 ---
    async def add_player(self, p: Player, room_id: str):
        if p.name in self.players:
            logging.info("名前の重複不可")
            raise HTTPException(400, "同名が接続中です")
        self.players[p.name] = p

        if p.role == "spectator":
            await p.send(self._rooms_payload())
            return

        # ---- player マッチング ----
        room = self.rooms[room_id]
        room.add_player(p)
        
        logging.info(f"player1: {room.players["black"].name}, player2: {room.players["white"].name}")

        # 既に待機者がいる → ルーム作成
        p1, p2 = room.players["black"], room.players["white"]
        logging.info(f"id: {room_id}")

        p2.room_id = room_id

        await room.broadcast({
            "type": "matched",
            "room": room_id,
            "player1": p1.name,
            "player2": p2.name,
        })
    
    # --- 部屋建て ---
    async def create_room(self, p: Player):
        room_id = generate_hash_id()
        room = Room(room_id=room_id, player1=p)
        self.rooms[room_id] = room
        logging.info(f"id: {room_id}")
        p.room_id = room_id
        logging.info(f"waiting player: {p.name}")
        await p.send({"type": "wait", "message": "対戦相手を待機中...", "room": room_id})
        return

    # --- player 離脱 ---
    async def remove_player(self, p: Player, code = 1000):
        logging.info(f"leave_code2: {code}")
        if self.waiting_player is p:
            self._unregister(p)
            return

        room = self.rooms.get(p.room_id)
        if not room:
            self._unregister(p)
            return

        if p in room.spectators:
            room.spectators.remove(p)
            return

        # 残りがいれば全員 close
        if room.players or room.spectators:
            await room.close_all(code=code, reason=f"{p.name} left")
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

def generate_hash_id(length=5):
    base = str(uuid.uuid4())
    hash_value = hashlib.sha1(base.encode()).hexdigest()  # SHA-1の16進数
    return hash_value[:length]

# singleton
matchmaker = MatchMaker()