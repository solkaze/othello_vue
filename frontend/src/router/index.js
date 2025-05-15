// src/router/index.js
import { createRouter, createWebHistory } from "vue-router"
import ConnectScreen from "@/components/ConnectScreen.vue"
import OthelloBoard from "@/components/OthelloBoard.vue"
import LocalGame from "@/components/LocalGame.vue"
import WaittingRoom from "@/components/WaittingRoom.vue" 
import DebugGame from '@/components/DebugGame.vue';

const routes = [
  { path: "/", component: ConnectScreen },
  { path: "/game", component: OthelloBoard },
  { path: "/local", component: LocalGame },
  { path: "/wait", component: WaittingRoom },
  { path: '/debug', component: DebugGame },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
