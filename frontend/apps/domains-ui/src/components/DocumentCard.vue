<template>
  <BaseCard class="document-card" clickable>
    <div class="card-content">
      <div class="doc-header">
        <h4 class="doc-title">{{ document.title }}</h4>
        <span class="status-badge" :class="`status--${document.status}`">
          {{ document.status }}
        </span>
      </div>
      
      <div class="doc-details">
        <div class="detail-row">
          <span class="detail-label">Type</span>
          <span class="detail-value">{{ document.metadata?.content_type || 'Unknown' }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Source</span>
          <span class="detail-value">{{ document.source_type }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Chunks</span>
          <span class="detail-value">{{ document.chunk_count }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Created</span>
          <span class="detail-value">{{ formatDate(document.created_at) }}</span>
        </div>
      </div>

      <div v-if="document.error_message" class="error-msg">
        {{ document.error_message }}
      </div>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import type { Document } from '../types/domains'
import BaseCard from 'shell/BaseCard'

defineProps<{
  document: Document
}>()

function formatDate(dateStr: string) {
  try {
    return new Date(dateStr).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
  } catch (e) {
    return dateStr
  }
}
</script>

<style scoped>
.document-card {
  padding: 16px;
  transition: all 0.2s;
}

.document-card:hover {
  border-color: var(--primary, #007AFF);
  transform: scale(1.01);
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.doc-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.doc-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--on-surface, #1D1D1F);
  margin: 0;
  word-break: break-all;
}

.status-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 999px;
  text-transform: uppercase;
}

.status--done { background: rgba(52, 199, 89, 0.1); color: #34C759; }
.status--processing { background: rgba(0, 122, 255, 0.1); color: #007AFF; animation: pulse 2s infinite; }
.status--pending { background: rgba(142, 142, 147, 0.1); color: #8E8E93; }
.status--failed { background: rgba(255, 59, 48, 0.1); color: #FF3B30; }

@keyframes pulse {
  0% { opacity: 0.7; }
  50% { opacity: 1; }
  100% { opacity: 0.7; }
}

.doc-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.detail-row {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.detail-label {
  font-size: 11px;
  color: var(--on-surface-variant, #86868B);
  text-transform: uppercase;
}

.detail-value {
  font-size: 13px;
  color: var(--on-surface, #414755);
  font-weight: 500;
}

.error-msg {
  font-size: 12px;
  color: var(--error, #ba1a1a);
  background: var(--error-container, #ffdad6);
  padding: 8px;
  border-radius: 6px;
  margin-top: 4px;
}
</style>
