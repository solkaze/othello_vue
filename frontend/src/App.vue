<template>
  <router-view />
</template>

<script setup>
import { onMounted, onBeforeUnmount } from 'vue'
import { useWebSocketStore } from '@/stores/websocket'

const ws = useWebSocketStore()

// 🔌 ページ離脱時にだけ呼び出される切断処理
const handleUnload = (event) => {
  console.log('📤 ページ離脱に伴う WebSocket 切断要求')
  ws.disconnect({ isUnload: true }) // leave API を叩くようにフラグ付きで呼ぶ
}

onMounted(() => {
  window.addEventListener('beforeunload', handleUnload)
})

onBeforeUnmount(() => {
  window.removeEventListener('beforeunload', handleUnload)
})
</script>

<style>
body {
  font-family: sans-serif;
  margin: 0;
  padding: 0;
}
</style>
