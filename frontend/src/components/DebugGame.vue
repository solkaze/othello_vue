<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import OthelloBoard from './OthelloBoard.vue'

/** DebugGame.vue — self-contained offline Othello board */

/* ---------- reactive state ---------- */
const board = ref<number[][]>(Array.from({ length: 8 }, () => Array(8).fill(0)))
board.value[3][3] = board.value[4][4] = 2 // W W
board.value[3][4] = board.value[4][3] = 1 // B B

const turn = ref<1 | 2>(1)        // 1 = black, 2 = white
const gameOver = ref(false)

/* ---------- derived ---------- */
const blackCount = computed(() => board.value.flat().filter(c => c === 1).length)
const whiteCount = computed(() => board.value.flat().filter(c => c === 2).length)

/* ---------- helpers ---------- */
const DIR: [number, number][] = [
  [1, 0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1],[0,-1],[1,-1]
]
const inBoard = (x:number,y:number)=>x>=0&&x<8&&y>=0&&y<8
const opp = (c:1|2):1|2 => (c===1?2:1)

function setCell(x:number,y:number,v:0|1|2){
  board.value[y] = [...board.value[y]]   // replace row
  board.value[y][x] = v
}

function captures(x:number,y:number,c:1|2){
  const out:[number,number][]=[]
  const o = opp(c)
  for(const [dx,dy] of DIR){
    let nx=x+dx, ny=y+dy
    const line:[number,number][]=[]
    while(inBoard(nx,ny)&&board.value[ny][nx]===o){line.push([nx,ny]);nx+=dx;ny+=dy}
    if(inBoard(nx,ny)&&board.value[ny][nx]===c&&line.length) out.push(...line)
  }
  return out
}

function hasMove(c:1|2){
  for(let y=0;y<8;y++) for(let x=0;x<8;x++)
    if(board.value[y][x]===0 && captures(x,y,c).length) return true
  return false
}

/* ---------- main actions ---------- */
function placeStone(x:number,y:number){
  console.log("x: " + x + "y: " + y)
  if(gameOver.value) return
  if(board.value[y][x]!==0) return
  const flips=captures(x,y,turn.value);
  if(!flips.length) return
  setCell(x,y,turn.value)
  flips.forEach(([fx,fy])=>setCell(fx,fy,turn.value))
  advanceTurn()
}


function advanceTurn(){
  const n=opp(turn.value)
  if(hasMove(n)) turn.value=n
  else if(!hasMove(turn.value)) gameOver.value=true
}

// DebugGame.vue 内
const validMoves = computed<[number, number][]>(() =>
  board.value.flatMap((row, y) =>
    row.flatMap((cell, x) =>
      cell === 0 && captures(x, y, turn.value).length
        ? [[x, y] as [number, number]]        // ←★ここでタプルにキャスト
        : []
    )
  )
)


/* ---------- navigation ---------- */
const router=useRouter()
const exit=()=>router.push('/')
</script>

<template>
  <div class="min-h-screen bg-slate-100 flex flex-col items-center gap-6 py-6">
    <h2 class="text-2xl font-semibold">ローカルデバッグ</h2>

    <div class="flex gap-8 items-center text-lg">
      <div>黒: {{ blackCount }}</div>
      <div>白: {{ whiteCount }}</div>
      <div v-if="!gameOver">
        ターン: <span :class="turn===1?'text-black':'text-gray-600'">{{ turn===1?'黒':'白' }}</span>
      </div>
      <div v-else>ゲーム終了</div>
    </div>

    <OthelloBoard
      :board="board"
      :valid="validMoves"
      @choose="placeStone" 
    />

    <button class="btn-secondary mt-6" @click="exit">終了</button>
  </div>
</template>

<style scoped>
.btn-secondary{@apply px-4 py-2 border border-gray-400 text-gray-700 hover:bg-gray-50 rounded-lg transition;}
</style>