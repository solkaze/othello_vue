import socket
import threading
import select
import json
import logging
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# CORSの許可設定（Vueとの通信を許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://frontend:3000",
        "http://localhost:3000"
    ],  # 本番環境では限定してください
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger("uvicorn")

connected_socket = None
server_socket = None

wait_expired = False
wait_cancelled = False
running = False

wait_thread = None

wait_cancel_event = threading.Event()

def wait_for_client():
    global connected_socket, server_socket
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setblocking(False)
        server_socket.bind(('', 10000))
        server_socket.listen(1)

        while not wait_cancel_event.is_set():
            readable, _, _ = select.select([server_socket], [], [], 1.0)
            if readable:
                conn, addr = server_socket.accept()
                print("接続:", addr)
                connected_socket = conn
                break
    finally:
        server_socket.close()
        server_socket = None
        print("ソケットを閉じました")


# /status エンドポイントの修正
@app.get("/status")
async def status():
    return JSONResponse({
        "connected": connected_socket is not None,
        "expired": wait_expired,
        "cancelled": wait_cancelled
    })

# /wait エンドポイント
@app.post("/wait")
async def wait_endpoint(request: Request):
    global wait_thread, server_socket
    try:
        wait_cancel_event.clear()  # 事前にフラグをリセット
        wait_thread = threading.Thread(target=wait_for_client, daemon=True)
        wait_thread.start()
        print("🟢 接続待機スレッドを起動しました")
        return JSONResponse({"status": "ok"})
    except Exception as e:
        print(f"❌ 例外発生: {e}")
        return JSONResponse({"status": "error", "reason": str(e)})

@app.post("/connect")
async def connect_to_opponent(request: Request):
    global connected_socket
    try:
        data = await request.json()
        target_ip = data.get("ip")  # 例: 192.168.1.5
        target_name = data.get("name")

        if not target_ip:
            return JSONResponse({"status": "error", "reason": "IPアドレスが指定されていません"})
        
        if not target_name:
            return JSONResponse({"status": "error", "reason": "名前が指定されていません"})

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((target_ip, 10000))  # TCPポート10000で接続

        connected_socket = sock  # 他の処理で使うため保持

        print(f"✅ 接続に成功しました: {target_ip}:10000")
        return JSONResponse({"status": "ok"})

    except Exception as e:
        print(f"❌ 接続失敗: {e}")
        return JSONResponse({"status": "error", "reason": str(e)})

@app.post("/cancel_wait")
async def cancel_wait():
    wait_cancel_event.set()  # スレッドに終了通知
    if wait_thread is not None:
        wait_thread.join()  # ✅ スレッド終了を待つ
    return JSONResponse({"status": "cancelled"})

# WebSocket接続管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print("✅ WebSocket 接続: 現在の接続数 =", len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print("❌ WebSocket 切断: 残り接続数 =", len(self.active_connections))

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/othello")
async def websocket_othello(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"WebSocket受信: {data}")
            response = {
                "type": "true",
                "message": f"受信しました: {data}"
            }
            await websocket.send_text(json.dumps(response))
    except Exception as e:
        print("WebSocket切断s:", e)