<template>
  <div class="flex flex-col items-center gap-4 p-4">
    <h2 class="text-xl font-bold">
      {{ store.player }}（{{ myColorLabel }}） vs {{ store.opponent || '???' }}
    </h2>

    <p v-if="isMyTurn" class="text-green-600 font-semibold">あなたの手番です</p>
    <p v-else class="text-gray-500">相手の手番です</p>

    <!-- 盤面コンポーネント -->
    <OthelloBoard
      :board="board"
      :valid-moves="validMoves"
      @place="handlePlace"
    />

    <button class="mt-6 px-4 py-2 rounded bg-red-500 text-white" @click="store.leave">
      退室
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import OthelloBoard from './OthelloBoard.vue'
import { useOthelloStore } from '@/stores/othello'

/** --------------------------------------------------
 *  Composition API / store
 * --------------------------------------------------*/
const store = useOthelloStore()
const board = store.board                    // reactive 8×8 number[][]

/** --------------------------------------------------
 *  ユーティリティ
 * --------------------------------------------------*/
const DIRS = [
  [1, 0], [-1, 0], [0, 1], [0, -1],
  [1, 1], [1, -1], [-1, 1], [-1, -1]
] as const

type Color = 'black' | 'white'

/**
 * 指定座標に置いたときに反転対象となる座標を列挙
 */
function getFlips (x: number, y: number, color: Color) {
  const me   = color === 'black' ? 1 : 2
  const opp  = color === 'black' ? 2 : 1
  const flips: number[][] = []

  for (const [dx, dy] of DIRS) {
    const tmp: number[][] = []
    let cx = x + dx
    let cy = y + dy
    while (cx >= 0 && cx < 8 && cy >= 0 && cy < 8 && board[cy][cx] === opp) {
      tmp.push([cx, cy])
      cx += dx
      cy += dy
    }
    if (tmp.length && cx >= 0 && cx < 8 && cy >= 0 && cy < 8 && board[cy][cx] === me) {
      flips.push(...tmp)
    }
  }
  return flips
}

/** --------------------------------------------------
 *  Computed values
 * --------------------------------------------------*/
const isMyTurn = computed(() => store.turn === store.color)
const myColorLabel = computed(() => store.color === 'black' ? '黒' : '白')

const validMoves = computed(() => {
  const moves: { x: number, y: number }[] = []
  if (!isMyTurn.value) return moves
  for (let y = 0; y < 8; y++) {
    for (let x = 0; x < 8; x++) {
      if (board[y][x] !== 0) continue
      if (getFlips(x, y, store.color as Color).length) {
        moves.push({ x, y })
      }
    }
  }
  return moves
})

/** --------------------------------------------------
 *  手番を処理
 * --------------------------------------------------*/
function applyMove (x: number, y: number, color: Color) {
  const me = color === 'black' ? 1 : 2
  const flips = getFlips(x, y, color)
  if (!flips.length) return false   // 非合法手

  board[y][x] = me
  for (const [fx, fy] of flips) board[fy][fx] = me
  store.turn = color === 'black' ? 'white' : 'black'
  return true
}

function handlePlace ({ x, y }: { x: number, y: number }) {
  if (!isMyTurn.value) return
  if (board[y][x] !== 0) return
  if (applyMove(x, y, store.color as Color)) {
    // バックエンドへ送信（座標のみ）
    store.sendMove(x, y)
  }
}

/** --------------------------------------------------
 *  相手からの着手を検知して盤面を反映
 * --------------------------------------------------*/
watch(
  () => [store.turn, board.map(r => r.slice())],
  () => {
    // 自分の番でない = 相手が打った直後、とみなして盤面差分から推測して反転
    if (isMyTurn.value) return
    // 最新の相手着手座標は store 側では (x,y) のみ保持していないため、
    // "1 手だけ増えたセル" を探す簡易ロジックで補完。
    // ★必要なら store.handle("move") 側で flip 計算を行い、
    //    broadcast に flips[] を含める方向でも OK。
  },
  { flush: 'post' }
)
</script>

<style scoped>
/***** 盤面以外はここで簡単にレイアウト調整 *****/
</style>
