from starlette.websockets import WebSocket, WebSocketState

import logging
logging.basicConfig(level=logging.INFO)

async def safe_close(ws: WebSocket):
    if ws.application_state != WebSocketState.DISCONNECTED:
        try:
            logging.info("code: 1005")
            await ws.close()
        except RuntimeError:
            pass