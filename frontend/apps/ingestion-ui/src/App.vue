<template>
  <div class="ingestion-app">
    <header class="app-header">
      <div class="header-content">
        <div class="title-section">
          <h2 class="display-lg">Ingestion Status</h2>
          <div class="connection-badge" :class="`status--${wsStatus}`">
            <span class="pulse-dot"></span>
            {{ wsStatus }}
          </div>
        </div>
        <p class="body-base subtitle">Monitor and manage document ingestion jobs in real-time.</p>
      </div>
    </header>

    <main class="app-main">
      <div class="content-layout">
        <div class="list-section">
          <JobList />
        </div>
        
        <aside class="upload-section">
          <IngestionForm />
        </aside>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { inject, onMounted, onUnmounted } from 'vue'
import { useIngestionStore } from './stores/ingestion'
import { WebSocketKey, wsClient as localWsClient, type WebSocketService } from './services/websocket'
import JobList from './components/JobList.vue'
import IngestionForm from './components/IngestionForm.vue'

const ingestionStore = useIngestionStore()

// Use the shell's shared connection when embedded; fall back to a local
// connection when running in standalone dev mode (no shell to inject from).
const shellWs = inject<WebSocketService | undefined>(WebSocketKey, undefined)
const ws = shellWs ?? localWsClient
const wsStatus = ws.status

onMounted(() => {
  ingestionStore.loadJobs()

  if (shellWs) {
    // Subscribe to ingestion room on the already-open shell connection.
    shellWs.emit('subscribe', { room: 'ingestion' })
  } else {
    // Standalone mode: open our own connection.
    localWsClient.connect()
  }

  ingestionStore.setupWebSocket(ws)
})

onUnmounted(() => {
  ingestionStore.teardownWebSocket(ws)
  if (!shellWs) {
    localWsClient.disconnect()
  }
})
</script>

<style scoped>
.ingestion-app {
  min-height: 100%;
  background: var(--background, #f9f9ff);
  color: var(--on-background, #181c23);
  font-family: Inter, sans-serif;
}

.app-header {
  padding: 40px 24px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 1px solid var(--outline-variant, #E5E5E7);
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 12px;
}

.display-lg {
  font-size: 32px;
  font-weight: 700;
  margin: 0;
}

.connection-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 999px;
  text-transform: capitalize;
  background: var(--surface-container, #ecedf9);
}

.status--connected { color: #34C759; }
.status--connected .pulse-dot { background: #34C759; box-shadow: 0 0 0 rgba(52, 199, 89, 0.4); animation: pulse-green 2s infinite; }

.status--connecting { color: #007AFF; }
.status--connecting .pulse-dot { background: #007AFF; animation: pulse-blue 2s infinite; }

.status--disconnected { color: #8E8E93; }
.status--disconnected .pulse-dot { background: #8E8E93; }

.status--error { color: #FF3B30; }
.status--error .pulse-dot { background: #FF3B30; }

.pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

@keyframes pulse-green {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(52, 199, 89, 0.7); }
  70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(52, 199, 89, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(52, 199, 89, 0); }
}

@keyframes pulse-blue {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 122, 255, 0.7); }
  70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(0, 122, 255, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 122, 255, 0); }
}

.subtitle {
  color: var(--on-surface-variant, #86868B);
  margin: 0;
}

.app-main {
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px 24px;
}

.content-layout {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 40px;
}

@media (max-width: 1024px) {
  .content-layout {
    grid-template-columns: 1fr;
  }
  .upload-section {
    order: -1;
  }
}
</style>
