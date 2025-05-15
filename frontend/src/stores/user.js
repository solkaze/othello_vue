// stores/user.js または stores/userStore.js
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  // 自分の情報
  const myName = ref('')
  const myIP = ref('')

  // 相手の情報
  const oppName = ref('')
  const opptIP = ref('')

  // 観戦者一覧（オブジェクトの配列）
  const watchers = ref([]) // 例: [{ name: 'Alice', ip: '192.168.1.2' }, ...]

  // 観戦者追加
  const addWatcher = (name, ip) => {
    watchers.value.push({ name, ip })
  }

  // 観戦者削除
  const removeWatcher = (ip) => {
    watchers.value = watchers.value.filter(w => w.ip !== ip)
  }

  return {
    myName,
    myIP,
    oppName,
    opptIP,
    watchers,
    addWatcher,
    removeWatcher
  }
})
