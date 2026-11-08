<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useSSE } from './composables/useSSE.js'
import { TABS } from './constants/navigation.js'
import AppHeader from './components/AppHeader.vue'
import AppNav from './components/AppNav.vue'
import ResearchView from './views/ResearchView.vue'
import ReportView from './views/ReportView.vue'
import HostDiscussionView from './views/HostDiscussionView.vue'
import ConfigView from './views/ConfigView.vue'

const currentTaskId = ref(localStorage.getItem('currentResearchTaskId') || '')
const currentResearchQuery = ref(localStorage.getItem('currentResearchQuery') || '')
const { connected, roleProgress, roleResults, connect, clearResearchState } = useSSE(currentTaskId)
const activeTab = ref('research')
const completedRoles = computed(() => Object.keys(roleResults.value).length)

function handleTaskCreated(taskId, researchQuery = '') {
  currentTaskId.value = taskId
  if (researchQuery) currentResearchQuery.value = researchQuery
}

watch(currentTaskId, taskId => {
  if (taskId) {
    localStorage.setItem('currentResearchTaskId', taskId)
  } else {
    localStorage.removeItem('currentResearchTaskId')
  }
  connect()
})

watch(currentResearchQuery, researchQuery => {
  if (researchQuery) {
    localStorage.setItem('currentResearchQuery', researchQuery)
  } else {
    localStorage.removeItem('currentResearchQuery')
  }
})

onMounted(() => connect())
</script>

<template>
  <div class="app-shell">
    <div class="accent-bar"></div>
    <AppHeader :connected="connected" />
    <AppNav
      v-model:activeTab="activeTab"
      :tabs="TABS"
      :completedRoles="completedRoles"
    />

    <main class="app-main">
      <ResearchView
        v-show="activeTab === 'research'"
        :roleProgress="roleProgress"
        :roleResults="roleResults"
        :current-task-id="currentTaskId"
        @research-started="clearResearchState"
        @task-created="handleTaskCreated"
      />
      <ReportView
        v-show="activeTab === 'report'"
        :task-id="currentTaskId"
        :research-query="currentResearchQuery"
      />
      <HostDiscussionView v-show="activeTab === 'host'" :task-id="currentTaskId" />
      <ConfigView v-show="activeTab === 'config'" />
    </main>
  </div>
</template>

<style scoped>
.accent-bar {
  position: fixed; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, transparent, var(--amber), transparent);
  opacity: 0.6;
  z-index: 10;
  animation: pulse-glow 4s ease-in-out infinite;
}

.app-main {
  padding: 0;
  max-width: 1440px;
  margin: 0 auto;
}
</style>