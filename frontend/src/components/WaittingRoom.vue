<template>
  <div class="waiting-room">
    <h2>接続者一覧</h2>
    <p v-if="isCancel">キャンセルしています...</p>
    <p v-else>対戦相手の接続を待っています...</p>

    <div class="player">
      <h3>プレイヤー</h3>
      <div class="players">
        <div class="player-box">
          <p class="role-label">● 黒</p>
          <p class="player-name">{{ blackPlayer?.name || '接続待ち...' }}</p>
        </div>
        <div class="player-box">
          <p class="role-label">○ 白</p>
          <p class="player-name">{{ whitePlayer?.name || '接続待ち...' }}</p>
        </div>
      </div>
    </div>

    <div class="audience">
      <h3>観戦者</h3>
      <ul>
        <li v-for="(client, index) in audienceList" :key="index" v-if="index < 10">
          {{ client.name }} - {{ client.ip }}
        </li>
      </ul>
    </div>

    <button @click="cancelWait">キャンセルして戻る</button>
  </div>
</template>



<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';

const router = useRouter()
const isWaiting = ref(false)
let interval = null;
const isCancel = ref(false);
const store = useUserStore();
const blackPlayer = computed(() => ({
  name: store.myName,
  ip: store.myIP
}))

const whitePlayer = computed(() => ({
  name: store.oppName,
  ip: store.oppIP
}))
// 仮の観戦者データ
const audienceList = ref([
  { name: '観戦者1', ip: '192.168.0.1' },
  { name: '観戦者2', ip: '192.168.0.2' },
  { name: '観戦者3', ip: '192.168.0.3' },
  { name: '観戦者4', ip: '192.168.0.4' },
  { name: '観戦者5', ip: '192.168.0.5' },
  { name: '観戦者6', ip: '192.168.0.6' },
  { name: '観戦者7', ip: '192.168.0.7' },
  { name: '観戦者8', ip: '192.168.0.8' },
  { name: '観戦者9', ip: '192.168.0.9' },
  { name: '観戦者10', ip: '192.168.0.10' },
  { name: '観戦者11', ip: '192.168.0.11' }, // これは表示されない
]);

onMounted(() => {
  waitForConnection()
  console.log(store.myName)
})

onUnmounted(() => {
  if (interval) clearInterval(interval)
})

const waitForConnection = () => {

  fetch(`http://localhost:10001/wait`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ role: 'host' })
  })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'ok') {
        interval = setInterval(() => {
          fetch(`http://localhost:10001/status`)
            .then(res => res.json())
            .then(status => {
              if (status.connected) {
                clearInterval(interval);
                router.push('/game');
              } else if (status.cancelled) {
                console.log('キャンセルされました')
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

const cancelWait = () => {
  isCancel.value = true
  clearInterval(interval)
  fetch('http://localhost:10001/cancel_wait', { method: 'POST' })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'cancelled') {
        isWaiting.value = false
        router.push('/')
      }
    })
    .catch(err => {
      console.error('キャンセル中にエラー:', err)
    })
};
</script>


<style scoped>
.waiting-room {
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

.players {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.player-box {
  flex: 1;
  padding: 20px;
  border: 2px dashed #888;
  border-radius: 12px;
  min-height: 100px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.role-label {
  font-weight: bold;
  font-size: 18px;
  margin-bottom: 8px;
}

.player-name {
  font-size: 16px;
}

.audience ul {
  list-style-type: none;
  padding: 0;
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 10px;
}

.audience li {
  padding: 6px 0;
}

</style>
