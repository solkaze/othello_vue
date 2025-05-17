from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Optional, List
from starlette.websockets import WebSocketState
import uuid
from pydantic import BaseModel

# ------------------------------------------------------------
# FastAPI アプリ初期化
# ------------------------------------------------------------
app = FastAPI()

# ★ 本番では許可ドメインを絞る
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------
# データモデル
# ------------------------------------------------------------
class Player:
    """WebSocket 1 本 = 1 Player or Spectator"""

    def __init__(self, name: str, websocket: WebSocket, role: str = "player"):
        self.name: str = name
        self.websocket: WebSocket = websocket
        self.role: str = role  # "player" | "spectator"
        self.room_id: Optional[str] = None
        self.color: Optional[str] = None  # "black" | "white" | None

    async def send(self, data: dict):
        await self.websocket.send_json(data)


class Room:
    def __init__(self, room_id: str, black: Player, white: Player):
        self.id = room_id
        self.players: Dict[str, Player] = {"black": black, "white": white}
        self.spectators: List[Player] = []

    # ────────────────────────────────────────────────
    # Utility
    # ────────────────────────────────────────────────
    def opponent_of(self, color: str) -> Player:
        return self.players["white" if color == "black" else "black"]

    async def broadcast(self, payload: dict, *, include_players=True, include_spectators=True):
        targets = []
        if include_players:
            targets.extend(p.websocket for p in self.players.values())
        if include_spectators:
            targets.extend(s.websocket for s in self.spectators)

        for ws in targets:
            try:
                # すでに閉じていないか念のため確認
                if ws.application_state == WebSocketState.DISCONNECTED:
                    continue
                await ws.send_json(payload)
            except Exception:
                # ログだけ残して続行。ここで raise しない
                import logging; logging.warning("broadcast failed", exc_info=True)


class MatchMaker:
    """プレイヤーの待機キューとアクティブルームを管理"""

    def __init__(self) -> None:
        self.waiting_player: Optional[Player] = None  # 先着 1 名を待機状態に
        self.rooms: Dict[str, Room] = {}
        self.players: Dict[str, Player] = {}  # name -> Player (spectator 含む)

    # ────────────────────────────────────────────────
    # 登録 / 削除
    # ────────────────────────────────────────────────
    async def add(self, p: Player):
        if p.name in self.players:
            raise HTTPException(400, "同名のユーザーが既に接続しています")
        self.players[p.name] = p

        # Spectator はまず部屋リストを渡して終了
        if p.role == "spectator":
            await p.send(
                {
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
            )
            return

        # Player マッチング
        if self.waiting_player is None:
            self.waiting_player = p
            await p.send({"type": "wait", "message": "対戦相手を待機中..."})
        else:
            p1 = self.waiting_player
            p2 = p
            self.waiting_player = None

            room_id = str(uuid.uuid4())
            room = Room(room_id, black=p1, white=p2)
            self.rooms[room_id] = room

            p1.room_id = p2.room_id = room_id
            p1.color, p2.color = "black", "white"

            await room.broadcast(
                {
                    "type": "matched",
                    "room": room_id,
                    "black": p1.name,
                    "white": p2.name,
                }
            )

    async def remove(self, p: Player):
        # 待機キューにいる？
        if self.waiting_player is p:
            self.waiting_player = None

        # 部屋から除外
        if p.room_id and p.room_id in self.rooms:
            room = self.rooms[p.room_id]

            if p.role == "player":
                # 対戦プレイヤーが退室 → 全員切断して部屋を削除
                try:
                    await room.broadcast({"type": "leave", "message": f"{p.name} が退室しました"})
                except Exception:
                    pass
                for ws in [pl.websocket for pl in room.players.values()] + [sp.websocket for sp in room.spectators]:
                    try:
                        await ws.close()
                    except Exception:
                        pass
                del self.rooms[p.room_id]
            else:
                # Spectator の場合はリストから外すだけ
                room.spectators = [s for s in room.spectators if s is not p]

        # 最後に全体リストから除外
        self.players.pop(p.name, None)


async def safe_close(ws):
    # Starlette ≥0.33 では .application_state で判定できる
    if ws.application_state != WebSocketState.DISCONNECTED:
        try:
            await ws.close()
        except RuntimeError:
            # すでに close 済みだった場合は何もしない
            pass


matchmaker = MatchMaker()

# ------------------------------------------------------------
# WebSocket エンドポイント
# ------------------------------------------------------------
@app.websocket("/ws/othello/{name}")
async def websocket_endpoint(websocket: WebSocket, name: str):
    # クエリパラメータ role=? を取得（無ければ player）
    role = websocket.query_params.get("role", "player")

    await websocket.accept()
    player = Player(name, websocket, role)

    try:
        await matchmaker.add(player)

        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            # ───── Spectator モード ─────
            if player.role == "spectator":
                if msg_type == "join_room":
                    room_id = data.get("room")
                    room = matchmaker.rooms.get(room_id)
                    if not room:
                        await player.send({"type": "error", "message": "Room が存在しません"})
                        continue
                    player.room_id = room_id
                    room.spectators.append(player)
                    await player.send(
                        {
                            "type": "joined",
                            "room": room_id,
                            "black": room.players["black"].name,
                            "white": room.players["white"].name,
                        }
                    )
                elif msg_type == "start_request":
                    room = matchmaker.rooms.get(player.room_id)
                    if room:
                        await room.broadcast(
                            {
                                "type": "start",
                                "room": player.room_id,
                                "first": data.get("first", "black"),
                            }
                        )
                elif msg_type == "leave":
                    await matchmaker.remove(player)
                    await websocket.close()
                    break
                else:
                    await player.send({"type": "error", "message": "Spectator はこの操作を行えません"})
                continue  # Spectator 処理はここでループ

            # ───── Player モード ─────
            if msg_type == "move":
                room = matchmaker.rooms.get(player.room_id)
                if room:
                    await room.broadcast(
                        {
                            "type": "move",
                            "x": data["x"],
                            "y": data["y"],
                            "color": player.color,
                        }
                    )

            elif msg_type == "chat":
                room = matchmaker.rooms.get(player.room_id)
                if room:
                    await room.broadcast(
                        {
                            "type": "chat",
                            "from": player.name,
                            "message": data["message"],
                        }
                    )

            elif msg_type == "leave":
                await matchmaker.remove(player)
                await websocket.close()
                break

            else:
                await player.send({"type": "error", "message": "未知のメッセージタイプ"})

    except WebSocketDisconnect:
        # クライアント側が自発的に切っただけ。後始末だけ行う
        await matchmaker.remove(player)
    except Exception as exc:
        # 想定外のエラー時だけクライアントへ通知
        if websocket.application_state == WebSocketState.CONNECTED:
            await websocket.send_json({"type": "error", "message": str(exc)})
        await matchmaker.remove(player)
    finally:
        await safe_close(websocket)


# ------------------------------------------------------------
# 補助 REST API
# ------------------------------------------------------------
class NamePayload(BaseModel):
    name: str


@app.post("/name_check")
async def name_check(payload: NamePayload):
    duplicate = (
        payload.name in matchmaker.players
        or (matchmaker.waiting_player and matchmaker.waiting_player.name == payload.name)
    )
    return {"ok": not duplicate}


@app.get("/status/{name}")
async def status(name: str):
    p = matchmaker.players.get(name)
    if not p:
        return {"connected": False}
    return {"connected": True, "room": p.room_id, "role": p.role, "color": p.color}


@app.get("/rooms")
async def list_rooms():
    """現在進行中の部屋一覧を取得（観戦 UI 用）"""
    return {
        "rooms": [
            {
                "id": r.id,
                "black": r.players["black"].name,
                "white": r.players["white"].name,
                "spectators": len(r.spectators),
            }
            for r in matchmaker.rooms.values()
        ]
    }
