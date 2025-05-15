import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'

type Color = 'black' | 'white'
type Status = 'idle' | 'waiting' | 'playing'

export const useOthelloStore = defineStore('othello', () => {
  const router = useRouter()
  const firstTurn = ref<'black' | 'white'>('black')

  /* ----- state ----- */
  const spectators = ref<string[]>([])
  const ws        = ref<WebSocket | null>(null)
  const player    = ref('')
  const opponent  = ref('')
  const room      = ref('')
  const color     = ref<Color>('black')
  const status    = ref<Status>('idle')

  const board = reactive<number[][]>(
    Array.from({ length: 8 }, () => Array(8).fill(0))
  )
  const turn = ref<Color>('black')

  function setFirstTurn(choice: 'random' | 'black' | 'white') {
    firstTurn.value =
      choice === 'random'
        ? (Math.random() < 0.5 ? 'black' : 'white')
        : choice
  }

  /* ----- actions ----- */
  async function nameCheck (name: string) {
    const res = await fetch('http://localhost:10001/name_check', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name })
    })
    return (await res.json()).ok as boolean
  }

  function resetBoardAndStart() {
    /* board 初期化 + turn = firstTurn.value */
  }

  async function connect(name: string, host = 'localhost', role: 'player' | 'spectator' = 'player') {
    if (!(await nameCheck(name))) throw new Error('duplicate')

    player.value = name
    ws.value = new WebSocket(`ws://${host}:10001/ws/othello/${encodeURIComponent(name)}?role=${role}`)

    ws.value.onmessage = (ev) => handle(JSON.parse(ev.data))
    ws.value.onerror   = () => reset()

    status.value = 'waiting'
  }

  function sendMove (x: number, y: number) {
    if (!ws.value) return
    ws.value.send(JSON.stringify({ type: 'move', x, y }))
  }

  function leave () {
    if (ws.value) ws.value.send(JSON.stringify({ type: 'leave' }))
    reset()
  }

  /* ----- private: WS handler ----- */
  function handle (m: any) {
    switch (m.type) {
      case 'wait':
        // 何もしない（待機中）
        break
      case 'start':
        spectators.value = []   
        room.value   = m.room
        opponent.value = m.opponent
        color.value  = m.color
        status.value = 'playing'
        resetBoard()
        router.push('/game')
        break
      case 'move':
        board[m.y][m.x] = m.color === 'black' ? 1 : 2
        turn.value = m.color === 'black' ? 'white' : 'black'
        break
      case 'leave':
        alert('相手が退室しました')
        reset()
        break
      case 'spectator_join':
        spectators.value.push(m.name)
        break
      case 'spectator_leave':
        spectators.value = spectators.value.filter(n => n !== m.name)
        break
      case 'chat':
        // ここでチャット履歴に追加など
        break
    }
  }

  function resetBoard () {
    for (const row of board) row.fill(0)
    // 初期４石などを置きたければここで
    turn.value = 'black'
  }

  function reset () {
    ws.value?.close()
    ws.value   = null
    status.value = 'idle'
    router.push('/')
  }

  return {
    spectators,
    ws, player,
    opponent,
    room,
    color,
    board,
    turn,
    status,
    connect,
    sendMove,
    leave
  }
})
