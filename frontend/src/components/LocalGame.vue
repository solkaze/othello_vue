<script setup lang="ts">
import { computed } from 'vue'
import { useOthelloStore } from '@/stores/othello'
import OthelloBoard from './OthelloBoard.vue'

const store = useOthelloStore()

const myTurn = computed(() => store.turn === store.color)

function choose (x: number, y: number) {
  if (myTurn.value) store.sendMove(x, y)
}
</script>

<template>
  <div class="p-6 flex flex-col gap-4">
    <p>
      あなた: {{ store.color }} /
      相手: {{ store.opponent }} /
      ターン: {{ store.turn }}
    </p>

    <OthelloBoard :board="store.board" @choose="choose" />
    <button class="btn-secondary w-min" @click="store.leave">退出</button>
  </div>
</template>
