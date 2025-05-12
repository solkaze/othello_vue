<template>
  <div class="connect-screen">
    <h2>オセロ 対戦接続</h2>
    <div class="card-container">
      <!-- 接続する側 -->
      <div class="card">
        <h3>対戦相手に接続</h3>
        <input
          v-model="ipAddress"
          type="text"
          placeholder="相手のIPアドレスを入力"
        />
        <button @click="connectToOpponent">接続する</button>
        <button @click="connectToOpponent">試合を観戦</button>
      </div>

      <!-- 接続を待機する側 -->
      <div class="card">
        <h3>接続を待機</h3>
        <button @click="waitForConnection">待機開始</button>
        <p v-if="isWaiting">接続を待機中です...</p>
        <button @click="cancelWait" :disabled="!isWaiting">キャンセル</button>
      </div>
      <div class="card">
        <h3>一人で練習</h3>
        <button @click="startLocalGame">ゲーム開始</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const ipAddress = ref('')
const isWaiting = ref(false)
const router = useRouter()

let ws = null;

onMounted(() => {
  setupWebSocket()
})

const setupWebSocket = () => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    console.log("✅ すでにWebSocket接続済みです")
    return
  }

  ws = new WebSocket('ws://localhost:10001/ws/othello')

  ws.onopen = () => {
    console.log("✅ WebSocket接続確立")
    ws.send("hello vue")
  }

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    console.log("📩 メッセージ受信:", data)
  }

  ws.onclose = () => {
    console.log("🔌 WebSocket切断")
  }

  ws.onerror = (err) => {
    console.error("❌ WebSocketエラー:", err)
  }
}

// WebSocket を明示的に閉じる関数
const closeWebSocket = () => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.close()
    ws = null
  }
}

const connectToOpponent = () => {
  fetch(`http://localhost:10001/connect`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ip: ipAddress.value })
  })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'ok') {
        alert('接続成功しました')
        setupWebSocket()
        router.push('/game')
      } else {
        alert('接続失敗: ' + data.reason)
      }
    })
    .catch(err => {
      console.error(err)
      alert('接続に失敗しました')
    })
}

let interval = null;
let timeout = null;

const waitForConnection = () => {
  isWaiting.value = true

  const timeoutDuration = 10000;  // 30秒

  timeout = setTimeout(() => {
    alert('接続タイムアウトしました');
    isWaiting.value = false;
  }, timeoutDuration);

  fetch(`http://localhost:10001/wait`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ role: 'host' })
  })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'ok') {
        // 接続確認ポーリング
        interval = setInterval(() => {
          fetch(`http://localhost:10001/status`)
            .then(res => res.json())
            .then(status => {
              if (status.connected) {
                clearInterval(interval);
                clearTimeout(timeout);
                alert('相手が接続しました');
                setupWebSocket();
                router.push('/game');
              } else if (status.expired) {
                clearInterval(interval)
              } else if (status.cancelled) {
                clearInterval(interval)
              }
            })
            .catch(err => {
              console.error('ステータス確認エラー:', err)
            })
        }, 1000)
      } else {
        alert('待機失敗: ' + data.reason)
      }
    })
    .catch(err => {
      console.error(err)
      alert('待機処理中にエラーが発生しました')
    })
}

// 待機をやめるボタン
const cancelWait = () => {
  clearInterval(interval)
  clearTimeout(timeout)
  fetch('http://localhost:10001/cancel_wait', { method: 'POST' })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'cancelled') {
        isWaiting.value = false
      }
    })
    .catch(err => {
      console.error('キャンセル中にエラー:', err)
    })
}

const startLocalGame = () => {
  closeWebSocket()
  router.push('/local')
}
</script>

<style scoped>
.connect-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 40px;
  margin-top: 50px;
  color: var(--text-color);
}

.card-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 40px;
  margin-top: 30px;
  flex-wrap: wrap;
}


.card {
  flex: 1 1 calc(50% - 40px);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 2em;
  max-width: 400px;
  min-width: 350px;
  box-sizing: border-box;
  background-color: var(--card-bg);
  transition: background-color 0.5s border-color 0.3s;
  box-shadow: 0 2px 6px rgba(120, 120, 120, 10.5);
}

input, button {
  width: 100%;
  padding: 0.5em;
  font-size: 1em;
  margin-top: 0.5em;
  box-sizing: border-box;
}

button {
  padding: 0.5em 1em;
  font-size: 1em;
}

p {
  margin-top: 1em;
  color: var(--text-muted);
}
</style>

