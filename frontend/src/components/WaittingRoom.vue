<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useOthelloStore } from '@/stores/othello'
import { useRouter } from 'vue-router'

const store = useOthelloStore()
const router = useRouter()

// Spectators 配列が store に無いとレンダリングで落ちるため、
// ???? なら空配列を返す安全ラッパーを用意
const spectators = computed(() => store.spectators ?? [])

// ラジオ選択: 'random' | 'black' | 'white'
// (自分が黒 ＝ 先手)
const firstTurn = ref<'random' | 'me' | 'opp'>('random')

// プレイヤーが両方いるか
const ready = computed(() => !!store.opponent)

// 対戦成立したら opponent/name が埋まる → UI 更新
watch(
  () => store.opponent,
  (v) => {
    if (v) {
      // 両者揃ったがゲーム開始はまだ
    }
  },
)

// サーバーから途中で leave が来たとき
// onMounted(() => {
//   store.ws?.addEventListener('message', (ev) => {
//     const m = JSON.parse(ev.data)
//     if (m.type === 'leave') {
//       alert('相手が退室しました')
//       router.push('/')
//     }
//   })
// })

function startGame () {
  if (!store.ws) return        // 念のため null ガード
  store.setFirstTurn(firstTurn.value)   // ラジオで選んだ値を確定
  store.ws?.send(
    JSON.stringify({
      type: 'start_request',
      first: store.firstTurn    // 'me' | 'opp'
    })
  )
}

function cancel() {
  console.log("waittingRoom_leave")
  store.leave(4000)
  router.push('/')
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-b from-emerald-50 to-emerald-200 flex items-center justify-center p-4">
    <div class="w-full max-w-lg bg-white/80 backdrop-blur-lg rounded-2xl shadow-lg p-8 space-y-6">
      <h2 class="text-xl font-semibold text-center">接続待機中</h2>
      <h3 class="text-center">部屋ID: {{ store.room }}</h3>

      <!-- プレイヤー一覧 -->
      <div class="flex justify-around py-4">
        <div class="text-center">
          <p class="font-medium">あなた</p>
          <p class="text-lg">{{ store.player }}</p>
        </div>
        <div class="text-center">
          <p class="font-medium">相手</p>
          <p class="text-lg" v-if="store.opponent">{{ store.opponent }}</p>
          <p class="text-gray-400" v-else>接続待ち…</p>
        </div>
      </div>

      <!-- 観戦者一覧 -->
      <div>
        <p class="font-medium mb-1">観戦者</p>
        <div class="flex flex-wrap gap-2">
          <span v-for="s in store.spectators" :key="s" class="px-2 py-1 bg-gray-200 rounded-lg text-sm">{{ s }}</span>
          <span v-if="store.spectators.length === 0" class="text-gray-400">なし</span>
        </div>
      </div>

      <!-- 先手選択 -->
      <div class="space-y-2 border-t pt-4">
        <p class="font-medium">先手を決める</p>
        <div class="flex gap-4">
          <label class="flex items-center gap-1 cursor-pointer">
              <input
                  type="radio"
                  id="random"
                  value="random"
                  v-model="firstTurn"
                  :disabled="!store.isHost"
                />
            ランダム
          </label>
          <label class="flex items-center gap-1 cursor-pointer">
            <input
              type="radio"
              id="me"
              value="me"
              v-model="firstTurn"
              :disabled="!store.isHost"
            />
            あなた
          </label>
          <label class="flex items-center gap-1 cursor-pointer" :class="{ 'opacity-50 cursor-not-allowed': !store.opponent }">
            <input
              type="radio"
              id="opp"
              value="opp"
              v-model="firstTurn"
              :disabled="!store.isHost"
            />
            相手
          </label>
        </div>
      </div>

      <!-- ボタン -->
      <div class="grid grid-cols-2 gap-4 pt-2">
        <button class="btn-secondary" @click="cancel">キャンセル</button>
        <button class="btn-primary" :class="{ 'opacity-50': !ready }" :disabled="!ready" @click="startGame">スタート</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.btn-primary {
  @apply w-full px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white font-medium rounded-lg shadow transition;
}
.btn-secondary {
  @apply w-full px-4 py-2 border border-gray-400 text-gray-700 hover:bg-gray-50 rounded-lg transition;
}
</style>
