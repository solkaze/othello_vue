<!-- GameResultOverlay.vue -->
<template>
  <transition name="fade">
    <div v-if="visible" class="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl p-8 flex flex-col items-center gap-6 w-[min(90%,480px)]">
        <h2 class="text-3xl font-extrabold" :class="winnerColorClass">{{ winnerText }}</h2>

        <p class="text-xl font-semibold flex gap-4">
          <span class="flex items-center gap-1">
            <span class="w-4 h-4 rounded-full bg-black inline-block"></span>
            黒 {{ black }}
          </span>
          <span class="flex items-center gap-1">
            <span class="w-4 h-4 rounded-full bg-white border inline-block"></span>
            白 {{ white }}
          </span>
        </p>

        <!-- ▼ 追加メッセージだけでボタンは無し ▼ -->
        <p class="text-sm text-gray-500 dark:text-gray-400">
          5&nbsp;秒後に自動でロビーへ戻ります…
        </p>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props { visible: boolean; black: number; white: number }
const props = defineProps<Props>()

const winnerText = computed(() => {
  if (props.black > props.white) return '黒の勝利！'
  if (props.white > props.black) return '白の勝利！'
  return '引き分け'
})
const winnerColorClass = computed(() =>
  props.black === props.white
    ? 'text-gray-600 dark:text-gray-300'
    : props.black > props.white
      ? 'text-black dark:text-white'
      : 'text-gray-200 dark:text-gray-100'
)
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity .25s; }
.fade-enter-from,   .fade-leave-to     { opacity: 0; }
</style>
