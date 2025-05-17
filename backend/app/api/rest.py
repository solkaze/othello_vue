from fastapi import APIRouter
from pydantic import BaseModel

from app.services.matchmaker import matchmaker

router = APIRouter()

class NamePayload(BaseModel):
    name: str

@router.post("/name_check")
async def name_check(payload: NamePayload):
    duplicate = (
        payload.name in matchmaker.players
        or (matchmaker.waiting_player and matchmaker.waiting_player.name == payload.name)
    )
    return {"ok": not duplicate}

@router.get("/status/{name}")
async def status(name: str):
    p = matchmaker.players.get(name)
    if not p:
        return {"connected": False}
    return {"connected": True, "room": p.room_id, "role": p.role, "color": p.color}

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