from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging

from app.models.player import Player
from app.services.matchmaker import matchmaker
from app.utils.safe_close import safe_close

logging.basicConfig(level=logging.INFO)

router = APIRouter()

@router.websocket("/ws/othello/{name}")
async def websocket_endpoint(websocket: WebSocket, name: str):
    role = websocket.query_params.get("role", "player")
    host = websocket.query_params.get("host", "false").lower() == "true"
    select_room_id = websocket.query_params.get("room", "XXXXX")
    await websocket.accept()
    logging.info(f"Player {name} connected")
    player = Player(name, websocket, role, host) # プレイヤーのインスタンス
    try:
        if host:
            await matchmaker.create_room(player)
        else:
            await matchmaker.add_player(player, select_room_id)

        while True:
            # jsonで受取
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
            
            room_id = data.get("room")
            # Player actions
            if msg_type == "start_request": # first me : opp
                room = matchmaker.rooms.get(player.room_id)
                first = data.get("first")
                logging.info(f"first: {first}")
                
                if room is None:
                    return
                
                # 色を設定する処理が必要
                if first != room.players["black"].name:
                    room.swap_player_colors()
                
                logging.info(f"black: {room.players["black"].name}, white: {room.players["white"].name}")
                
                room.turn = first
                await room.broadcast({
                    "type": "start",
                    "room": room.id,
                    "first": room.turn,
                    "black": room.players["black"].name,
                    "white": room.players["white"].name
                })
            elif msg_type == "move":
                """石を置くときの処理"""
                room = matchmaker.rooms.get(player.room_id)
                isSkip = data.get("isSkip")
                if room:
                    x, y = int(data["x"]), int(data["y"])
                    logging.info(f"{player.name}: x: {x}, y: {y}")
                    await room.broadcast({
                        "type": "move",
                        "x": x,
                        "y": y,
                        "turn": room.turn,
                    })
                    if not isSkip:
                        room.turn = room.players["black"].name if room.turn == room.players["white"].name else room.players["white"].name
                else:
                    logging.info(f"配置拒否")
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