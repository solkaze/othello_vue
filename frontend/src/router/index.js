// src/router/index.js
import { createRouter, createWebHistory } from "vue-router"
import ConnectScreen from "@/components/ConnectScreen.vue"
import WaittingRoom from "@/components/WaittingRoom.vue" 
import DebugGame from '@/components/DebugGame.vue';
import OthelloGame from '@/components/OthelloGame.vue'

const routes = [
  { path: "/", component: ConnectScreen },
  { path: "/game", component: OthelloGame },
  { path: "/wait", component: WaittingRoom },
  { path: "/debug", component: DebugGame },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
