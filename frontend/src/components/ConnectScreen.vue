<script setup lang="ts">
import { ref } from 'vue'
import { useOthelloStore } from '@/stores/othello'
import { useRouter } from 'vue-router'

const store = useOthelloStore()
const router = useRouter()

const name = ref('')
const network = ref('localhost')
const roomId = ref('')
const errorMsg = ref('')

async function connect(
  role: 'player' | 'spectator',
  isHost: boolean = false
) {
  errorMsg.value = ''
  if (!name.value) {
    errorMsg.value = '名前を入力してください'
    return
  }
  if (!isHost && !roomId.value) {
    errorMsg.value = 'ROOM_IDを入力してください'
    return
  } else if (isHost && roomId.value) {
    errorMsg.value = 'ROOM_IDは入力しないでください'
    return
  }
  try {
    await store.connect(name.value, network.value, role, isHost, roomId.value) // ★ store 側で (name, network, role) に対応させる
    if (role === 'player') {
      router.push('/wait')
    } else {
      router.push('/spectate') // 観戦画面を別途用意 今はまだ作っていない
    }
  } catch (e: any) {
    errorMsg.value = '接続に失敗しました: ' + (e?.message ?? '')
  }
}

function debugLocal() {
  router.push('/debug') // ローカルデバッグ用ルート
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-b from-sky-50 to-sky-200 flex items-center justify-center p-4">
    <div class="w-full max-w-md bg-white/80 backdrop-blur-lg rounded-2xl shadow-lg p-8 space-y-6">
      <h1 class="text-2xl font-semibold text-center">オンラインオセロ</h1>

      <div class="space-y-4">
        <label class="block">
          <span class="text-sm font-medium text-gray-700">名前</span>
          <input v-model="name" type="text" placeholder="name" class="mt-1 w-full rounded-lg border-gray-300 focus:ring-2 focus:ring-sky-400" />
        </label>

        <label class="block">
          <span class="text-sm font-medium text-gray-700">接続先 IP / ホスト名</span>
          <input v-model="network" type="text" placeholder="localhost または 192.168.0.42" class="mt-1 w-full rounded-lg border-gray-300 focus:ring-2 focus:ring-sky-400" />
        </label>

        <label class="block">
          <span class="text-sm font-medium text-gray-700">部屋ID(接続時使用)</span>
          <input v-model="roomId" type="text" placeholder="XXXXX" class="mt-1 w-full rounded-lg border-gray-300 focus:ring-2 focus:ring-sky-400" />
        </label>

        <p v-if="errorMsg" class="text-sm text-red-600">{{ errorMsg }}</p>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <button @click="connect('player', true)" class="col-span-2 btn-primary">ホストとして接続</button>
        <button @click="connect('player')" class="col-span-2 btn-secondary">対戦相手として接続</button>
        <button @click="connect('spectator')" class="btn-tertiary">観戦者として接続</button>
        <button @click="debugLocal" class="btn-outline">ローカルデバッグ</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.btn-primary {
  @apply w-full px-4 py-2 bg-sky-500 hover:bg-sky-600 text-white font-medium rounded-lg shadow transition;
}
.btn-secondary {
  @apply w-full px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white font-medium rounded-lg shadow transition;
}
.btn-tertiary {
  @apply w-full px-4 py-2 bg-orange-500 hover:bg-orange-600 text-white font-medium rounded-lg shadow transition;
}
.btn-outline {
  @apply w-full px-4 py-2 border border-gray-400 text-gray-700 hover:bg-gray-50 rounded-lg transition;
}
</style>
