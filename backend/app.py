import socket
import threading
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import logging

app = FastAPI()

# CORSの許可設定（Vueとの通信を許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://frontend:3000"
    ],  # 本番環境では限定してください
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# グローバルに接続情報を保持
connected_socket = None

logger = logging.getLogger("uvicorn")

# TCP接続を非同期で待つ関数
def wait_for_client():
    global connected_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', 10000))  # 0.0.0.0:10000 で待ち受け
    server_socket.listen(1)
    print("🔌 TCP接続待機中（ポート10000）...")

    conn, addr = server_socket.accept()
    print(f"✅ 相手と接続されました: {addr}")
    connected_socket = conn  # 他の処理で使用するために保持

    # ※ ゲームロジックなどで受信ループをスタートしてもOK

# /wait エンドポイント
@app.post("/wait")
async def wait_endpoint(request: Request):
    try:
        # 非同期スレッドで TCP 接続を待つ
        thread = threading.Thread(target=wait_for_client, daemon=True)
        thread.start()

        return JSONResponse({"status": "ok"})
    except Exception as e:
        return JSONResponse({"status": "error", "reason": str(e)})

@app.post("/connect")
async def connect_to_opponent(request: Request):
    global connected_socket
    try:
        data = await request.json()
        target_ip = data.get("ip")  # 例: 192.168.1.5

        if not target_ip:
            return JSONResponse({"status": "error", "reason": "IPアドレスが指定されていません"})

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((target_ip, 10000))  # TCPポート10000で接続

        connected_socket = sock  # 他の処理で使うため保持

        print(f"✅ 接続に成功しました: {target_ip}:10000")
        return JSONResponse({"status": "ok"})

    except Exception as e:
        print(f"❌ 接続失敗: {e}")
        return JSONResponse({"status": "error", "reason": str(e)})

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
                "type": "pong",
                "message": f"受信しました: {data}"
            }
            await websocket.send_text(json.dumps(response))
    except Exception as e:
        print("WebSocket切断:", e)