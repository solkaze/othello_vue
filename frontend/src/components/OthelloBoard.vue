<script setup lang="ts">
import { computed } from 'vue'
// Board props
interface Props {
  board: number[][]            // 0 = empty, 1 = black, 2 = white
  valid?: [number, number][]   // 配置可能マスの座標リスト（任意）
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'choose', x: number, y: number): void
}>()

// 高速判定用に Set<string> へ変換
const validSet = computed(() => {
  if (!props.valid) return new Set<string>()
  return new Set(props.valid.map(([x, y]) => `${x},${y}`))
})

function handle(x: number, y: number) {
  emit('choose', x, y)
}
</script>

<template>
  <div class="board">
    <table class="h-full w-full select-none">
      <tr v-for="(row, y) in props.board" :key="y">
        <td v-for="(cell, x) in row" :key="x" @click="handle(x, y)" class="cell">
          <!-- Stones -->
          <div v-if="cell === 1" class="stone stone-black" />
          <div v-else-if="cell === 2" class="stone stone-white" />
          <!-- Valid move indicator -->
          <div
            v-else-if="validSet.has(`${x},${y}`)"
            class="indicator"
          />
        </td>
      </tr>
    </table>
  </div>
</template>

<style scoped>
/* Board container */
.board {
  width: 512px;
  height: 512px;
  background: #378805 url('https://cdn.jsdelivr.net/gh/andrews1022/images@main/wood-texture.png');
  background-size: cover;
  padding: 8px;
  border-radius: 16px;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.25);
}
/* Cells */
.cell {
  width: 56px;
  height: 56px;
  border: 2px solid #2f5d02;
  background-color: rgba(0, 0, 0, 0.02);
  position: relative;
  transition: background-color 0.15s;
  cursor: pointer;
}
.cell:hover {
  background-color: rgba(255, 255, 255, 0.15);
}
/* Stones */
.stone {
  width: 46px;
  height: 46px;
  border-radius: 50%;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  box-shadow: inset 0 2px 4px rgba(255, 255, 255, 0.4), inset 0 -2px 4px rgba(0, 0, 0, 0.4);
}
.stone-black {
  background: radial-gradient(circle at 30% 30%, #444, #000 70%);
}
.stone-white {
  background: radial-gradient(circle at 30% 30%, #fff, #cfcfcf 70%);
}
/* Valid move indicator */
.indicator {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, #ffe066, #d4a600 70%);
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  pointer-events: none; /* clicks pass through */
}
</style>
