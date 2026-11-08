<script setup>
import { computed, ref } from 'vue'
import { startResearch, getResearchResults } from '../composables/api.js'
import RoleProgressGrid from '../components/RoleProgressGrid.vue'
import SavedResultsSection from '../components/SavedResultsSection.vue'
import ResearchHero from '../components/ResearchHero.vue'

const props = defineProps({
  roleProgress: Object,
  roleResults: Object,
  currentTaskId: String,
})

const emit = defineEmits(['research-started', 'task-created'])

const query = ref('')
const researching = ref(false)
const results = ref(null)
const loadingResults = ref(false)
const researchDisabled = computed(() =>
  Object.entries(props.roleProgress || {}).some(([role, progress]) =>
    !props.roleResults?.[role]
    && progress?.status !== 'error'
    && (progress?.progress_pct || 0) < 100
  )
)

async function handleResearch() {
  if (!query.value.trim() || researching.value || researchDisabled.value) return
  researching.value = true
  results.value = null
  emit('research-started')
  try {
    const researchQuery = query.value.trim()
    const response = await startResearch(researchQuery)
    if (response?.task_id) emit('task-created', response.task_id, researchQuery)
  } catch (e) {
    console.error('Research start failed:', e)
  } finally {
    researching.value = false
  }
}

async function loadResults() {
  if (!props.currentTaskId) return
  loadingResults.value = true
  try {
    const data = await getResearchResults(props.currentTaskId)
    if (data?.results) {
      results.value = data.results
      if (data.task_id) emit('task-created', data.task_id)
    }
  } catch {}
  loadingResults.value = false
}
</script>

<template>
  <div class="research-view">
    <ResearchHero
      v-model:query="query"
      :researching="researching"
      :research-disabled="researchDisabled"
      :loading-results="loadingResults"
      :has-current-task="Boolean(currentTaskId)"
      @research="handleResearch"
      @load-results="loadResults"
    />

    <RoleProgressGrid
      :role-progress="roleProgress"
      :role-results="roleResults"
    />

    <SavedResultsSection :results="results" />
  </div>
</template>
