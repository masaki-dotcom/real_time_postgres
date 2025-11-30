import { ref } from 'vue'

// --- Singleton 防止 ---
const lastEvent = ref<any>(null)
let eventSource: EventSource | null = null
let initialized = false

export function useUserEvents() {

  const start = () => {
    if (initialized) {
      console.log("🔁 SSE already initialized")
      return
    }
    initialized = true

    eventSource = new EventSource("http://localhost:5001/events")
    console.log("🌐 SSE start")

    eventSource.onopen = () => {
      console.log("🟢 SSE connected")
    }

    eventSource.onmessage = (event) => {
      console.log("📩 SSE:", event.data)
      try {
        const data = JSON.parse(event.data)
        // _ts を追加して watch を必ず発火させる
        lastEvent.value = { ...data, _ts: Date.now() }
      } catch (e) {
        console.error("JSON parse error", e)
      }
    }

    eventSource.onerror = (err) => {
      console.error("❌ SSE error", err)
      eventSource?.close()
      eventSource = null
      initialized = false
      setTimeout(start, 3000)
    }
  }

  // close() はしない。複数接続防止
  const close = () => {
    console.log("⚠ close() is disabled to prevent multiple SSE bindings")
  }

  start()

  return {
    lastEvent,
    start,
    close
  }
}
