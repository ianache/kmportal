<template>
  <div class="search-result-card" @click="$emit('open-document', result.document_id)">
    <div class="card-header">
      <div class="metadata">
        <span class="type-badge" :class="`type--${result.metadata?.type?.toLowerCase() || 'unknown'}`">
          {{ result.metadata?.type || 'Document' }}
        </span>
        <span class="domain-badge">{{ result.document_title }}</span>
      </div>
      <div class="relevance-score" :style="{ color: scoreColor }">
        <svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor">
          <path d="M10 2l2.4 7.4h7.6l-6.2 4.5 2.4 7.4-6.2-4.5-6.2 4.5 2.4-7.4-6.2-4.5h7.6z"/>
        </svg>
        <span>{{ Math.round(result.score * 100) }}% relevance</span>
      </div>
    </div>

    <h3 class="result-title">{{ result.document_title }}</h3>
    
    <div class="result-excerpt" v-html="highlightedText"></div>

    <div class="card-footer">
      <div class="footer-meta">
        <span class="meta-item">
          <strong>Source:</strong> {{ result.metadata?.source || 'Upload' }}
        </span>
        <span class="meta-item">
          <strong>Date:</strong> {{ formatDate(result.metadata?.created_at) }}
        </span>
      </div>
      <button class="view-btn">View Document</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useSearchStore } from '../stores/search'
import type { SearchResult } from '../types/search'

const props = defineProps<{
  result: SearchResult
}>()

defineEmits<{
  (e: 'open-document', id: string): void
}>()

const searchStore = useSearchStore()

const highlightedText = computed(() => {
  return searchStore.highlightText(props.result.text, searchStore.query)
})

const scoreColor = computed(() => {
  const score = props.result.score
  if (score > 0.8) return 'var(--primary, #007AFF)'
  if (score > 0.5) return 'var(--tertiary, #9e3d00)'
  return 'var(--on-surface-variant, #86868B)'
})

function formatDate(dateStr?: string) {
  if (!dateStr) return 'N/A'
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
  } catch (e) {
    return dateStr
  }
}
</script>

<style scoped>
.search-result-card {
  background: var(--surface-container-lowest, #ffffff);
  border: 1px solid var(--outline-variant, #E5E5E7);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.search-result-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(0,0,0,0.08);
  border-color: var(--primary, #007AFF);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.metadata {
  display: flex;
  align-items: center;
  gap: 10px;
}

.type-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 999px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: var(--surface-container, #ecedf9);
  color: var(--on-surface-variant, #414755);
}

.type--pdf { background: rgba(255, 59, 48, 0.1); color: #FF3B30; }
.type--txt { background: rgba(52, 199, 89, 0.1); color: #34C759; }
.type--docx { background: rgba(0, 122, 255, 0.1); color: #007AFF; }

.domain-badge {
  font-size: 12px;
  color: var(--on-surface-variant, #86868B);
}

.relevance-score {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
}

.result-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--on-surface, #1D1D1F);
  margin: 0;
  letter-spacing: -0.01em;
}

.result-excerpt {
  font-size: 14px;
  line-height: 1.6;
  color: var(--on-surface-variant, #414755);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.result-excerpt :deep(mark) {
  background: var(--primary-container, #0070eb);
  color: var(--on-primary, #ffffff);
  padding: 0 2px;
  border-radius: 2px;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 12px;
  border-top: 1px solid var(--surface-container, #ecedf9);
  margin-top: 4px;
}

.footer-meta {
  display: flex;
  gap: 16px;
}

.meta-item {
  font-size: 12px;
  color: var(--on-surface-variant, #86868B);
}

.meta-item strong {
  color: var(--on-surface, #1D1D1F);
  font-weight: 500;
}

.view-btn {
  font-size: 13px;
  font-weight: 600;
  color: var(--primary, #007AFF);
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
}

.view-btn:hover {
  text-decoration: underline;
}
</style>
