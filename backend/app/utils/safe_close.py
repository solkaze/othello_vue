from starlette.websockets import WebSocket, WebSocketState

async def safe_close(ws: WebSocket):
    if ws.application_state != WebSocketState.DISCONNECTED:
        try:
            await ws.close()
        except RuntimeError:
            pass