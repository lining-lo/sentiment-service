import { request } from './http.js'

export function startResearch(query) {
  return request('POST', '/research', { query })
}

export function getResearchResults(taskId) {
  return request('GET', `/research/results?task_id=${encodeURIComponent(taskId)}`)
}
