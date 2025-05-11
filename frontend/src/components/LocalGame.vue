<template>
  <div class="local-game">
    <h2>ローカルオセロ</h2>
    <p>現在の手番: <span :class="currentPlayer">{{ currentPlayer === 'B' ? '黒' : '白' }}</span></p>

    <div class="board">
      <div v-for="(row, rowIndex) in board" :key="rowIndex" class="row">
        <div
          v-for="(cell, colIndex) in row"
          :key="colIndex"
          class="cell"
          :class="{
            black: cell === 'B',
            white: cell === 'W',
            hint: isHint(rowIndex, colIndex)
          }"
          @click="handleClick(rowIndex, colIndex)"
        />
      </div>
    </div>
  </div>
  <div class="end">
    <h3>練習を終了する</h3>
    <button @click="exitGame">Exit</button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const SIZE = 8
const board = ref(Array.from({ length: SIZE }, () => Array(SIZE).fill('')))
board.value[3][3] = 'W'
board.value[3][4] = 'B'
board.value[4][3] = 'B'
board.value[4][4] = 'W'

const currentPlayer = ref('B')
const validMoves = ref([])

onMounted(() => {
  updateValidMoves()
})

const handleClick = (row, col) => {
  if (!isValidMove(row, col, currentPlayer.value)) return

  board.value[row][col] = currentPlayer.value
  flipStones(row, col, currentPlayer.value)

  currentPlayer.value = currentPlayer.value === 'B' ? 'W' : 'B'
  updateValidMoves()
}

const isValidMove = (row, col, player) => {
  if (board.value[row][col] !== '') return false
  const opponent = player === 'B' ? 'W' : 'B'
  const directions = [
    [-1, -1], [-1, 0], [-1, 1],
    [0, -1],          [0, 1],
    [1, -1], [1, 0], [1, 1]
  ]
  for (const [dx, dy] of directions) {
    let x = row + dx, y = col + dy
    let foundOpponent = false
    while (x >= 0 && x < SIZE && y >= 0 && y < SIZE && board.value[x][y] === opponent) {
      x += dx
      y += dy
      foundOpponent = true
    }
    if (foundOpponent && x >= 0 && x < SIZE && y >= 0 && y < SIZE && board.value[x][y] === player) {
      return true
    }
  }
  return false
}

const flipStones = (row, col, player) => {
  const opponent = player === 'B' ? 'W' : 'B'
  const directions = [
    [-1, -1], [-1, 0], [-1, 1],
    [0, -1],          [0, 1],
    [1, -1], [1, 0], [1, 1]
  ]
  for (const [dx, dy] of directions) {
    let x = row + dx, y = col + dy
    const toFlip = []
    while (x >= 0 && x < SIZE && y >= 0 && y < SIZE && board.value[x][y] === opponent) {
      toFlip.push([x, y])
      x += dx
      y += dy
    }
    if (toFlip.length && x >= 0 && x < SIZE && y >= 0 && y < SIZE && board.value[x][y] === player) {
      for (const [fx, fy] of toFlip) {
        board.value[fx][fy] = player
      }
    }
  }
}

const updateValidMoves = () => {
  validMoves.value = []
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      if (isValidMove(i, j, currentPlayer.value)) {
        validMoves.value.push([i, j])
      }
    }
  }
}

const isHint = (row, col) => {
  return validMoves.value.some(([r, c]) => r === row && c === col)
}

const exitGame = () => {
  router.push('/')
}
</script>

<style scoped>
.local-game {
  text-align: center;
  margin-top: 30px;
  background-color: #2d2d2d;
  color: #eee;
  font-family: 'Segoe UI', sans-serif;
  padding-bottom: 50px;
}

h2 {
  font-size: 2em;
  margin-bottom: 10px;
}

.board {
  display: inline-block;
  border: 8px solid #7b5e3c;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.6);
  background: repeating-linear-gradient(
    45deg,
    #228B22,
    #228B22 10px,
    #1e7b1e 10px,
    #1e7b1e 20px
  );
  border-radius: 12px;
  overflow: hidden;
}

.row {
  display: flex;
}

.cell {
  width: 60px;
  height: 60px;
  background-color: rgba(34, 139, 34, 0.95);
  border: 1px solid #444;
  position: relative;
  cursor: pointer;
  transition: background-color 0.2s;
}

.cell:hover {
  background-color: #2e8b57;
}

.cell.black::before,
.cell.white::before {
  content: '';
  display: block;
  width: 80%;
  height: 80%;
  border-radius: 50%;
  margin: 10%;
  box-shadow: inset -3px -3px 6px rgba(0, 0, 0, 0.6), inset 2px 2px 5px rgba(255, 255, 255, 0.3);
}

.cell.black::before {
  background: radial-gradient(circle at 30% 30%, #444, #000);
}

.cell.white::before {
  background: radial-gradient(circle at 30% 30%, #eee, #bbb);
}

.cell.hint::after {
    content: '';
    display: block;
    width: 20%;
    height: 20%;
    background-color: yellow;
    border-radius: 50%;
    margin: auto;
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    opacity: 0.7;
}


.black {
  color: #ccc;
  font-weight: bold;
}

.white {
  color: #f5f5f5;
  font-weight: bold;
}

</style>
