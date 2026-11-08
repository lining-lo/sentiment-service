import { request } from './http.js'

export function getReportStatus(taskId) {
  return request('GET', `/report/status?task_id=${encodeURIComponent(taskId)}`)
}

export function generateReport(taskId) {
  return request('POST', '/report/generate', { task_id: taskId })
}

export function getReportResult(generationId) {
  return fetch(`/api/report/result/${generationId}`).then(response => response.text())
}

export function getReportDownloadUrl(generationId, fileType = 'html') {
  return `/api/report/download/${generationId}/${fileType}`
}

export function getMarkdownUrl(generationId) {
  return getReportDownloadUrl(generationId, 'md')
}