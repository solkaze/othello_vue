<template>
  <div class="flex flex-col gap-3 p-4 w-56 rounded-2xl shadow-lg bg-slate-800/90 text-slate-100">
    <h2 class="text-xl font-semibold text-center">ゲーム情報</h2>

    <!-- 自分の色 -->
    <div class="flex justify-between items-center">
      <span>あなたの色</span>
      <span class="flex items-center gap-1 font-bold capitalize">
        <span :class="circleClass(playerColor)" class="w-3 h-3 rounded-full inline-block"></span>
        {{ playerColor }}
      </span>
    </div>

    <!-- 石の枚数 -->
    <div class="flex justify-between items-center">
      <span>黒</span>
      <span class="flex items-center gap-1 font-medium">
        <span :class="circleClass('black')" class="w-3 h-3 rounded-full inline-block"></span>
        {{ blackCount }}
      </span>
    </div>
    <div class="flex justify-between items-center">
      <span>白</span>
      <span class="flex items-center gap-1 font-medium">
        <span :class="circleClass('white')" class="w-3 h-3 rounded-full inline-block border border-slate-300"></span>
        {{ whiteCount }}
      </span>
    </div>

    <!-- 手番表示 -->
    <div v-if="!gameOver" class="flex flex-col gap-1 items-center mt-1">
      <div class="flex justify-between w-full items-center">
        <span>現在の手番</span>
        <span class="flex items-center gap-1 font-bold capitalize animate-pulse">
          <span :class="circleClass(turn)" class="w-3 h-3 rounded-full inline-block"></span>
          {{ turn }}
        </span>
      </div>
      <p :class="isMyTurn ? 'text-green-400' : 'text-gray-400'" class="text-sm font-semibold">
        {{ isMyTurn ? 'あなたの手番です' : '相手の手番です' }}
      </p>
    </div>

    <div v-else class="text-center font-bold text-green-400 mt-2">
      ゲーム終了
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, toRefs } from 'vue'

interface Props {
  board: (null | 'black' | 'white')[][]
  playerColor: 'black' | 'white' | null
  turn: 'black' | 'white'
  gameOver?: boolean
}

const props = defineProps<Props>()
const { board, playerColor, turn, gameOver } = toRefs(props)

const blackCount = computed(() => board.value.flat().filter(c => c === 'black').length)
const whiteCount = computed(() => board.value.flat().filter(c => c === 'white').length)

const isMyTurn = computed(() => !gameOver?.value && turn.value === playerColor.value)

function circleClass(color: 'black' | 'white' | null) {
  return color === 'black' ? 'bg-black' : 'bg-white'
}
</script>

<style scoped>
.bg-white {
  background-color: #ffffff;
}
.bg-black {
  background-color: #000000;
}
</style>
