import { defineStore } from 'pinia'
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'

type Color = 'black' | 'white' | null
type Status = 'idle' | 'waiting' | 'playing'


export const useOthelloStore = defineStore('othello', () => {
  const router = useRouter()
  const firstTurn = ref('')

  /* ----- state ----- */
  const spectators = ref<string[]>([])
  const ws         = ref<WebSocket | null>(null)
  const player     = ref<string>('')              // 自分の名前
  const opponent   = ref<string>('')              // 相手の名前
  const network    = ref<string>('localhost')
  const room       = ref('')
  const my_color   = ref<Color>('black')
  const opp_color  = ref<Color>('white')
  const status     = ref<Status>('idle')
  const isHost     = ref<boolean>(false)
  
  const turn = ref<Color>('black')

  // --- state ---------------------------------
  const lastMove = ref<{ x: number; y: number; color: 'black' | 'white' | null } | null>(null)


  function setFirstTurn(choice: 'random' | 'me' | 'opp') {
    firstTurn.value =
      choice === 'random'
        ? (Math.random() < 0.5 ? player.value : opponent.value)
        : choice === 'me' ? player.value : opponent.value
  }

  /* ----- actions ----- */
  async function nameCheck (name: string, room_id: string) {
    const res = await fetch(`http://${network.value}:10001/name_check`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, room_id })
    })
    return (await res.json()).ok as boolean
  }

  async function roomCheck (room_id: string) {
    const res = await fetch(`http://${network.value}:10001/room_check`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ room_id })
    })
    return (await res.json()).ok as boolean
  }

  async function connect(name: string,
    net = 'localhost',
    role: 'player' | 'spectator' = 'player',
    host: boolean = false,
    room_id: string
  ) {
    network.value = net
    if (!host) {
      if (!(await roomCheck(room_id))) {
        console.log("error: ルームID不正")
        throw new Error('invalid room id')
      }
      if (!(await nameCheck(name, room_id))) {
        console.log("error: 名前重複")
        throw new Error('duplicate name')
      }
      room.value = room_id
    }

    player.value = name
    isHost.value = host
    console.log('connect', name, net, role, host)
    ws.value = new WebSocket(`ws://${net}:10001/ws/othello/${encodeURIComponent(name)}?role=${role}&host=${host}&room=${room_id}`)

    ws.value.onmessage = (ev) => handle(JSON.parse(ev.data))
    ws.value.onerror   = () => reset()

    ws.value.onclose = (ev) => {
      console.log(ev.reason)
      console.log("code: ", ev.code)
      if (ev.code === 1000) {
        console.log("正常終了")
      } else if (ev.code === 4000) {
        alert('相手が退室しました')
      } else {
        alert('接続が切れました')
      }
      reset()               // 盤面リセット & ルート遷移
    }

    status.value = 'waiting'
  }

  function sendMove (x: number, y: number) {
    if (!ws.value) return
    ws.value.send(JSON.stringify({ type: 'move', x, y }))
  }

  function leave (code: number = 1000) {
    console.log("leave_code: ", code)
    if (ws.value){
      ws.value.send(JSON.stringify({ type: 'leave', code: code }))
      reset()
    }
  }

  /* ----- private: WS handler ----- */
  function handle (m: any) {
    switch (m.type) {
      case 'matched':
        console.log('player1', m.player1, 'player2', m.player2)
        opponent.value = player.value === m.player1 ? m.player2 : m.player1
        console.log('opponent: ', opponent.value)
        break
      case 'wait':
        console.log('wait: ',m.message)
        room.value = m.room
        break
      case 'start':
        firstTurn.value = m.first
        my_color.value = player.value === m.black ? 'black' : 'white'
        opp_color.value = player.value === m.black ? 'white' : 'black'
        console.log("first: ", firstTurn.value)
        console.log("自分の色: ", my_color.value)
        status.value = 'playing'
        resetBoard()
        console.log("turn: ", turn.value)
        router.push('/game')
        break
      case 'move':
        console.log("move: ", m.turn, "x: ", m.x, "y: ", m.y)
        lastMove.value = { x: m.x, y: m.y, color: m.turn === player.value ? my_color.value : opp_color.value }
        turn.value = m.turn === player.value ? opp_color.value : my_color.value
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
    // 初期４石などを置きたければここで
    turn.value = 'black'
  }

  function reset () {
    // ① ソケットを閉じる（既に CLOSED でもエラーにならない）
    ws.value?.close()
    ws.value = null

    // ② 名前関連をクリア
    opponent.value = ''
    /* player.value は残す／消す どちらでも可 */

    // ③ 盤面・状態を初期化
    status.value = 'idle'
    router.push('/')
  }

  return {
    spectators,
    ws, player,
    isHost,
    setFirstTurn,
    firstTurn,
    opponent,
    room,
    my_color,
    opp_color,
    turn,
    status,
    connect,
    sendMove,
    leave,
    lastMove,
    clearLastMove () { lastMove.value = null },
  }
})
