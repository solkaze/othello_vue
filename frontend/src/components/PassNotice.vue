<template>
  <!-- 1秒だけ全画面に "パス!!" を表示 -->
  <transition name="fade-scale">
    <div v-if="visible" class="fixed inset-0 flex items-center justify-center pointer-events-none z-[9999]">
      <div class="select-none text-7xl md:text-8xl font-extrabold text-red-600 drop-shadow-[0_4px_4px_rgba(0,0,0,0.4)]">
        パス!!
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
/**
 * PassNotice.vue
 * Props:
 *   visible: boolean — true の間だけ表示
 */
interface Props {
  visible: boolean
}

defineProps<Props>()
</script>

<style scoped>
.fade-scale-enter-active,
.fade-scale-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.fade-scale-enter-from,
.fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.85);
}
</style>
