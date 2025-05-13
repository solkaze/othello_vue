// src/stores/websocket.js
import { defineStore } from 'pinia'

export const useWebSocketStore = defineStore('websocket', {
  state: () => ({
    socket: null,
    isConnected: false,
    messages: [],
  }),

  actions: {
    connect(url = 'ws://localhost:10001/ws/othello') {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        console.log("✅ すでにWebSocket接続済みです")
        return
      }

      this.socket = new WebSocket(url)

      this.socket.onopen = () => {
        this.isConnected = true
        console.log('✅ WebSocket接続確立')
        this.socket.send('hello vue')
      }

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          console.log('📩 メッセージ受信:', data)
          this.messages.push(data)
        } catch (e) {
          console.warn('メッセージのJSON解析に失敗:', event.data)
        }
      }

      this.socket.onclose = () => {
        console.log('🔌 WebSocket切断')
        this.isConnected = false
        this.socket = null
      }

      this.socket.onerror = (error) => {
        console.error('❌ WebSocketエラー:', error)
      }
    },

    send(message) {
      if (this.isConnected && this.socket) {
        this.socket.send(message)
      } else {
        console.warn('⚠️ WebSocketが未接続のため送信できません')
      }
    },

    disconnect() {
      if (this.socket) {
        this.socket.close()
        this.socket = null
        this.isConnected = false
      }
    },
  },
})
