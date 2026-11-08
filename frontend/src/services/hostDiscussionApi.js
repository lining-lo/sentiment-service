import { request } from './http.js'

export function getHostDiscussionLog(taskId) {
  return request('GET', `/host/discussion?task_id=${encodeURIComponent(taskId)}`)
}
