<template>
  <div class="hybrid-card">
    <!-- Header: OWL class + ISO compliance badges -->
    <div class="hybrid-card__header">
      <div class="badge-group">
        <span class="badge badge--owl">
          <!-- Network icon -->
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="5" r="3"/><circle cx="19" cy="19" r="3"/><circle cx="5" cy="19" r="3"/>
            <line x1="12" y1="8" x2="12" y2="14"/><line x1="12" y1="17" x2="19" y2="17"/>
            <line x1="12" y1="17" x2="5" y2="17"/>
          </svg>
          {{ result.provenance.owl_class }}
        </span>

        <span class="badge" :class="isoClass">
          <!-- ShieldCheck icon -->
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            <polyline points="9 12 11 14 15 10"/>
          </svg>
          {{ result.provenance.iso_compliance }}
        </span>
      </div>

      <span class="score">
        <!-- FileText icon -->
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/>
          <line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>
        </svg>
        {{ scoreLabel }}
      </span>
    </div>

    <!-- Content excerpt -->
    <p class="hybrid-card__content">{{ result.content }}</p>

    <!-- Footer: source file + lineage button -->
    <div class="hybrid-card__footer">
      <span class="source-file">{{ result.source_file || 'Unknown source' }}</span>

      <button class="lineage-btn" @click.stop="$emit('show-lineage', result)">
        <!-- Network icon larger -->
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="5" r="3"/><circle cx="19" cy="19" r="3"/><circle cx="5" cy="19" r="3"/>
          <line x1="12" y1="8" x2="12" y2="14"/><line x1="12" y1="17" x2="19" y2="17"/>
          <line x1="12" y1="17" x2="5" y2="17"/>
        </svg>
        Lineage
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { HybridSearchResult } from '../types/semantic'

const props = defineProps<{ result: HybridSearchResult }>()
defineEmits<{ (e: 'show-lineage', result: HybridSearchResult): void }>()

const scoreLabel = computed(() => `${(props.result.score * 100).toFixed(1)}%`)

const isoClass = computed(() => {
  const c = props.result.provenance.iso_compliance?.toUpperCase()
  if (c === 'PÚBLICO' || c === 'PUBLICO' || c === 'PUBLIC') return 'badge--iso-public'
  if (c === 'CONFIDENCIAL' || c === 'CONFIDENTIAL') return 'badge--iso-confidential'
  return 'badge--iso-default'
})
</script>

<style scoped>
.hybrid-card {
  background: var(--surface-container-lowest, #ffffff);
  border: 1px solid var(--outline-variant, #e5e5e7);
  border-radius: 12px;
  padding: 18px 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: box-shadow 0.2s, border-color 0.2s;
}

.hybrid-card:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.07);
  border-color: var(--primary, #0058bc);
}

/* Header */
.hybrid-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.badge-group {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 999px;
  letter-spacing: 0.03em;
}

/* OWL class badge — light blue */
.badge--owl {
  background: rgba(0, 88, 188, 0.1);
  color: var(--primary, #0058bc);
}

/* ISO compliance badges */
.badge--iso-public {
  background: rgba(22, 163, 74, 0.1);
  color: #16a34a;
}

.badge--iso-confidential {
  background: rgba(234, 88, 12, 0.1);
  color: #ea580c;
}

.badge--iso-default {
  background: var(--surface-container, #ecedf9);
  color: var(--on-surface-variant, #86868b);
}

/* Score */
.score {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
  font-weight: 600;
  color: var(--on-surface-variant, #414755);
  white-space: nowrap;
}

/* Content */
.hybrid-card__content {
  font-size: 14px;
  line-height: 1.6;
  color: var(--on-surface-variant, #414755);
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Footer */
.hybrid-card__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 10px;
  border-top: 1px solid var(--surface-container, #ecedf9);
}

.source-file {
  font-size: 12px;
  color: var(--on-surface-variant, #86868b);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 60%;
}

.lineage-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--primary, #0058bc);
  background: rgba(0, 88, 188, 0.06);
  border: 1px solid rgba(0, 88, 188, 0.2);
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
  white-space: nowrap;
}

.lineage-btn:hover {
  background: rgba(0, 88, 188, 0.12);
  border-color: var(--primary, #0058bc);
}
</style>
