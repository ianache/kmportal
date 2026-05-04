<template>
  <BaseCard class="job-card" :class="{ 'job-card--failed': job.status === 'failed' }">
    <div class="job-content">
      <div class="job-header">
        <div class="job-title-wrap">
          <h4 class="job-title">Job #{{ job.id.slice(0, 8) }}</h4>
          <span class="job-meta">Doc: {{ job.document_id.slice(0, 8) }} • Domain: {{ job.domain_id.slice(0, 8) }}</span>
        </div>
        <div class="job-status">
          <span class="status-badge" :class="`status--${job.status}`">
            <span v-if="job.status === 'processing'" class="spinner"></span>
            {{ job.status }}
          </span>
        </div>
      </div>

      <div class="progress-section">
        <div class="progress-bar-bg">
          <div 
            class="progress-bar-fill" 
            :class="`fill--${job.status}`"
            :style="{ width: `${job.progress}%` }"
          ></div>
        </div>
        <div class="progress-text">
          <span>{{ job.progress }}% complete</span>
          <span>{{ formatDate(job.created_at) }}</span>
        </div>
      </div>

      <div v-if="job.error_message" class="error-msg">
        <strong>Error:</strong> {{ job.error_message }}
      </div>

      <div v-if="job.status === 'failed'" class="job-actions">
        <BaseButton secondary small @click="ingestionStore.retryJob(job.id)">
          Retry Job
        </BaseButton>
      </div>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import type { IngestionJob } from '../types/ingestion'
import { useIngestionStore } from '../stores/ingestion'
import BaseCard from 'shell/BaseCard'
import BaseButton from 'shell/BaseButton'

defineProps<{
  job: IngestionJob
}>()

const ingestionStore = useIngestionStore()

function formatDate(dateStr: string) {
  try {
    return new Date(dateStr).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch (e) {
    return dateStr
  }
}
</script>

<style scoped>
.job-card {
  padding: 20px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.job-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}

.job-card--failed {
  border-color: rgba(255, 59, 48, 0.3);
}

.job-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.job-title-wrap {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.job-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: var(--on-surface, #1D1D1F);
}

.job-meta {
  font-size: 12px;
  color: var(--on-surface-variant, #86868B);
}

.status-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
  text-transform: uppercase;
  display: flex;
  align-items: center;
  gap: 6px;
}

.status--done { background: rgba(52, 199, 89, 0.1); color: #34C759; }
.status--processing { background: rgba(0, 122, 255, 0.1); color: #007AFF; }
.status--pending { background: rgba(142, 142, 147, 0.1); color: #8E8E93; }
.status--failed { background: rgba(255, 59, 48, 0.1); color: #FF3B30; }

.spinner {
  width: 10px;
  height: 10px;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.progress-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-bar-bg {
  height: 8px;
  background: var(--surface-container, #ecedf9);
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 4px;
}

.fill--done { background: #34C759; }
.fill--processing { background: #007AFF; }
.fill--pending { background: #8E8E93; }
.fill--failed { background: #FF3B30; }

.progress-text {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--on-surface-variant, #86868B);
  font-weight: 500;
}

.error-msg {
  font-size: 13px;
  color: var(--error, #ba1a1a);
  background: var(--error-container, #ffdad6);
  padding: 10px 12px;
  border-radius: 8px;
  line-height: 1.4;
}

.job-actions {
  display: flex;
  justify-content: flex-end;
}
</style>
