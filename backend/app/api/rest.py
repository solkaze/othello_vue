from fastapi import APIRouter
from pydantic import BaseModel
import logging
logging.basicConfig(level=logging.INFO)

from app.services.matchmaker import matchmaker

router = APIRouter()

class NameCheckRequest(BaseModel):
    name: str
    room_id: str

class idPayload(BaseModel):
    room_id: str

@router.post("/room_check")
async def room_check(payload: idPayload):
    duplicate = None
    room = matchmaker.rooms.get(payload.room_id)
    if not room:
        duplicate = True

    logging.info(f"check: {duplicate}")
    return {"ok": not duplicate}

@router.post("/name_check")
async def name_check(payload: NameCheckRequest):
    duplicate = None
    room = matchmaker.rooms.get(payload.room_id)
    logging.info(room.players.values())
    if room:
        duplicate = any(
            payload.name == player.name
            for player in room.players.values()
            if player
        )

    logging.info(f"check: {duplicate}")
    return {"ok": not duplicate}

@router.get("/status/{name}")
async def status(name: str):
    p = matchmaker.players.get(name)
    if not p:
        return {"connected": False}
    return {"connected": True, "room": p.room_id, "role": p.role}

@router.get("/rooms")
async def list_rooms():
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