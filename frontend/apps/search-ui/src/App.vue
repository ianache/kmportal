<template>
  <div class="search-ui">

    <!-- Hero -->
    <div class="hero" :class="{ 'hero--compact': hasResults }">
      <template v-if="!hasResults">
        <h1 class="hero-title">Semantic Search</h1>
        <p class="hero-desc">Ask anything across your knowledge base.</p>
      </template>
      <div class="search-bar-wrap">
        <div class="search-bar" :class="{ 'search-bar--focused': focused }">
          <svg class="search-icon" width="18" height="18" viewBox="0 0 20 20" fill="none"
            stroke="currentColor" stroke-width="1.8">
            <circle cx="9" cy="9" r="6"/><path d="M17 17l-3.5-3.5"/>
          </svg>
          <input
            ref="inputEl"
            v-model="query"
            class="search-input"
            placeholder="Search nodes, concepts, documents…"
            @focus="focused = true"
            @blur="focused = false"
            @keydown.enter="doSearch"
          />
          <button v-if="query" class="clear-btn" @click="query = ''; results = []">
            <svg width="14" height="14" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="4" y1="4" x2="16" y2="16"/><line x1="16" y1="4" x2="4" y2="16"/>
            </svg>
          </button>
          <button class="search-btn" @click="doSearch">Search</button>
        </div>
      </div>

      <!-- Suggestions (when empty) -->
      <div v-if="!hasResults" class="suggestions">
        <span class="suggestions-label">Try:</span>
        <button
          v-for="s in suggestions"
          :key="s"
          class="suggestion-pill"
          @click="query = s; doSearch()"
        >{{ s }}</button>
      </div>
    </div>

    <!-- Filters row -->
    <div v-if="hasResults" class="results-header">
      <span class="results-count">{{ results.length }} results for "<strong>{{ lastQuery }}</strong>"</span>
      <div class="type-filters">
        <button
          v-for="t in typeFilters"
          :key="t"
          class="chip"
          :class="{ 'chip--active': activeType === t }"
          @click="activeType = t"
        >{{ t }}</button>
      </div>
    </div>

    <!-- Results -->
    <div v-if="hasResults" class="results-grid">
      <div
        v-for="r in filteredResults"
        :key="r.id"
        class="result-card"
      >
        <div class="result-meta">
          <span class="result-type" :style="{ background: r.typeColor + '18', color: r.typeColor }">
            {{ r.type }}
          </span>
          <span class="result-domain">{{ r.domain }}</span>
        </div>
        <h3 class="result-title">{{ r.title }}</h3>
        <p class="result-excerpt" v-html="r.excerpt"></p>
        <div class="result-footer">
          <span class="result-score">
            <svg width="12" height="12" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8">
              <polygon points="10,2 12.4,7.4 18.4,7.6 14,11.8 15.6,17.6 10,14.4 4.4,17.6 6,11.8 1.6,7.6 7.6,7.4"/>
            </svg>
            {{ r.score }}% relevance
          </span>
          <span class="result-date">{{ r.date }}</span>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Result {
  id: number
  title: string
  excerpt: string
  type: string
  typeColor: string
  domain: string
  score: number
  date: string
}

const query = ref('')
const lastQuery = ref('')
const focused = ref(false)
const activeType = ref('All')
const results = ref<Result[]>([])

const suggestions = [
  'transformer architecture',
  'quantum entanglement',
  'urban planning theory',
  'Bayesian inference',
  'Renaissance political thought',
]

const typeFilters = computed(() => {
  const types = ['All', ...new Set(results.value.map((r) => r.type))]
  return types
})

const hasResults = computed(() => results.value.length > 0)

const filteredResults = computed(() => {
  if (activeType.value === 'All') return results.value
  return results.value.filter((r) => r.type === activeType.value)
})

function doSearch() {
  if (!query.value.trim()) return
  lastQuery.value = query.value
  activeType.value = 'All'
  results.value = [
    {
      id: 1,
      title: 'Transformer Architecture Overview',
      excerpt: 'The <mark>transformer</mark> model, introduced in "Attention is All You Need," fundamentally changed NLP through self-attention mechanisms.',
      type: 'Document',
      typeColor: '#007AFF',
      domain: 'Artificial Intelligence',
      score: 97,
      date: '2 h ago',
    },
    {
      id: 2,
      title: 'Self-Attention Mechanisms',
      excerpt: 'Self-attention allows the model to relate different positions of a single sequence to compute a representation of that sequence.',
      type: 'Node',
      typeColor: '#AF52DE',
      domain: 'Artificial Intelligence',
      score: 91,
      date: '5 h ago',
    },
    {
      id: 3,
      title: 'BERT and GPT Comparison',
      excerpt: 'Bidirectional vs. unidirectional pre-training approaches and their downstream task performance.',
      type: 'Document',
      typeColor: '#007AFF',
      domain: 'Artificial Intelligence',
      score: 84,
      date: '1 d ago',
    },
    {
      id: 4,
      title: 'Cognitive Load Theory',
      excerpt: 'Working memory limitations shape how information is processed and retained during learning.',
      type: 'Concept',
      typeColor: '#FF9500',
      domain: 'Cognitive Models',
      score: 72,
      date: '3 d ago',
    },
  ]
}
</script>

<style scoped>
.search-ui {
  min-height: 100%;
  display: flex;
  flex-direction: column;
}

/* ── Hero ────────────────────────────────── */
.hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80px 40px 40px;
  text-align: center;
  transition: padding 0.3s;
}

.hero--compact {
  padding: 32px 40px 24px;
}

.hero-title {
  font-size: 40px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text, #1D1D1F);
  margin-bottom: 8px;
}

.hero-desc {
  font-size: 17px;
  color: var(--text-2, #86868B);
  margin-bottom: 32px;
}

.search-bar-wrap {
  width: 100%;
  max-width: 640px;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--surface, #fff);
  border: 1.5px solid var(--border, #E5E5E7);
  border-radius: var(--radius, 12px);
  padding: 12px 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: border-color 0.15s, box-shadow 0.15s;
}

.search-bar--focused {
  border-color: var(--primary, #007AFF);
  box-shadow: 0 0 0 3px rgba(0,122,255,0.12), 0 2px 8px rgba(0,0,0,0.06);
}

.search-icon { color: var(--text-2, #86868B); flex-shrink: 0; }

.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 16px;
  font-family: inherit;
  color: var(--text, #1D1D1F);
  background: transparent;
}
.search-input::placeholder { color: var(--text-2, #86868B); }

.clear-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgba(0,0,0,0.06);
  color: var(--text-2, #86868B);
  cursor: pointer;
  border: none;
  transition: background 0.12s;
  flex-shrink: 0;
}
.clear-btn:hover { background: rgba(0,0,0,0.12); }

.search-btn {
  background: var(--primary, #007AFF);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  padding: 7px 18px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-family: inherit;
  flex-shrink: 0;
  transition: opacity 0.12s;
}
.search-btn:hover { opacity: 0.88; }

/* ── Suggestions ─────────────────────────── */
.suggestions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 20px;
  flex-wrap: wrap;
  justify-content: center;
}

.suggestions-label {
  font-size: 13px;
  color: var(--text-2, #86868B);
}

.suggestion-pill {
  padding: 5px 12px;
  border-radius: 999px;
  background: var(--surface, #fff);
  border: 1px solid var(--border, #E5E5E7);
  font-size: 13px;
  color: var(--text, #1D1D1F);
  cursor: pointer;
  font-family: inherit;
  transition: background 0.12s, border-color 0.12s;
}
.suggestion-pill:hover {
  background: var(--primary-soft, rgba(0,122,255,0.1));
  border-color: var(--primary, #007AFF);
  color: var(--primary, #007AFF);
}

/* ── Results header ──────────────────────── */
.results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40px 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.results-count {
  font-size: 14px;
  color: var(--text-2, #86868B);
}
.results-count strong { color: var(--text, #1D1D1F); }

.type-filters {
  display: flex;
  gap: 6px;
}

.chip {
  padding: 5px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 500;
  background: var(--surface, #fff);
  border: 1px solid var(--border, #E5E5E7);
  color: var(--text-2, #86868B);
  cursor: pointer;
  font-family: inherit;
  transition: background 0.12s, color 0.12s;
}
.chip:hover { background: rgba(0,0,0,0.04); color: var(--text, #1D1D1F); }
.chip--active {
  background: var(--primary-soft, rgba(0,122,255,0.1));
  border-color: var(--primary, #007AFF);
  color: var(--primary, #007AFF);
}

/* ── Results grid ────────────────────────── */
.results-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 0 40px 40px;
}

.result-card {
  background: var(--surface, #fff);
  border: 1px solid var(--border, #E5E5E7);
  border-radius: var(--radius, 12px);
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  cursor: pointer;
  box-shadow: var(--shadow-card, 0 1px 2px rgba(0,0,0,0.04));
  transition: box-shadow 0.15s, transform 0.15s;
}
.result-card:hover {
  box-shadow: 0 4px 20px rgba(0,0,0,0.09);
  transform: translateY(-1px);
}

.result-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.result-type {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 999px;
  letter-spacing: 0.02em;
}

.result-domain {
  font-size: 12px;
  color: var(--text-2, #86868B);
}

.result-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text, #1D1D1F);
  letter-spacing: -0.01em;
}

.result-excerpt {
  font-size: 14px;
  color: var(--text-2, #86868B);
  line-height: 1.5;
}

.result-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 10px;
  border-top: 1px solid var(--border, #E5E5E7);
}

.result-score {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 500;
  color: var(--primary, #007AFF);
}

.result-date {
  font-size: 12px;
  color: var(--text-2, #86868B);
}
</style>
