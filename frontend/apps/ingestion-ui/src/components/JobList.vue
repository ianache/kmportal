<template>
  <div class="job-list-view">
    <div class="stats-row">
      <BaseCard class="stat-card">
        <span class="stat-label">Total Jobs</span>
        <span class="stat-value">{{ ingestionStore.stats.total }}</span>
      </BaseCard>
      <BaseCard class="stat-card">
        <span class="stat-label">Processing</span>
        <span class="stat-value processing">{{ ingestionStore.stats.processing }}</span>
      </BaseCard>
      <BaseCard class="stat-card">
        <span class="stat-label">Completed</span>
        <span class="stat-value done">{{ ingestionStore.stats.done }}</span>
      </BaseCard>
      <BaseCard class="stat-card">
        <span class="stat-label">Failed</span>
        <span class="stat-value failed">{{ ingestionStore.stats.failed }}</span>
      </BaseCard>
    </div>

    <div class="list-filters">
      <div class="filters-left">
        <select :value="ingestionStore.filters.status" @change="e => handleStatusFilter(e)">
          <option value="">All Statuses</option>
          <option value="done">Done</option>
          <option value="processing">Processing</option>
          <option value="pending">Pending</option>
          <option value="failed">Failed</option>
        </select>
      </div>
      <BaseButton secondary small @click="ingestionStore.loadJobs()">
        Refresh
      </BaseButton>
    </div>

    <div v-if="ingestionStore.isLoading && ingestionStore.jobs.length === 0" class="loading-state">
      <div v-for="i in 3" :key="i" class="skeleton-card"></div>
    </div>

    <div v-else-if="ingestionStore.jobs.length === 0" class="empty-state">
      <p>No ingestion jobs found.</p>
    </div>

    <div v-else class="jobs-grid">
      <JobCard 
        v-for="job in ingestionStore.recentJobs" 
        :key="job.id"
        :job="job"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useIngestionStore } from '../stores/ingestion'
import JobCard from './JobCard.vue'
import BaseCard from 'shell/BaseCard'
import BaseButton from 'shell/BaseButton'

const ingestionStore = useIngestionStore()

function handleStatusFilter(event: Event) {
  const value = (event.target as HTMLSelectElement).value
  ingestionStore.setFilter('status', value || undefined)
}
</script>

<style scoped>
.job-list-view {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
}

.stat-card {
  padding: 20px;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--on-surface-variant, #86868B);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--on-surface, #1D1D1F);
}

.stat-value.processing { color: #007AFF; }
.stat-value.done { color: #34C759; }
.stat-value.failed { color: #FF3B30; }

.list-filters {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.list-filters select {
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid var(--outline-variant, #E5E5E7);
  background: var(--surface-container-lowest, #ffffff);
  font-size: 14px;
  outline: none;
}

.jobs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.skeleton-card {
  height: 160px;
  background: var(--surface-container, #ecedf9);
  border-radius: 12px;
  margin-bottom: 20px;
  animation: pulse 1.5s infinite ease-in-out;
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

.empty-state {
  text-align: center;
  padding: 60px 0;
  color: var(--on-surface-variant, #86868B);
}

@media (max-width: 600px) {
  .jobs-grid {
    grid-template-columns: 1fr;
  }
}
</style>
