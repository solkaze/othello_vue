// src/router/index.js
import { createRouter, createWebHistory } from "vue-router"
import ConnectScreen from "@/components/ConnectScreen.vue"
import OthelloBoard from "@/components/OthelloBoard.vue"
import LocalGame from "@/components/LocalGame.vue"

const routes = [
  { path: "/", component: ConnectScreen },
  { path: "/game", component: OthelloBoard },
  { path: "/local", component: LocalGame }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
