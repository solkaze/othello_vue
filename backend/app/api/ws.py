from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.models.player import Player
from app.services.matchmaker import matchmaker
from app.utils.safe_close import safe_close

router = APIRouter()

@router.websocket("/ws/othello/{name}")
async def websocket_endpoint(websocket: WebSocket, name: str):
    role = websocket.query_params.get("role", "player")
    await websocket.accept()
    player = Player(name, websocket, role)

    try:
        await matchmaker.add_player(player)

        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            # Spectator
            if player.role == "spectator":
                if msg_type == "join_room":
                    room_id = data.get("room")
                    room = matchmaker.rooms.get(room_id)
                    if not room:
                        await player.send({"type": "error", "message": "Room が存在しません"})
                        continue
                    player.room_id = room_id
                    room.spectators.append(player)
                    await player.send({
                        "type": "joined",
                        "room": room_id,
                        "black": room.players["black"].name,
                        "white": room.players["white"].name,
                    })
                elif msg_type == "leave":
                    await matchmaker.remove_player(player)
                    break
                else:
                    await player.send({"type": "error", "message": "Spectator はこの操作を行えません"})
                continue

            # Player actions
            if msg_type == "start_request":
                room = matchmaker.rooms.get(player.room_id)
                
                if room is None:
                    return
                
                first = data.get("first", "black")
                room.turn = first
                
                await room.broadcast({
                    "type": "start",
                    "room": room_id,
                    "first": first
                })

            elif msg_type == "move":
                room = matchmaker.rooms.get(player.room_id)
                if room and player.color == room.turn:
                    x, y = int(data["x"]), int(data["y"])
                    await room.broadcast({
                        "type": "move",
                        "x": x,
                        "y": y,
                        "color": room.turn,
                    })
                    room.turn = "white" if room.turn == "black" else "black"
                else:
                    await player.send({"type": "error", "message": "まだあなたの手番ではありません"})

            elif msg_type == "chat":
                room = matchmaker.rooms.get(player.room_id)
                if room:
                    await room.broadcast({
                        "type": "chat",
                        "from": player.name,
                        "message": data["message"],
                    })

            elif msg_type == "leave":
                await matchmaker.remove_player(player)
                break

            else:
                await player.send({"type": "error", "message": "未知のメッセージタイプ"})

    except WebSocketDisconnect:
        await matchmaker.remove_player(player)
    finally:
        await safe_close(websocket)