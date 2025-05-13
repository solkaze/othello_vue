<template>
  <div class="waiting-room">
    <h2>接続者一覧</h2>
    <p v-if="isCancel">キャンセルしています...</p>
    <p v-else>対戦相手の接続を待っています...</p>
    <ul>
      <!-- <li v-for="(client, index) in connectedClients" :key="index">
        {{ client.name }} - {{ client.ip }}
      </li> -->
    </ul>
    <button @click="cancelWait">キャンセルして戻る</button>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router'

const router = useRouter()
const isWaiting = ref(false)
let interval = null;
const isCancel = ref(false);

onMounted(() => {
  waitForConnection()
})

onUnmounted(() => {
  if (interval) clearInterval(interval)
})

const waitForConnection = () => {
  isWaiting.value = true

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
}
</style>