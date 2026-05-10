<template>
  <div class="login-page">
    <!-- Decorative background blobs -->
    <div class="bg-blobs" aria-hidden="true">
      <div class="blob blob-tl"></div>
      <div class="blob blob-br"></div>
    </div>

    <!-- Hero -->
    <main class="hero">
      <div class="hero-inner">

        <!-- Brand -->
        <div class="brand animate-rise-1">
          <div class="logo-box">
            <span class="material-symbols-outlined logo-icon">lightbulb</span>
          </div>
          <h1 class="brand-name">Lumina Knowledge</h1>
        </div>

        <!-- Welcome -->
        <div class="welcome animate-rise-2">
          <h2 class="welcome-heading">Welcome back</h2>
          <p class="welcome-sub">
            Access your secure portal to the global knowledge network and managed workspace.
          </p>
        </div>

        <!-- CTA -->
        <div class="cta-area animate-rise-3">
          <button
            class="btn-signin"
            :class="{ loading: authStore.isLoading }"
            @click="login"
            :disabled="authStore.isLoading"
          >
            <span>{{ authStore.isLoading ? 'Signing in…' : 'Sign in with Keycloak' }}</span>
            <span v-if="!authStore.isLoading" class="material-symbols-outlined btn-arrow">arrow_forward</span>
          </button>
          <p class="legal-note">Unauthorized access is prohibited and monitored.</p>
          <p v-if="authStore.error" class="error-alert" role="alert">{{ authStore.error }}</p>
        </div>

      </div>
    </main>

    <!-- Right news sidebar — visible only on wide screens -->
    <aside class="news-sidebar" aria-label="Network intelligence feed">
      <div class="news-header">
        <span class="intel-label">Network Intel</span>
        <span class="live-dot" :style="liveDotStyle" aria-hidden="true"></span>
      </div>
      <div class="news-list glass">
        <article
          v-for="item in newsItems"
          :key="item.id"
          class="news-item"
          :class="{ 'news-item--linked': item.url }"
          @click="openUrl(item.url)"
        >
          <div class="news-meta">
            <span class="news-tag" :style="{ color: item.color, background: item.bg }">{{ item.tag }}</span>
            <span class="news-ago">{{ item.time }}</span>
          </div>
          <h4 class="news-title">{{ item.title }}</h4>
          <p class="news-text">{{ item.body }}</p>
        </article>
      </div>
    </aside>

    <!-- Bottom stats ribbon -->
    <footer class="stats-footer" aria-label="Platform statistics">
      <div class="stats-band glass">
        <div
          v-for="stat in platformStats"
          :key="stat.label"
          class="stat-cell"
        >
          <div class="stat-icon-wrap">
            <span class="material-symbols-outlined">{{ stat.icon }}</span>
          </div>
          <div class="stat-info">
            <span class="stat-val">{{ stat.value }}</span>
            <span class="stat-lbl">{{ stat.label }}</span>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { fetchKbSummary, fetchIntelStatus, fetchNews } from '../services/loginApi'
import type { IntelStatus, NewsCategory } from '../services/loginApi'

const authStore = useAuthStore()

function login() {
  authStore.clearError()
  authStore.login()
}

// ── Category → badge styles ────────────────────────────────────
const CATEGORY_STYLES: Record<NewsCategory, { color: string; bg: string }> = {
  PLATFORM:   { color: '#ffb595', bg: 'rgba(158,61,0,0.2)'   },
  INFRA:      { color: '#adc6ff', bg: 'rgba(0,88,188,0.2)'   },
  COMPLIANCE: { color: '#4ade80', bg: 'rgba(74,222,128,0.1)' },
  COMMUNITY:  { color: '#c084fc', bg: 'rgba(192,132,252,0.1)'},
  CONTENT:    { color: '#34d399', bg: 'rgba(52,211,153,0.1)' },
}

// ── Intel status → dot colour ──────────────────────────────────
const STATUS_COLOR: Record<IntelStatus, string> = {
  HEALTHY:  '#22c55e',
  WARNING:  '#f59e0b',
  CRITICAL: '#ef4444',
}

const intelStatus = ref<IntelStatus>('HEALTHY')
const liveDotColor = computed(() => STATUS_COLOR[intelStatus.value])
const liveDotStyle = computed(() => ({
  background: liveDotColor.value,
  boxShadow: `0 0 8px ${liveDotColor.value}99`,
}))

// ── Number formatter (1500 → "1.5k") ─────────────────────────
function formatStat(n: number): string {
  if (n >= 1000) {
    const v = n / 1000
    return (v % 1 === 0 ? v.toFixed(0) : v.toFixed(1)) + 'k'
  }
  return String(n)
}

// ── Relative date formatter ────────────────────────────────────
function formatRelativeDate(iso: string): string {
  const diff = new Date(iso).getTime() - Date.now()
  const absDays  = Math.abs(Math.round(diff / 86_400_000))
  const absHours = Math.abs(Math.round(diff / 3_600_000))
  const absMins  = Math.abs(Math.round(diff / 60_000))

  if (diff < 0) {
    if (absDays >= 7)  return `${Math.floor(absDays / 7)}W AGO`
    if (absDays >= 1)  return `${absDays}D AGO`
    if (absHours >= 1) return `${absHours}H AGO`
    if (absMins >= 1)  return `${absMins}M AGO`
    return 'JUST NOW'
  }
  if (absDays === 0) return 'TODAY'
  if (absDays === 1) return 'TOMORROW'
  if (absDays < 7) {
    const days = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
    return `NEXT ${days[new Date(iso).getDay()]}`
  }
  return `IN ${Math.round(absDays / 7)}W`
}

// ── Reactive state ────────────────────────────────────────────
interface DisplayNewsItem {
  id: string
  tag: string
  color: string
  bg: string
  time: string
  title: string
  body: string
  url?: string
}

const newsItems = ref<DisplayNewsItem[]>([])

const platformStats = ref([
  { icon: 'schema',      value: '—', label: 'Active Ontologies'  },
  { icon: 'category',    value: '—', label: 'Knowledge Domains'  },
  { icon: 'description', value: '—', label: 'Ingested Documents' },
  { icon: 'query_stats', value: '—', label: 'Monthly Queries'    },
])

function openUrl(url?: string) {
  if (url) window.open(url, '_blank', 'noopener,noreferrer')
}

// ── Load all data in parallel on mount ───────────────────────
onMounted(async () => {
  const [summary, intel, news] = await Promise.all([
    fetchKbSummary(),
    fetchIntelStatus(),
    fetchNews(),
  ])

  platformStats.value = [
    { icon: 'schema',      value: formatStat(summary.activeOntologies),  label: 'Active Ontologies'  },
    { icon: 'category',    value: formatStat(summary.knowledgeDomains),  label: 'Knowledge Domains'  },
    { icon: 'description', value: formatStat(summary.ingestedDocuments), label: 'Ingested Documents' },
    { icon: 'query_stats', value: formatStat(summary.monthlyQueries),    label: 'Monthly Queries'    },
  ]

  intelStatus.value = intel.overall

  newsItems.value = news.map(item => ({
    id:   item.id,
    tag:  item.category,
    time: formatRelativeDate(item.date),
    title: item.title,
    body: item.summary,
    url:  item.url,
    ...(CATEGORY_STYLES[item.category] ?? { color: '#adc6ff', bg: 'rgba(0,88,188,0.2)' }),
  }))
})
</script>

<style scoped>
/* ── Page shell ──────────────────────────────────────────────── */
.login-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: radial-gradient(circle at top left, #004493 0%, #001a41 100%);
  color: #f9f9ff;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* ── Decorative blobs ────────────────────────────────────────── */
.bg-blobs {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}
.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(120px);
}
.blob-tl {
  top: -20%;
  left: -10%;
  width: 60%;
  height: 60%;
  background: rgba(0, 88, 188, 0.2);
}
.blob-br {
  top: 40%;
  right: -5%;
  width: 40%;
  height: 40%;
  background: rgba(158, 61, 0, 0.1);
}

/* ── Hero ────────────────────────────────────────────────────── */
.hero {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 10;
  padding: 48px 24px;
}

.hero-inner {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 48px;
  max-width: 900px;
  width: 100%;
}

/* ── Brand ───────────────────────────────────────────────────── */
.brand {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

.logo-box {
  width: 96px;
  height: 96px;
  background: #ffffff;
  border-radius: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4), 0 0 20px rgba(0, 112, 235, 0.3);
}

.logo-icon {
  font-size: 48px;
  color: #0058bc;
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 48;
}

.brand-name {
  font-size: clamp(48px, 8vw, 96px);
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.05;
  margin: 0;
  color: #f9f9ff;
}

/* ── Welcome ─────────────────────────────────────────────────── */
.welcome {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.welcome-heading {
  font-size: clamp(32px, 5vw, 56px);
  font-weight: 300;
  color: #adc6ff;
  margin: 0;
  line-height: 1.1;
}

.welcome-sub {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
  max-width: 480px;
  line-height: 1.6;
}

/* ── CTA ─────────────────────────────────────────────────────── */
.cta-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

.btn-signin {
  display: inline-flex;
  align-items: center;
  gap: 16px;
  padding: 22px 48px;
  background: #ffffff;
  color: #001a41;
  font-family: inherit;
  font-size: 22px;
  font-weight: 600;
  letter-spacing: -0.01em;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
  transition: background 150ms ease, transform 150ms ease;
}

.btn-signin:hover:not(:disabled) {
  background: #e6e8f3;
  transform: scale(1.04);
}

.btn-signin:active:not(:disabled) {
  transform: scale(0.97);
}

.btn-signin:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.btn-arrow {
  font-size: 24px;
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
  transition: transform 150ms ease;
}

.btn-signin:hover .btn-arrow {
  transform: translateX(4px);
}

.legal-note {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.35);
  margin: 0;
}

.error-alert {
  padding: 12px 20px;
  background: rgba(186, 26, 26, 0.25);
  border: 1px solid rgba(186, 26, 26, 0.4);
  border-radius: 12px;
  font-size: 14px;
  color: #ffb4ab;
  max-width: 420px;
  margin: 0;
}

/* ── News sidebar ────────────────────────────────────────────── */
.news-sidebar {
  display: none;
  position: fixed;
  right: 32px;
  top: 32px;
  bottom: 148px; /* footer height (~106px) + gap (42px) */
  width: 300px;
  z-index: 20;
  flex-direction: column;
  gap: 16px;
}

.news-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 8px;
}

.intel-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #adc6ff;
}

.live-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
  transition: background 300ms ease, box-shadow 300ms ease;
}

.news-list {
  border-radius: 24px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  overflow-y: auto;
  flex: 1;
}

/* Scrollbar */
.news-list::-webkit-scrollbar { width: 4px; }
.news-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
}

.news-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  cursor: pointer;
}

.news-item:last-child {
  padding-bottom: 0;
  border-bottom: none;
}

.news-item--linked {
  cursor: pointer;
}

.news-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.news-tag {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  padding: 2px 8px;
  border-radius: 4px;
}

.news-ago {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.4);
}

.news-title {
  font-size: 13px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  line-height: 1.35;
  transition: color 150ms ease;
}

.news-item:hover .news-title {
  color: #adc6ff;
}

.news-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.55);
  margin: 0;
  line-height: 1.55;
}

/* ── Stats footer ────────────────────────────────────────────── */
.stats-footer {
  position: relative;
  z-index: 10;
  padding: 0 32px 32px;
}

.stats-band {
  border-radius: 24px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  overflow: hidden;
}

.stat-cell {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px 24px;
  background: rgba(0, 26, 65, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: background 150ms ease;
  cursor: default;
}

.stat-cell:hover {
  background: rgba(255, 255, 255, 0.05);
}

.stat-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  background: rgba(0, 88, 188, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #0058bc;
  flex-shrink: 0;
  transition: transform 150ms ease;
}

.stat-cell:hover .stat-icon-wrap {
  transform: scale(1.1);
}

.stat-icon-wrap .material-symbols-outlined {
  font-size: 22px;
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-val {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #f9f9ff;
  line-height: 1;
}

.stat-lbl {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.4);
}

/* ── Glassmorphism utility ───────────────────────────────────── */
.glass {
  backdrop-filter: saturate(180%) blur(25px);
  -webkit-backdrop-filter: saturate(180%) blur(25px);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* ── Animations ──────────────────────────────────────────────── */
@keyframes rise-in {
  from {
    opacity: 0;
    transform: translateY(32px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.4; }
}

.animate-rise-1 {
  animation: rise-in 700ms cubic-bezier(0.22, 1, 0.36, 1) both;
}
.animate-rise-2 {
  animation: rise-in 800ms cubic-bezier(0.22, 1, 0.36, 1) 200ms both;
}
.animate-rise-3 {
  animation: rise-in 900ms cubic-bezier(0.22, 1, 0.36, 1) 450ms both;
}

/* ── Responsive ──────────────────────────────────────────────── */
@media (min-width: 1280px) {
  .news-sidebar {
    display: flex;
  }

  .hero {
    padding-right: 380px;
  }

  .stats-band {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (min-width: 768px) {
  .stats-band {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>
