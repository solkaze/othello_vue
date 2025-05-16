<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount } from 'vue'
import { useOthelloStore } from '@/stores/othello'

const store = useOthelloStore()

function handleUnload () {
  store.leave()    // ソケットをきれいに閉じる
}

onMounted(() => window.addEventListener('beforeunload', handleUnload))
onBeforeUnmount(() => window.removeEventListener('beforeunload', handleUnload))
</script>

<style>
body {
  font-family: sans-serif;
  margin: 0;
  padding: 0;
}
</style>
