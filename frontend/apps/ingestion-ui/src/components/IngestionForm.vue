<template>
  <BaseCard class="ingestion-form-card">
    <h3 class="form-title">Nueva Ingesta</h3>

    <div class="form-body">
      <!-- Domain selector -->
      <div class="form-group">
        <label class="field-label">Dominio Objetivo</label>
        <select v-model="selectedDomainId" class="field-select" @change="onDomainChange">
          <option value="" disabled>Selecciona un dominio</option>
          <option v-for="d in domains" :key="d.id" :value="d.id">{{ d.name }}</option>
        </select>
      </div>

      <!-- Mode toggle -->
      <div class="mode-toggle-row">
        <span class="mode-label">Activar Clasificación Ontológica (Alta Fidelidad)</span>
        <button
          type="button"
          class="toggle-btn"
          :class="{ active: isSemanticMode }"
          :aria-checked="isSemanticMode"
          role="switch"
          @click="isSemanticMode = !isSemanticMode"
        >
          <span class="toggle-thumb" />
        </button>
      </div>

      <!-- File drop zone -->
      <div class="form-group">
        <label class="field-label">Archivo (PDF / TXT)</label>
        <div
          class="drop-zone"
          :class="{ 'is-dragging': isDragging, 'has-file': !!selectedFile }"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="handleDrop"
          @click="fileInputRef?.click()"
        >
          <input
            ref="fileInputRef"
            type="file"
            accept=".pdf,.txt"
            class="hidden-input"
            @change="handleFileInput"
          />
          <template v-if="selectedFile">
            <span class="file-chip">{{ selectedFile.name }}</span>
            <span class="file-size">{{ formatSize(selectedFile.size) }}</span>
          </template>
          <template v-else>
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/>
              <line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
            <span class="drop-hint">Click o arrastra un archivo PDF / TXT</span>
          </template>
          <span v-if="isExtracting" class="extracting-badge">Extrayendo texto…</span>
        </div>
      </div>

      <!-- Extraction preview -->
      <div class="form-group">
        <label class="field-label">Contenido Extraído</label>
        <textarea
          v-model="extractedContent"
          class="content-textarea"
          :placeholder="extractPlaceholder"
          rows="7"
        />
      </div>

      <!-- Semantic section -->
      <template v-if="isSemanticMode">
        <div class="semantic-section">
          <div class="semantic-header">
            <span class="semantic-badge">Semántico</span>
            <span class="semantic-sub">Campos requeridos para indexación ontológica</span>
          </div>

          <!-- OWL class selector -->
          <div class="form-group">
            <label class="field-label">Clase OWL <span class="required-star">*</span></label>
            <select v-model="owlClass" class="field-select">
              <option value="" disabled>
                {{ owlClasses.length ? 'Selecciona una clase' : 'Cargando clases…' }}
              </option>
              <option v-for="cls in owlClasses" :key="cls.id" :value="cls.label">
                {{ cls.label }}
              </option>
            </select>
          </div>

          <!-- Governance level -->
          <div class="form-group">
            <label class="field-label">Nivel de Gobernanza</label>
            <div class="radio-group">
              <label v-for="level in governanceLevels" :key="level" class="radio-option">
                <input type="radio" v-model="governanceLevel" :value="level" />
                {{ level }}
              </label>
            </div>
          </div>

          <!-- Property manager -->
          <div class="form-group">
            <div class="prop-header">
              <label class="field-label">Propiedades del Grafo</label>
              <button type="button" class="add-prop-btn" @click="addProperty">+ Añadir</button>
            </div>
            <div v-if="graphProperties.length" class="prop-list">
              <div v-for="(prop, i) in graphProperties" :key="i" class="prop-row">
                <input
                  v-model="prop.key"
                  class="prop-input"
                  placeholder="clave"
                  @keydown.enter.prevent="addProperty"
                />
                <span class="prop-sep">:</span>
                <input
                  v-model="prop.value"
                  class="prop-input"
                  placeholder="valor"
                  @keydown.enter.prevent="addProperty"
                />
                <button type="button" class="remove-prop-btn" @click="removeProperty(i)">✕</button>
              </div>
            </div>
            <p v-else class="prop-empty">Sin propiedades adicionales</p>
          </div>
        </div>
      </template>

      <!-- Status feedback -->
      <div v-if="submitPhase === 'processing'" class="feedback-bar feedback-bar--processing">
        <span class="feedback-spinner" />
        {{ isSemanticMode
          ? 'Validando integridad en Grafo y Vectores…'
          : 'Indexando fragmentos…' }}
      </div>

      <div v-if="submitPhase === 'success'" class="feedback-bar feedback-bar--success">
        Ingesta completada correctamente.
      </div>

      <div v-if="submitPhase === 'error'" class="feedback-bar feedback-bar--error">
        {{ errorMessage }}
      </div>

      <!-- Submit -->
      <BaseButton
        primary
        :disabled="!canSubmit"
        :loading="submitPhase === 'processing'"
        @click="submit"
      >
        {{ isSemanticMode ? 'Ingesta Semántica Atómica' : 'Quick RAG' }}
      </BaseButton>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import BaseCard from 'shell/BaseCard'
import BaseButton from 'shell/BaseButton'
import { ingestionApi } from '../services/ingestionApi'
import type { OWLClass } from '../services/ingestionApi'

const domains = ref<any[]>([])
const selectedDomainId = ref('')
const isSemanticMode = ref(false)

const selectedFile = ref<File | null>(null)
const isDragging = ref(false)
const isExtracting = ref(false)
const extractedContent = ref('')
const fileInputRef = ref<HTMLInputElement | null>(null)

const owlClass = ref('')
const owlClasses = ref<OWLClass[]>([])
const governanceLevels = ['PÚBLICO', 'INTERNO', 'CONFIDENCIAL'] as const
const governanceLevel = ref<typeof governanceLevels[number]>('CONFIDENCIAL')
const graphProperties = ref<{ key: string; value: string }[]>([])

const submitPhase = ref<'idle' | 'processing' | 'success' | 'error'>('idle')
const errorMessage = ref('')

const extractPlaceholder = computed(() =>
  selectedFile.value
    ? 'El texto extraído aparecerá aquí…'
    : 'Sube un archivo para extraer el texto automáticamente, o escribe aquí directamente.'
)

const canSubmit = computed(() => {
  if (!selectedDomainId.value) return false
  if (!extractedContent.value.trim()) return false
  if (submitPhase.value === 'processing') return false
  if (isSemanticMode.value && !owlClass.value) return false
  return true
})

onMounted(async () => {
  try {
    domains.value = await ingestionApi.getDomains()
  } catch {
    // non-blocking
  }
})

async function onDomainChange() {
  if (isSemanticMode.value && selectedDomainId.value) {
    await loadOWLClasses()
  }
}

watch(isSemanticMode, async (active) => {
  if (active && selectedDomainId.value) {
    await loadOWLClasses()
  }
})

async function loadOWLClasses() {
  try {
    owlClasses.value = await ingestionApi.getOWLClasses(selectedDomainId.value)
  } catch {
    owlClasses.value = []
  }
}

function handleFileInput(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files?.[0]) processFile(input.files[0])
}

function handleDrop(event: DragEvent) {
  isDragging.value = false
  const file = event.dataTransfer?.files[0]
  if (file) processFile(file)
}

async function processFile(file: File) {
  selectedFile.value = file
  extractedContent.value = ''
  isExtracting.value = true
  try {
    const result = await ingestionApi.extractFile(file)
    extractedContent.value = result.content
  } catch {
    // leave textarea empty; user can type manually
  } finally {
    isExtracting.value = false
  }
}

function addProperty() {
  graphProperties.value.push({ key: '', value: '' })
}

function removeProperty(index: number) {
  graphProperties.value.splice(index, 1)
}

function formatSize(bytes: number) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

async function submit() {
  if (!canSubmit.value) return
  submitPhase.value = 'processing'
  errorMessage.value = ''

  try {
    const sourceName = selectedFile.value?.name ?? 'manual'

    if (isSemanticMode.value) {
      const props: Record<string, string> = {}
      graphProperties.value.forEach(({ key, value }) => {
        if (key.trim()) props[key.trim()] = value
      })
      await ingestionApi.ingestSemantic(selectedDomainId.value, {
        content: extractedContent.value,
        metadata: {
          owl_class: owlClass.value,
          governance_level: governanceLevel.value,
          source_ref: sourceName
        },
        graph_properties: props
      })
    } else {
      await ingestionApi.ingestVector(
        selectedDomainId.value,
        extractedContent.value,
        sourceName
      )
    }

    submitPhase.value = 'success'
    resetAfterSuccess()
  } catch (err) {
    submitPhase.value = 'error'
    const msg = err instanceof Error ? err.message : 'Error desconocido'
    errorMessage.value = msg.includes('Neo4j') || msg.includes('ontol')
      ? 'Error de consistencia ontológica. El documento no fue indexado.'
      : msg
  }
}

function resetAfterSuccess() {
  selectedFile.value = null
  extractedContent.value = ''
  owlClass.value = ''
  governanceLevel.value = 'CONFIDENCIAL'
  graphProperties.value = []
  setTimeout(() => { submitPhase.value = 'idle' }, 3000)
}
</script>

<style scoped>
.ingestion-form-card {
  padding: 24px;
  position: sticky;
  top: 120px;
}

.form-title {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 24px;
  color: var(--on-surface, #1D1D1F);
}

.form-body {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field-label {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--on-surface-variant, #86868B);
}

.required-star {
  color: #FF3B30;
}

.field-select {
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid var(--outline-variant, #E5E5E7);
  background: var(--surface-container-lowest, #fff);
  font-size: 15px;
  outline: none;
  color: var(--on-surface, #1D1D1F);
  transition: border-color 0.15s;
}
.field-select:focus {
  border-color: var(--primary, #007AFF);
}

/* Mode toggle */
.mode-toggle-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 14px;
  background: var(--surface-container-low, #f1f3fe);
  border-radius: 12px;
}
.mode-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--on-surface, #1D1D1F);
  flex: 1;
}
.toggle-btn {
  position: relative;
  width: 44px;
  height: 24px;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  background: var(--outline-variant, #C7C7CC);
  transition: background 0.2s;
  flex-shrink: 0;
}
.toggle-btn.active {
  background: var(--primary, #007AFF);
}
.toggle-thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 1px 3px rgba(0,0,0,0.25);
  transition: transform 0.2s;
}
.toggle-btn.active .toggle-thumb {
  transform: translateX(20px);
}

/* Drop zone */
.drop-zone {
  border: 2px dashed var(--outline-variant, #E5E5E7);
  border-radius: 12px;
  padding: 24px 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--surface-container-low, #f1f3fe);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: var(--on-surface-variant, #86868B);
  min-height: 80px;
  justify-content: center;
}
.drop-zone:hover,
.drop-zone.is-dragging {
  border-color: var(--primary, #007AFF);
  background: rgba(0, 122, 255, 0.05);
}
.drop-zone.has-file {
  border-style: solid;
  border-color: var(--primary, #007AFF);
}
.hidden-input { display: none; }
.drop-hint { font-size: 13px; }
.file-chip {
  font-size: 13px;
  font-weight: 600;
  color: var(--on-surface, #1D1D1F);
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.file-size { font-size: 11px; }
.extracting-badge {
  font-size: 11px;
  font-weight: 600;
  color: var(--primary, #007AFF);
  animation: pulse-text 1.2s ease-in-out infinite;
}
@keyframes pulse-text {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

/* Content textarea */
.content-textarea {
  width: 100%;
  box-sizing: border-box;
  resize: vertical;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid var(--outline-variant, #E5E5E7);
  background: var(--surface-container-lowest, #fff);
  font-size: 13px;
  line-height: 1.6;
  color: var(--on-surface, #1D1D1F);
  font-family: inherit;
  outline: none;
  transition: border-color 0.15s;
}
.content-textarea:focus {
  border-color: var(--primary, #007AFF);
}

/* Semantic section */
.semantic-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid var(--primary, #007AFF);
  background: rgba(0, 122, 255, 0.04);
}
.semantic-header {
  display: flex;
  align-items: center;
  gap: 10px;
}
.semantic-badge {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #fff;
  background: var(--primary, #007AFF);
  padding: 2px 8px;
  border-radius: 999px;
}
.semantic-sub {
  font-size: 12px;
  color: var(--on-surface-variant, #86868B);
}

/* Radio group */
.radio-group {
  display: flex;
  gap: 20px;
}
.radio-option {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  cursor: pointer;
  color: var(--on-surface, #1D1D1F);
}

/* Property manager */
.prop-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.add-prop-btn {
  font-size: 12px;
  font-weight: 600;
  color: var(--primary, #007AFF);
  background: none;
  border: none;
  cursor: pointer;
  padding: 2px 6px;
}
.add-prop-btn:hover { opacity: 0.7; }
.prop-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.prop-row {
  display: flex;
  align-items: center;
  gap: 6px;
}
.prop-input {
  flex: 1;
  padding: 7px 10px;
  border-radius: 8px;
  border: 1px solid var(--outline-variant, #E5E5E7);
  font-size: 13px;
  background: var(--surface-container-lowest, #fff);
  color: var(--on-surface, #1D1D1F);
  outline: none;
}
.prop-input:focus { border-color: var(--primary, #007AFF); }
.prop-sep { color: var(--on-surface-variant, #86868B); font-weight: 700; }
.remove-prop-btn {
  background: none;
  border: none;
  color: var(--on-surface-variant, #86868B);
  cursor: pointer;
  font-size: 12px;
  padding: 4px;
}
.remove-prop-btn:hover { color: #FF3B30; }
.prop-empty {
  font-size: 12px;
  color: var(--on-surface-variant, #86868B);
  margin: 0;
}

/* Feedback bars */
.feedback-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
}
.feedback-bar--processing {
  background: rgba(0, 122, 255, 0.08);
  color: var(--primary, #007AFF);
}
.feedback-bar--success {
  background: rgba(52, 199, 89, 0.1);
  color: #1A7A3A;
}
.feedback-bar--error {
  background: rgba(255, 59, 48, 0.08);
  color: #C0392B;
}
.feedback-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

.form-body :deep(button[class*="base-btn"]),
.form-body :deep(button) {
  width: 100%;
}
</style>
