<script setup lang="ts">
import { ref, computed, watch, onBeforeUnmount } from 'vue'
import OthelloBoard from '@/components/OthelloBoard.vue'
import { useOthelloStore } from '@/stores/othello'
import InfoPanel from '@/components/InfoPanel.vue'
import GameResultOverlay from '@/components/GameResultOverlay.vue'
import PassNotice from '@/components/PassNotice.vue'

type Stone = 'black' | 'white' | null

/** OthelloGame.vue — online Othello game component (stones are now "black"/"white") */

const store = useOthelloStore()

/* ---------- reactive state ---------- */
const board = ref<Stone[][]>(Array.from({ length: 8 }, () => Array<Stone>(8).fill(null)))
board.value[3][3] = board.value[4][4] = 'white'
board.value[3][4] = board.value[4][3] = 'black'

const turn = ref<'black' | 'white'>('black')
const gameOver = ref(false)
const isSkip = ref(false)

/* ---------- derived ---------- */
const blackCount = computed(() => board.value.flat().filter(c => c === 'black').length)
const whiteCount = computed(() => board.value.flat().filter(c => c === 'white').length)

/* ---------- helpers ---------- */
const DIR: [number, number][] = [
  [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1], [1, -1]
]

const inBoard = (x: number, y: number) => x >= 0 && x < 8 && y >= 0 && y < 8
const opp = (c: 'black' | 'white' | null): 'black' | 'white' => (c === 'black' ? 'white' : 'black') 

/* 勝敗判定用の最終枚数 */
const resultBlack = computed(() => blackCount.value)
const resultWhite = computed(() => whiteCount.value)

const autoLeaveTimer = ref<number | null>(null)

// === 終局 → 5 秒で退室 ======================================
watch(gameOver, (v) => {
  if (v) {
    autoLeaveTimer.value = window.setTimeout(() => {
      if (store.my_color === 'black') store.leave()      // ★ 退室／ロビー遷移
    }, 5000)
  }
})

// コンポーネントが破棄される時にタイマーを掃除
onBeforeUnmount(() => {
  if (autoLeaveTimer.value !== null) clearTimeout(autoLeaveTimer.value)
})
// =============================================================

/* ===== パス通知用フラグ & タイマー =============================== */
const showPassNotice = ref(false)
const passTimer = ref<number | null>(null)

watch(isSkip, (v) => {
  if (v) {
    // 「パス!!」を 1 秒だけ表示
    console.log('パス!!')
    showPassNotice.value = true

    passTimer.value = window.setTimeout(() => {
      showPassNotice.value = false
    }, 1000)                     // ← 1 秒
    isSkip.value = false          // ★ フラグをクリア
  }
})

onBeforeUnmount(() => {
  if (passTimer.value !== null) clearTimeout(passTimer.value)
})
/* ================================================================ */

watch(
  () => store.lastMove,
  mv => {
    if (!mv) return                    // まだ何も来ていない
    const { x, y, color } = mv
    if (color !== store.opp_color) return

    // 既存のロジックを流用して盤面を書き換える
    if (board.value[y][x] === null) {
      const flips = captures(x, y, color)
      if (flips.length) {
        setCell(x, y, color)
        flips.forEach(([fx, fy]) => setCell(fx, fy, color))
      }
    }

    // 手番を進める（ストアでも更新済みだがローカル turn も合わせる）
    advanceTurn()
    console.log('turn:', turn.value)
    // 消し忘れると次の watch が走らないのでクリア
    store.clearLastMove()
  }
)

/* ---------- functions ---------- */
function setCell(x: number, y: number, v: Stone) {
  board.value[y] = [...board.value[y]]   // replace row (for Vue reactivity)
  board.value[y][x] = v
}

function captures(x: number, y: number, c: 'black' | 'white' | null) {
  const out: [number, number][] = []
  const o = opp(c)
  for (const [dx, dy] of DIR) {
    let nx = x + dx, ny = y + dy
    const line: [number, number][] = []
    while (inBoard(nx, ny) && board.value[ny][nx] === o) {
      line.push([nx, ny])
      nx += dx; ny += dy
    }
    if (inBoard(nx, ny) && board.value[ny][nx] === c && line.length) out.push(...line)
  }
  return out
}

function hasMove(c: 'black' | 'white') {
  for (let y = 0; y < 8; y++)
    for (let x = 0; x < 8; x++)
      if (board.value[y][x] === null && captures(x, y, c).length) return true
  return false
}

/* ---------- main actions ---------- */
function placeStone(x: number, y: number) {
  if (turn.value !== store.my_color) return
  if (gameOver.value) return
  if (board.value[y][x] !== null) return
  const flips = captures(x, y, turn.value)
  if (!flips.length) return
  setCell(x, y, turn.value)
  flips.forEach(([fx, fy]) => setCell(fx, fy, turn.value))
  advanceTurn()
  store.ws?.send(
    JSON.stringify({
      type: 'move',
      name: store.player,
      x: x,
      y: y,
      color: store.my_color,
      isSkip: isSkip.value
    })
  )
}

function advanceTurn() {
  const n = opp(turn.value)
  if (hasMove(n)) turn.value = n
  else if (!hasMove(turn.value)) gameOver.value = true
  else {
    isSkip.value = true
    console.log('skip')
  }
}

/* ---------- valid moves (for indicator) ---------- */
const validMoves = computed<[number, number][]>(() =>
  board.value.flatMap((row, y) =>
    row.flatMap((cell, x) => (cell === null && captures(x, y, turn.value).length ? [[x, y] as [number, number]]  : []))
  )
)

</script>

<template>
  <div class="min-h-screen bg-gradient-to-b from-orange-50 to-orange-200 flex items-center justify-center p-4">
    <div class="flex flex-col items-center gap-4 p-4">

      <h1 class="text-xl font-bold gap-3 p-4 rounded-2xl shadow-lg bg-slate-100/90 text-slate-900">
        {{ store.player }} vs {{ store.opponent || '???' }}
      </h1>

      <!-- ===== ここを flex にして Board と InfoPanel を横並び ===== -->
      <div class="flex gap-6">
        <!-- 盤面 -->
        <OthelloBoard
          :board="board"
          :valid="validMoves"
          @place="placeStone"
        />

        <!-- インフォパネル -->
        <InfoPanel
          :board="board"
          :player-color="store.my_color"
          :turn="turn"
          :game-over="gameOver"
        />
      </div>
      <!-- =========================================================== -->

      <button class="mt-6 px-40 py-4 rounded-3xl bg-red-500 text-white" @click="store.leave">
        退室
      </button>
    </div>
  </div>
  <GameResultOverlay
    :visible="gameOver"
    :black="blackCount"
    :white="whiteCount"
  />
  <PassNotice :visible="showPassNotice" />
</template>

<style scoped>
</style>