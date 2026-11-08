<script setup>
import { computed, ref, onUnmounted, nextTick, watch } from 'vue'
import { getHostDiscussionLog } from '../composables/api.js'
import { DEFAULT_RESEARCH_DIMENSIONS } from '../constants/roles.js'
import HostDiscussionDimensionList from '../components/HostDiscussionDimensionList.vue'
import HostDiscussionEmptyState from '../components/HostDiscussionEmptyState.vue'

const props = defineProps({
  taskId: String,
})

const messages = ref([])
const researchDimensions = DEFAULT_RESEARCH_DIMENSIONS
let pollTimer = null

const dimensionRows = computed(() =>
  researchDimensions.map(dimension => {
    const scoped = messages.value.filter(msg => msg.dimension_key === dimension.key)
    return {
      ...dimension,
      insight: latestBySpeaker(scoped, 'insight'),
      media: latestBySpeaker(scoped, 'media'),
      host: latestBySpeaker(scoped, 'host'),
      count: scoped.length,
    }
  })
)

const hasStructuredMessages = computed(() => dimensionRows.value.some(row => row.count))

function latestBySpeaker(items, source) {
  return [...items].reverse().find(msg => msg.source === source) || null
}

function normalizeDiscussionRecords(data) {
  const records = data?.discussion_records || []
  return records.map(record => ({
    source: record.source || '',
    message_text: record.message_text || '',
    sent_at: record.sent_at || '',
    dimension_key: record.dimension_key || '',
  }))
}

async function refreshLog() {
  if (!props.taskId) return
  try {
    const data = await getHostDiscussionLog(props.taskId)
    const nextMessages = normalizeDiscussionRecords(data)
    const shouldUpdate = hasDiscussionChanged(nextMessages)
    const shouldFollow = isNearBottom()
    if (shouldUpdate) {
      messages.value = nextMessages
      await nextTick()
      if (shouldFollow) scrollToBottom()
    }
    if (isDiscussionComplete()) {
      stopPolling()
    }
  } catch {}
}

function startPolling() {
  stopPolling()
  pollTimer = setInterval(refreshLog, 3000)
}

watch(
  () => props.taskId,
  taskId => {
    messages.value = []
    if (!taskId) {
      stopPolling()
      return
    }
    refreshLog()
    startPolling()
  },
  { immediate: true },
)

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

function isDiscussionComplete() {
  return dimensionRows.value.every(row => row.host)
}

function hasDiscussionChanged(nextMessages) {
  if (nextMessages.length !== messages.value.length) return true
  const currentLast = messages.value[messages.value.length - 1]
  const nextLast = nextMessages[nextMessages.length - 1]
  return JSON.stringify(currentLast) !== JSON.stringify(nextLast)
}

function isNearBottom() {
  const el = document.querySelector('.host-discussion-content')
  if (!el) return true
  return el.scrollHeight - el.scrollTop - el.clientHeight < 80
}

function scrollToBottom() {
  const el = document.querySelector('.host-discussion-content')
  if (el) el.scrollTop = el.scrollHeight
}

onUnmounted(stopPolling)
</script>

<template>
  <div class="host-discussion-view">
    <header class="view-header stagger-1">
      <div class="header-overline">HOST DISCUSSION</div>
      <h2 class="view-title">主持人研判讨论</h2>
      <p class="view-desc">主持人按五个研究维度对齐双 Agent 输出，沉淀逐章研判</p>
    </header>

    <div v-if="messages.length" class="host-discussion-content stagger-3">
      <HostDiscussionDimensionList v-if="hasStructuredMessages" :rows="dimensionRows" />
    </div>

    <HostDiscussionEmptyState v-else :has-task="Boolean(taskId)" />
  </div>
</template>

<style scoped>
.view-header {
  margin-bottom: 2rem;
}

.header-overline {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  letter-spacing: 0.25em;
  color: var(--amber);
  opacity: 0.7;
  margin-bottom: 0.5rem;
}

.view-title {
  font-size: clamp(1.8rem, 4vw, 2.4rem);
  color: var(--paper);
  margin-bottom: 0.4rem;
  letter-spacing: 0.02em;
}

.view-desc {
  color: var(--paper-dim);
  font-size: 0.9rem;
  line-height: 1.6;
}

.host-discussion-content {
  max-height: 66vh;
  overflow-y: auto;
  padding-right: 0.5rem;
}
</style>
