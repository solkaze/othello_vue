// src/stores/websocket.js
import { defineStore } from 'pinia'

export const useWebSocketStore = defineStore('websocket', {
  state: () => ({
    socket: null,
    isConnected: false,
    messages: [],
  }),

  actions: {
    connect(url) {
      if (this.socket) return

      this.socket = new WebSocket(url)

      this.socket.onopen = () => {
        this.isConnected = true
        console.log('WebSocket connected')
      }

      this.socket.onmessage = (event) => {
        const data = event.data
        this.messages.push(data)
        console.log('WebSocket message received:', data)
      }

      this.socket.onclose = () => {
        this.isConnected = false
        this.socket = null
        console.log('WebSocket disconnected')
      }

      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error)
      }
    },

    send(message) {
      if (this.isConnected && this.socket) {
        this.socket.send(message)
      } else {
        console.warn('WebSocket is not connected.')
      }
    },

    disconnect() {
      if (this.socket) {
        this.socket.close()
      }
    },
  },
})