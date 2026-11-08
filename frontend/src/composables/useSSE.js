/* SSE event stream composable for real-time role updates. */

import { ref, onUnmounted } from 'vue'
import { getResearchResults } from './api.js'

export function useSSE(currentTaskId = ref('')) {
  const connected = ref(false)
  const roleProgress = ref({})
  const roleResults = ref({})
  let eventSource = null
  let reconnectTimer = null

  /* 通知-拉取:role_result 仅为完成信号,数据从 REST 拉取 */
  async function fetchRoleResult(role, taskId) {
    try {
      const data = await getResearchResults(taskId)
      const result = data?.results?.[role]
      if (result) {
        roleResults.value = {
          ...roleResults.value,
          [role]: result
        }
      }
    } catch {}
  }

  function connect() {
    clearTimeout(reconnectTimer)
    if (eventSource) eventSource.close()

    const taskId = currentTaskId.value
    if (!taskId) {
      eventSource = null
      connected.value = false
      return
    }

    eventSource = new EventSource(
      `/api/events/stream?task_id=${encodeURIComponent(taskId)}`
    )

    eventSource.addEventListener('connected', () => {
      connected.value = true
    })

    eventSource.onmessage = (event) => {
      try {
        const { event: evtType, data } = JSON.parse(event.data)
        if (currentTaskId.value && data?.task_id && data.task_id !== currentTaskId.value) return
        if (evtType === 'role_progress' && data?.role) {
          const previous = roleProgress.value[data.role]
          const progress = data.status === 'starting'
            ? data.progress_pct
            : Math.max(previous?.progress_pct || 0, data.progress_pct || 0)
          roleProgress.value = {
            ...roleProgress.value,
            [data.role]: {
              ...data,
              progress_pct: progress
            }
          }
        } else if (evtType === 'role_result' && data?.role) {
          fetchRoleResult(data.role, data.task_id || currentTaskId.value)
        }
      } catch {}
    }

    eventSource.onerror = () => {
      connected.value = false
      eventSource?.close()
      reconnectTimer = setTimeout(connect, 3000)
    }
  }

  function disconnect() {
    clearTimeout(reconnectTimer)
    eventSource?.close()
    eventSource = null
    connected.value = false
  }

  function clearResearchState() {
    roleProgress.value = {}
    roleResults.value = {}
  }

  onUnmounted(disconnect)

  return { connected, roleProgress, roleResults, connect, clearResearchState }
}