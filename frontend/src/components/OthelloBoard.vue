<template>
  <div class="board">
    <div
    v-for="(row, rowIndex) in board"
    :key="rowIndex"
    class="row"
    >
    <div
        v-for="(cell, colIndex) in row"
        :key="colIndex"
        class="cell"
        :class="{
          black: cell === 'B',
          white: cell === 'W',
          hint: isHint(rowIndex, colIndex)
        }"
        @click="placeStone(rowIndex, colIndex)"
    />
    </div>
  </div>
</template>

<script setup>
  import { ref } from 'vue'
  import './OthelloBoard.css'

  const SIZE = 8
  const board = ref(Array.from({ length: SIZE }, () => Array(SIZE).fill('')))
  // 初期配置
  board.value[3][3] = 'W'
  board.value[3][4] = 'B'
  board.value[4][3] = 'B'
  board.value[4][4] = 'W'
  const currentPlayer = ref('B')
  const validMove = ref([])

  updateValidMove()

  function updateValidMove() {
    validMove.value = []
    for (let i = 0; i < SIZE; ++i) {
      for (let j = 0; j < SIZE; ++j) {
        if (isValidMove(i, j, currentPlayer.value)) {
          validMove.value.push([i, j])
        }
      }
    }
  }

  function isValidMove(row, col, player) {
    if (board.value[row][col] !== '') return false

    const opponent = player === 'B' ? 'W' : 'B'
    const directions = [
      [-1, -1], [-1, 0], [-1, 1],
      [0, -1],          [0, 1],
      [1, -1],  [1, 0], [1, 1]
    ]

    for (const [dx, dy] of directions) {
      let x = row + dx
      let y = col + dy
      let hasOpponentBetween = false

      while (
        x >= 0 && x < SIZE &&
        y >= 0 && y < SIZE &&
        board.value[x][y] === opponent
      ) {
        x += dx
        y += dy
        hasOpponentBetween = true
      }

      if (
        hasOpponentBetween &&
        x >= 0 && x < SIZE &&
        y >= 0 && y < SIZE &&
        board.value[x][y] === player
      ) {
        return true
      }
    }

    return false
  }

  function placeStone(row, col) {
    if (!isValidMove(row, col, currentPlayer.value)) return

    board.value[row][col] = currentPlayer.value
    flipStones(row, col, currentPlayer.value)
    currentPlayer.value = currentPlayer.value === 'B' ? 'W' : 'B'
    updateValidMove()
  }

  function flipStones(row, col, player) {
    const opponent = player === 'B' ? 'W' : 'B'
    const directions = [
      [-1, -1], [-1, 0], [-1, 1],
      [0, -1],          [0, 1],
      [1, -1],  [1, 0], [1, 1]
    ]

    for (const [dx, dy] of directions) {
      let x = row + dx
      let y = col + dy
      const cellsToFlip = []

      while (
          x >= 0 && x < SIZE &&
          y >= 0 && y < SIZE &&
          board.value[x][y] === opponent
        ) {
          cellsToFlip.push([x, y])
          x += dx
          y += dy
        }

        if (
          cellsToFlip.length > 0 &&
          x >= 0 && x < SIZE &&
          y >= 0 && y < SIZE &&
          board.value[x][y] === player
        ) {
        for (const [fx, fy] of cellsToFlip) {
          board.value[fx][fy] = player
        }
      }
    }
  }

  function isHint(row, col) {
    return validMove.value.some(([r, c]) => r === row && c === col)
  }

</script>
