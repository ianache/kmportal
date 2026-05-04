<template>
  <div class="domains">

    <!-- ── Explorer ──────────────────────── -->
    <template v-if="view === 'explorer'">
      <div class="page-header">
        <div>
          <h1 class="page-title">Knowledge Domains</h1>
          <p class="page-desc">Explore, manage, and curate your structured information vaults.</p>
        </div>
        <button class="btn-primary" @click="openCreate">
          <svg width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="10" y1="4" x2="10" y2="16"/><line x1="4" y1="10" x2="16" y2="10"/>
          </svg>
          New Domain
        </button>
      </div>

      <div class="filter-bar">
        <div class="filter-chips">
          <button
            v-for="f in filters"
            :key="f.value"
            class="chip"
            :class="{ 'chip--active': activeFilter === f.value }"
            @click="activeFilter = f.value"
          >{{ f.label }}</button>
        </div>
        <div class="search-input-wrap">
          <svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="#86868B" stroke-width="1.8">
            <circle cx="9" cy="9" r="6"/><path d="M17 17l-3.5-3.5"/>
          </svg>
          <input v-model="searchQ" class="search-input" placeholder="Search domains…" />
        </div>
      </div>

      <div v-if="isLoading" class="domain-grid">
        <div v-for="n in 4" :key="n" class="domain-card skeleton">
          <div class="card-top">
            <div class="domain-icon" style="background:#f0f0f0;"></div>
            <div class="badge" style="background:#f0f0f0;color:transparent;">Status</div>
          </div>
          <div class="card-body">
            <div style="height:18px;background:#f0f0f0;border-radius:4px;margin-bottom:8px;"></div>
            <div style="height:36px;background:#f0f0f0;border-radius:4px;"></div>
          </div>
        </div>
      </div>

      <div v-else class="domain-grid">
        <div
          v-for="d in filteredDomains"
          :key="d.id"
          class="domain-card"
          @click="openDomain(d)"
        >
          <!-- Cover image or default icon -->
          <div class="card-cover" :style="d.cover_image ? `background-image:url('${d.cover_image}')` : ''">
            <div v-if="!d.cover_image" class="card-cover-icon">
              <svg width="24" height="24" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M10 2C5.6 2 2 5.6 2 10s3.6 8 8 8 8-3.6 8-8-3.6-8-8-8z"/>
                <path d="M2 10h16M10 2a12 12 0 0 1 0 16M10 2a12 12 0 0 0 0 16"/>
              </svg>
            </div>
            <span class="badge" :class="d.visibility === 'public' ? 'badge--public' : 'badge--private'">
              {{ d.visibility === 'public' ? 'Público' : 'Privado' }}
            </span>
          </div>

          <div class="card-body">
            <h3 class="domain-name">{{ d.name }}</h3>
            <p class="domain-desc">{{ d.description }}</p>
            <div v-if="d.tags?.length" class="tag-row">
              <span v-for="t in d.tags.slice(0, 3)" :key="t" class="tag-chip">{{ t }}</span>
              <span v-if="(d.tags?.length || 0) > 3" class="tag-chip tag-chip--more">+{{ (d.tags?.length || 0) - 3 }}</span>
            </div>
          </div>

          <div class="card-footer">
            <span class="resource-count">
              <svg width="13" height="13" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6">
                <path d="M4 4h12v2H4zM4 9h12v2H4zM4 14h8v2H4z"/>
              </svg>
              {{ d.document_count || 0 }} recursos
            </span>
            <span class="domain-updated">{{ new Date(d.updated_at).toLocaleDateString('es') }}</span>
          </div>
        </div>

        <div v-if="filteredDomains.length === 0" class="empty-state">
          <svg width="40" height="40" viewBox="0 0 20 20" fill="none" stroke="#86868B" stroke-width="1.2">
            <path d="M10 2C5.6 2 2 5.6 2 10s3.6 8 8 8 8-3.6 8-8-3.6-8-8-8z"/>
            <path d="M2 10h16M10 2a12 12 0 0 1 0 16M10 2a12 12 0 0 0 0 16"/>
          </svg>
          <p>No se encontraron dominios</p>
        </div>
      </div>
    </template>

    <!-- ── Create Domain ─────────────────── -->
    <template v-else-if="view === 'create'">
      <div class="page-header">
        <div>
          <button class="btn-ghost btn-back" @click="view = 'explorer'">
            <svg width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 4l-6 6 6 6"/>
            </svg>
            Volver
          </button>
          <h1 class="page-title" style="margin-top:12px">Crear Nuevo Dominio</h1>
          <p class="page-desc">Define un nuevo vault de conocimiento estructurado.</p>
        </div>
      </div>

      <div class="create-layout">

        <!-- LEFT: Image + Domain Details -->
        <div class="form-main">

          <!-- Section: Imagen Representativa -->
          <div class="form-card">
            <h2 class="section-title">Imagen Representativa</h2>

            <!-- Drop zone (hidden when image loaded) -->
            <div
              v-if="!imageDataUrl"
              class="upload-zone"
              :class="{ 'upload-zone--over': isDragOver }"
              @dragover.prevent="isDragOver = true"
              @dragleave.prevent="isDragOver = false"
              @drop.prevent="onImageDrop"
              @click="triggerFileInput"
            >
              <input ref="fileInputRef" type="file" accept="image/png,image/jpeg,image/webp" hidden @change="onImageSelect" />
              <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round">
                <rect x="3" y="3" width="18" height="18" rx="3"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <polyline points="21,15 16,10 5,21"/>
              </svg>
              <p class="upload-label">Arrastra una imagen o <u @click.stop="triggerFileInput">selecciona un archivo</u></p>
              <p class="upload-hint">PNG, JPG, WebP · máx. 5 MB</p>
            </div>

            <!-- Image preview + crop/rotate -->
            <div v-else class="image-editor">
              <!-- Crop frame -->
              <div
                class="crop-container"
                ref="cropContainerRef"
                @pointerdown="onCropPointerDown"
                @pointermove="onCropPointerMove"
                @pointerup="onCropPointerUp"
                @pointercancel="onCropPointerUp"
              >
                <img
                  ref="previewImgRef"
                  :src="imageDataUrl"
                  class="crop-img"
                  :style="{
                    transform: `rotate(${imageRotation}deg) translate(${imgOffsetX}px, ${imgOffsetY}px)`,
                    transformOrigin: 'center center'
                  }"
                  draggable="false"
                />
                <!-- Dark overlay with transparent crop rect -->
                <div class="crop-overlay">
                  <div
                    class="crop-rect"
                    :style="{
                      left: `${cropRect.x}px`,
                      top:  `${cropRect.y}px`,
                      width: `${cropRect.w}px`,
                      height: `${cropRect.h}px`,
                    }"
                  >
                    <div class="crop-handle crop-handle--tl" data-handle="tl"></div>
                    <div class="crop-handle crop-handle--tr" data-handle="tr"></div>
                    <div class="crop-handle crop-handle--bl" data-handle="bl"></div>
                    <div class="crop-handle crop-handle--br" data-handle="br"></div>
                  </div>
                </div>
              </div>

              <!-- Toolbar -->
              <div class="image-toolbar">
                <button class="tool-btn" title="Rotar izquierda" @click="rotateImage(-90)">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="1,4 1,10 7,10"/>
                    <path d="M3.51 15a9 9 0 1 0 .49-3.7"/>
                  </svg>
                </button>
                <button class="tool-btn" title="Rotar derecha" @click="rotateImage(90)">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="23,4 23,10 17,10"/>
                    <path d="M20.49 15a9 9 0 1 1-.49-3.7"/>
                  </svg>
                </button>
                <button class="tool-btn tool-btn--danger" title="Eliminar imagen" @click="clearImage">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3,6 5,6 21,6"/>
                    <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
                    <path d="M10 11v6M14 11v6"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- Section: Detalles del Dominio -->
          <div class="form-card">
            <div class="section-header">
              <h2 class="section-title">Detalles del Dominio</h2>
              <!-- Language tabs -->
              <div class="lang-tabs">
                <button
                  class="lang-tab"
                  :class="{ 'lang-tab--active': activeLang === 'es' }"
                  @click="activeLang = 'es'"
                >
                  <span class="lang-flag">🇪🇸</span> ES
                </button>
                <button
                  class="lang-tab"
                  :class="{ 'lang-tab--active': activeLang === 'en' }"
                  @click="activeLang = 'en'"
                >
                  <span class="lang-flag">🇬🇧</span> EN
                </button>
              </div>
            </div>

            <!-- ES fields -->
            <template v-if="activeLang === 'es'">
              <div class="field">
                <label class="field-label">Nombre <span class="required">*</span></label>
                <input
                  v-model="form.name_es"
                  class="field-input"
                  :class="{ 'field-input--error': showErrors && !form.name_es.trim() }"
                  placeholder="Ej. Inteligencia Artificial"
                />
                <span v-if="showErrors && !form.name_es.trim()" class="field-error">El nombre es requerido</span>
              </div>
              <div class="field">
                <label class="field-label">Descripción</label>
                <textarea
                  v-model="form.description_es"
                  class="field-input field-textarea"
                  placeholder="Describe el alcance y propósito de este dominio de conocimiento…"
                  rows="3"
                />
              </div>
            </template>

            <!-- EN fields -->
            <template v-else>
              <div class="field">
                <label class="field-label">Name <span class="field-label-hint">(optional)</span></label>
                <input
                  v-model="form.name_en"
                  class="field-input"
                  placeholder="e.g. Artificial Intelligence"
                />
              </div>
              <div class="field">
                <label class="field-label">Description <span class="field-label-hint">(optional)</span></label>
                <textarea
                  v-model="form.description_en"
                  class="field-input field-textarea"
                  placeholder="Describe the scope and purpose of this knowledge domain…"
                  rows="3"
                />
              </div>
            </template>
          </div>
        </div>

        <!-- RIGHT: Settings + Actions -->
        <div class="form-sidebar">

          <!-- Visibility -->
          <div class="form-card">
            <h2 class="section-title">Visibilidad</h2>
            <div class="visibility-options">
              <label class="visibility-option" :class="{ 'visibility-option--active': form.visibility === 'public' }">
                <input type="radio" v-model="form.visibility" value="public" class="sr-only" />
                <div class="visibility-icon">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="2" y1="12" x2="22" y2="12"/>
                    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
                  </svg>
                </div>
                <div class="visibility-text">
                  <span class="visibility-name">Público</span>
                  <span class="visibility-desc">Cualquier usuario puede ver este dominio</span>
                </div>
                <div class="radio-dot" :class="{ 'radio-dot--active': form.visibility === 'public' }"></div>
              </label>

              <label class="visibility-option" :class="{ 'visibility-option--active': form.visibility === 'private' }">
                <input type="radio" v-model="form.visibility" value="private" class="sr-only" />
                <div class="visibility-icon">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                  </svg>
                </div>
                <div class="visibility-text">
                  <span class="visibility-name">Privado</span>
                  <span class="visibility-desc">Solo usuarios con acceso pueden verlo</span>
                </div>
                <div class="radio-dot" :class="{ 'radio-dot--active': form.visibility === 'private' }"></div>
              </label>
            </div>
          </div>

          <!-- Tags -->
          <div class="form-card">
            <h2 class="section-title">Etiquetas</h2>
            <div class="field">
              <div class="tag-input-wrap">
                <div class="tag-chips-inline">
                  <span v-for="(t, i) in form.tags" :key="t" class="tag-chip tag-chip--removable">
                    {{ t }}
                    <button class="tag-remove" @click="removeTag(i)">✕</button>
                  </span>
                  <input
                    v-model="tagDraft"
                    class="tag-input"
                    placeholder="Agregar etiqueta…"
                    @keydown.enter.prevent="addTag"
                    @keydown.comma.prevent="addTag"
                    @keydown.tab.prevent="addTag"
                    @blur="addTag"
                  />
                </div>
              </div>
              <span class="field-hint">Presiona Enter, coma o Tab para agregar</span>
            </div>
          </div>

          <!-- Flujo de Ingesta -->
          <div class="form-card">
            <h2 class="section-title">Flujo de Ingesta</h2>
            <div class="field">
              <label class="field-label">Flujo de trabajo</label>
              <select v-model="form.ingestion_flow" class="field-input field-select">
                <option value="">— Sin flujo asignado —</option>
                <option v-for="f in ingestionFlows" :key="f.value" :value="f.value">{{ f.label }}</option>
                <option value="__new__">+ Crear Nuevo Flujo…</option>
              </select>
            </div>

            <!-- New flow name input -->
            <div v-if="form.ingestion_flow === '__new__'" class="field" style="margin-top:12px">
              <label class="field-label">Nombre del nuevo flujo</label>
              <input
                v-model="form.new_flow_name"
                class="field-input"
                :placeholder="form.name_es || 'Nombre del dominio'"
              />
              <span class="field-hint">El diseño del flujo se configurará en la sección "Ingestion"</span>
            </div>
          </div>

          <!-- Actions -->
          <div class="form-actions-sticky">
            <button class="btn-ghost btn-full" @click="view = 'explorer'">Cancelar</button>
            <button
              class="btn-primary btn-full"
              :disabled="store.isCreating"
              @click="handleCreate"
            >
              <svg v-if="store.isCreating" class="spinner-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 12a9 9 0 1 1-6.2-8.6"/>
              </svg>
              {{ store.isCreating ? 'Creando…' : 'Guardar Dominio' }}
            </button>

            <p v-if="store.error" class="form-error">{{ store.error }}</p>
          </div>
        </div>
      </div>
    </template>

    <!-- ── Domain Detail ─────────────────── -->
    <template v-else-if="view === 'detail' && activeDomain">
      <div class="page-header">
        <button class="btn-ghost btn-back" @click="view = 'explorer'">
          <svg width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 4l-6 6 6 6"/>
          </svg>
          Todos los Dominios
        </button>

        <div class="detail-header">
          <div
            class="detail-cover"
            :style="activeDomain.cover_image ? `background-image:url('${activeDomain.cover_image}')` : ''"
          >
            <div v-if="!activeDomain.cover_image" class="detail-cover-icon">
              <svg width="28" height="28" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M10 2C5.6 2 2 5.6 2 10s3.6 8 8 8 8-3.6 8-8-3.6-8-8-8z"/>
                <path d="M2 10h16M10 2a12 12 0 0 1 0 16M10 2a12 12 0 0 0 0 16"/>
              </svg>
            </div>
          </div>
          <div class="detail-meta">
            <h1 class="page-title">{{ activeDomain.name }}</h1>
            <p class="page-desc">{{ activeDomain.description }}</p>
            <div class="detail-badges">
              <span class="badge" :class="activeDomain.visibility === 'public' ? 'badge--public' : 'badge--private'">
                {{ activeDomain.visibility === 'public' ? 'Público' : 'Privado' }}
              </span>
              <span v-for="t in (activeDomain.tags || []).slice(0, 4)" :key="t" class="tag-chip">{{ t }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="detail-stats">
        <div class="stat-card">
          <span class="stat-value">{{ activeDomain.document_count || 0 }}</span>
          <span class="stat-label">Documentos</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ activeDomain.embedding_model?.split('-').pop() || '—' }}</span>
          <span class="stat-label">Modelo</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ activeDomain.embedding_dimension || 768 }}</span>
          <span class="stat-label">Dimensiones</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ new Date(activeDomain.updated_at).toLocaleDateString('es') }}</span>
          <span class="stat-label">Actualizado</span>
        </div>
      </div>

      <div class="documents-section">
        <h2 class="section-title" style="font-size:13px;letter-spacing:.04em;text-transform:uppercase;color:#86868B;margin-bottom:16px;">Documentos</h2>
        <div v-if="store.isLoadingDocuments" class="documents-list">
          <div v-for="n in 3" :key="n" class="doc-row skeleton">
            <div style="height:16px;width:40%;background:#f0f0f0;border-radius:4px;"></div>
            <div style="height:14px;width:20%;background:#f0f0f0;border-radius:4px;"></div>
          </div>
        </div>
        <div v-else-if="store.documents.length === 0" class="documents-empty">
          No hay documentos en este dominio todavía.
        </div>
        <div v-else class="documents-list">
          <div v-for="doc in store.documents" :key="doc.id" class="doc-row">
            <div class="doc-info">
              <span class="doc-title">{{ doc.title }}</span>
              <span class="doc-meta">{{ doc.source_type }} · {{ doc.status }}</span>
            </div>
            <span class="doc-date">{{ new Date(doc.created_at).toLocaleDateString('es') }}</span>
          </div>
        </div>
      </div>
    </template>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useDomainsStore } from './stores/domains'
import type { Domain } from './types'

type View = 'explorer' | 'create' | 'detail'

const store = useDomainsStore()
const view = ref<View>('explorer')
const activeFilter = ref('all')
const searchQ = ref('')
const showErrors = ref(false)

// ── Form state ────────────────────────────────────
const activeLang = ref<'es' | 'en'>('es')
const tagDraft = ref('')

const emptyForm = () => ({
  name_es: '',
  description_es: '',
  name_en: '',
  description_en: '',
  tags: [] as string[],
  visibility: 'private' as 'public' | 'private',
  ingestion_flow: '',
  new_flow_name: '',
})

const form = ref(emptyForm())

// ── Image state ───────────────────────────────────
const fileInputRef = ref<HTMLInputElement | null>(null)
const cropContainerRef = ref<HTMLDivElement | null>(null)
const previewImgRef = ref<HTMLImageElement | null>(null)
const imageDataUrl = ref<string | null>(null)
const imageRotation = ref(0)
const isDragOver = ref(false)
const imgOffsetX = ref(0)
const imgOffsetY = ref(0)

// Crop rect (in container-relative px)
const cropRect = ref({ x: 20, y: 20, w: 260, h: 260 })

// Pointer drag state
type DragMode = 'move-img' | 'move-crop' | 'resize-tl' | 'resize-tr' | 'resize-bl' | 'resize-br' | null
const dragMode = ref<DragMode>(null)
const dragStart = ref({ x: 0, y: 0 })
const dragOrigin = ref({ x: 0, y: 0, w: 0, h: 0, ix: 0, iy: 0 })

// ── Ingestion flows mock ──────────────────────────
const ingestionFlows = [
  { value: 'auto_embed', label: 'Automático: Clasificar y embeber' },
  { value: 'manual_review', label: 'Manual: Revisión humana' },
  { value: 'batch_nightly', label: 'Batch: Procesamiento nocturno' },
  { value: 'realtime', label: 'Tiempo real: Stream continuo' },
]

// ── Filters ───────────────────────────────────────
const filters = [
  { label: 'Todos', value: 'all' },
  { label: 'Públicos', value: 'public' },
  { label: 'Privados', value: 'private' },
]

const filteredDomains = computed(() => {
  if (!Array.isArray(store.domains)) return []
  return store.domains.filter((d) => {
    const matchFilter = activeFilter.value === 'all' || d.visibility === activeFilter.value
    const matchSearch = !searchQ.value || d.name.toLowerCase().includes(searchQ.value.toLowerCase())
    return matchFilter && matchSearch
  })
})

const activeDomain = computed(() => store.selectedDomain)
const isLoading = computed(() => store.isLoading)

// ── Navigation ────────────────────────────────────
function openCreate() {
  form.value = emptyForm()
  clearImage()
  showErrors.value = false
  activeLang.value = 'es'
  view.value = 'create'
}

function openDomain(d: Domain) {
  store.selectDomain(d.id)
  view.value = 'detail'
}

// ── Tag input ─────────────────────────────────────
function addTag() {
  const raw = tagDraft.value.replace(/,$/, '').trim()
  if (raw && !form.value.tags.includes(raw)) {
    form.value.tags.push(raw)
  }
  tagDraft.value = ''
}

function removeTag(index: number) {
  form.value.tags.splice(index, 1)
}

// ── Image upload ──────────────────────────────────
function triggerFileInput() {
  fileInputRef.value?.click()
}

function onImageSelect(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) loadImageFile(file)
}

function onImageDrop(e: DragEvent) {
  isDragOver.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file && file.type.startsWith('image/')) loadImageFile(file)
}

function loadImageFile(file: File) {
  const reader = new FileReader()
  reader.onload = (ev) => {
    imageDataUrl.value = ev.target?.result as string
    imageRotation.value = 0
    imgOffsetX.value = 0
    imgOffsetY.value = 0
    nextTick(() => initCropRect())
  }
  reader.readAsDataURL(file)
}

function clearImage() {
  imageDataUrl.value = null
  imageRotation.value = 0
  imgOffsetX.value = 0
  imgOffsetY.value = 0
  if (fileInputRef.value) fileInputRef.value.value = ''
}

function rotateImage(deg: number) {
  imageRotation.value = ((imageRotation.value + deg) + 360) % 360
}

function initCropRect() {
  const c = cropContainerRef.value
  if (!c) return
  const { width, height } = c.getBoundingClientRect()
  const size = Math.min(width, height) * 0.85
  cropRect.value = {
    x: (width - size) / 2,
    y: (height - size) / 2,
    w: size,
    h: size,
  }
}

// ── Crop/drag pointer events ──────────────────────
function onCropPointerDown(e: PointerEvent) {
  const target = e.target as HTMLElement
  const handle = target.dataset.handle
  const c = cropContainerRef.value!
  const rect = c.getBoundingClientRect()
  const px = e.clientX - rect.left
  const py = e.clientY - rect.top

  dragStart.value = { x: e.clientX, y: e.clientY }
  dragOrigin.value = {
    x: cropRect.value.x, y: cropRect.value.y,
    w: cropRect.value.w, h: cropRect.value.h,
    ix: imgOffsetX.value, iy: imgOffsetY.value,
  }

  if (handle === 'tl') dragMode.value = 'resize-tl'
  else if (handle === 'tr') dragMode.value = 'resize-tr'
  else if (handle === 'bl') dragMode.value = 'resize-bl'
  else if (handle === 'br') dragMode.value = 'resize-br'
  else if (target.closest('.crop-rect')) dragMode.value = 'move-crop'
  else dragMode.value = 'move-img'

  c.setPointerCapture(e.pointerId)
}

function onCropPointerMove(e: PointerEvent) {
  if (!dragMode.value) return
  const dx = e.clientX - dragStart.value.x
  const dy = e.clientY - dragStart.value.y
  const o = dragOrigin.value

  if (dragMode.value === 'move-img') {
    imgOffsetX.value = o.ix + dx
    imgOffsetY.value = o.iy + dy
  } else if (dragMode.value === 'move-crop') {
    cropRect.value.x = o.x + dx
    cropRect.value.y = o.y + dy
  } else if (dragMode.value === 'resize-br') {
    cropRect.value.w = Math.max(60, o.w + dx)
    cropRect.value.h = Math.max(60, o.h + dy)
  } else if (dragMode.value === 'resize-tl') {
    cropRect.value.x = o.x + dx
    cropRect.value.y = o.y + dy
    cropRect.value.w = Math.max(60, o.w - dx)
    cropRect.value.h = Math.max(60, o.h - dy)
  } else if (dragMode.value === 'resize-tr') {
    cropRect.value.y = o.y + dy
    cropRect.value.w = Math.max(60, o.w + dx)
    cropRect.value.h = Math.max(60, o.h - dy)
  } else if (dragMode.value === 'resize-bl') {
    cropRect.value.x = o.x + dx
    cropRect.value.w = Math.max(60, o.w - dx)
    cropRect.value.h = Math.max(60, o.h + dy)
  }
}

function onCropPointerUp(_e: PointerEvent) {
  dragMode.value = null
}

// ── Get final cropped image as data URL ───────────
async function getFinalImage(): Promise<string | null> {
  if (!imageDataUrl.value || !cropContainerRef.value || !previewImgRef.value) return null

  return new Promise((resolve) => {
    const img = new Image()
    img.onload = () => {
      const container = cropContainerRef.value!
      const containerRect = container.getBoundingClientRect()
      const imgEl = previewImgRef.value!
      const imgRect = imgEl.getBoundingClientRect()

      // Scale from container-relative crop coords to actual image pixels
      const scaleX = img.naturalWidth / imgRect.width
      const scaleY = img.naturalHeight / imgRect.height

      // Crop rect relative to the rendered image element
      const cropX = (cropRect.value.x - (imgRect.left - containerRect.left)) * scaleX
      const cropY = (cropRect.value.y - (imgRect.top - containerRect.top)) * scaleY
      const cropW = cropRect.value.w * scaleX
      const cropH = cropRect.value.h * scaleY

      const outputSize = 512
      const canvas = document.createElement('canvas')
      canvas.width = outputSize
      canvas.height = outputSize
      const ctx = canvas.getContext('2d')!

      ctx.translate(outputSize / 2, outputSize / 2)
      ctx.rotate((imageRotation.value * Math.PI) / 180)
      ctx.drawImage(img, cropX, cropY, cropW, cropH, -outputSize / 2, -outputSize / 2, outputSize, outputSize)

      resolve(canvas.toDataURL('image/jpeg', 0.85))
    }
    img.src = imageDataUrl.value!
  })
}

// ── Create domain ─────────────────────────────────
async function handleCreate() {
  showErrors.value = true
  if (!form.value.name_es.trim()) return

  // Finalize any pending tag
  if (tagDraft.value.trim()) addTag()

  // Get final image
  const coverImage = await getFinalImage()

  const flowValue = form.value.ingestion_flow === '__new__'
    ? (form.value.new_flow_name.trim() || form.value.name_es)
    : form.value.ingestion_flow || undefined

  try {
    await store.createDomain({
      name: form.value.name_es,
      description: form.value.description_es || undefined,
      name_en: form.value.name_en || undefined,
      description_en: form.value.description_en || undefined,
      tags: form.value.tags,
      visibility: form.value.visibility,
      cover_image: coverImage || undefined,
      ingestion_flow: flowValue,
    })
    view.value = 'explorer'
  } catch {
    // error shown via store.error
  }
}

onMounted(() => {
  store.fetchDomains()
})
</script>

<style scoped>
/* ── Base ─────────────────────────────────────── */
.domains {
  padding: 32px 40px;
  min-height: 100%;
}

/* ── Page header ──────────────────────────────── */
.page-header {
  margin-bottom: 28px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text, #1D1D1F);
  line-height: 1.2;
}

.page-desc {
  font-size: 14px;
  color: var(--text-2, #86868B);
  margin-top: 4px;
}

/* ── Buttons ──────────────────────────────────── */
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--primary, #007AFF);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  padding: 9px 18px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  transition: opacity 0.12s;
  font-family: inherit;
  flex-shrink: 0;
}
.btn-primary:hover { opacity: 0.88; }
.btn-primary:disabled { opacity: 0.55; cursor: not-allowed; }

.btn-ghost {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: transparent;
  color: var(--text-2, #86868B);
  font-size: 14px;
  font-weight: 500;
  padding: 8px 14px;
  border-radius: 8px;
  border: 1px solid var(--border, #E5E5E7);
  cursor: pointer;
  transition: background 0.12s, color 0.12s;
  font-family: inherit;
}
.btn-ghost:hover { background: rgba(0,0,0,0.04); color: var(--text, #1D1D1F); }

.btn-full { width: 100%; justify-content: center; }

/* ── Filter bar ───────────────────────────────── */
.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.filter-chips { display: flex; gap: 6px; }

.chip {
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 500;
  background: var(--surface, #fff);
  border: 1px solid var(--border, #E5E5E7);
  color: var(--text-2, #86868B);
  cursor: pointer;
  transition: background 0.12s, color 0.12s, border-color 0.12s;
  font-family: inherit;
}
.chip:hover { background: rgba(0,0,0,0.04); color: var(--text, #1D1D1F); }
.chip--active { background: rgba(0,122,255,0.1); border-color: #007AFF; color: #007AFF; }

.search-input-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fff;
  border: 1px solid var(--border, #E5E5E7);
  border-radius: 8px;
  padding: 7px 12px;
  min-width: 220px;
}

.search-input {
  border: none;
  outline: none;
  font-size: 14px;
  font-family: inherit;
  color: var(--text, #1D1D1F);
  background: transparent;
  flex: 1;
}

/* ── Domain grid ──────────────────────────────── */
.domain-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.domain-card {
  background: #fff;
  border: 1px solid var(--border, #E5E5E7);
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: box-shadow 0.15s, transform 0.15s;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04), 0 4px 16px rgba(0,0,0,0.06);
}
.domain-card:hover { box-shadow: 0 4px 24px rgba(0,0,0,0.10); transform: translateY(-1px); }

.card-cover {
  height: 100px;
  background: rgba(0,122,255,0.07);
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  padding: 10px 12px;
  flex-shrink: 0;
}
.card-cover-icon {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #007AFF;
  opacity: 0.4;
}
.card-cover { position: relative; }

.card-body { padding: 16px 16px 8px; flex: 1; display: flex; flex-direction: column; gap: 6px; }

.domain-name { font-size: 15px; font-weight: 600; color: var(--text, #1D1D1F); letter-spacing: -0.01em; }

.domain-desc {
  font-size: 13px;
  color: var(--text-2, #86868B);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.tag-row { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 4px; }

.tag-chip {
  font-size: 11px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(0,0,0,0.06);
  color: var(--text-2, #636366);
}
.tag-chip--more { background: transparent; color: var(--text-2, #86868B); }
.tag-chip--removable { display: inline-flex; align-items: center; gap: 4px; }

.tag-remove {
  background: none;
  border: none;
  cursor: pointer;
  color: inherit;
  font-size: 10px;
  padding: 0;
  line-height: 1;
  opacity: 0.7;
}
.tag-remove:hover { opacity: 1; }

.card-footer {
  padding: 8px 16px 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid var(--border, #E5E5E7);
  margin-top: auto;
}

.resource-count {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-2, #86868B);
  font-weight: 500;
}

.domain-updated { font-size: 12px; color: var(--text-2, #86868B); }

/* badges */
.badge { font-size: 11px; font-weight: 600; padding: 3px 8px; border-radius: 999px; letter-spacing: 0.02em; }
.badge--public  { background: rgba(0,122,255,0.12);  color: #005EC4; }
.badge--private { background: rgba(134,134,139,0.12); color: #636366; }

/* ── Empty state ──────────────────────────────── */
.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 64px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--text-2, #86868B);
  font-size: 14px;
}

/* ── Create layout ────────────────────────────── */
.create-layout {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 24px;
  align-items: start;
}

.form-main { display: flex; flex-direction: column; gap: 20px; }
.form-sidebar { display: flex; flex-direction: column; gap: 16px; position: sticky; top: 24px; }

.form-card {
  background: #fff;
  border: 1px solid var(--border, #E5E5E7);
  border-radius: 12px;
  padding: 20px 24px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.section-title {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--text-2, #86868B);
}

/* ── Language tabs ────────────────────────────── */
.lang-tabs { display: flex; gap: 4px; }

.lang-tab {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  border: 1px solid var(--border, #E5E5E7);
  background: transparent;
  color: var(--text-2, #86868B);
  cursor: pointer;
  transition: all 0.12s;
  font-family: inherit;
}
.lang-tab--active {
  background: var(--primary, #007AFF);
  border-color: var(--primary, #007AFF);
  color: #fff;
}
.lang-flag { font-size: 14px; }

/* ── Fields ───────────────────────────────────── */
.field { display: flex; flex-direction: column; gap: 5px; }

.field-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text, #1D1D1F);
}

.field-label-hint { font-size: 12px; color: var(--text-2, #86868B); font-weight: 400; }

.required { color: var(--primary, #007AFF); }

.field-input {
  border: 1px solid var(--border, #E5E5E7);
  border-radius: 8px;
  padding: 9px 12px;
  font-size: 14px;
  font-family: inherit;
  color: var(--text, #1D1D1F);
  background: #F5F5F7;
  outline: none;
  transition: border-color 0.12s, box-shadow 0.12s;
  width: 100%;
  box-sizing: border-box;
}
.field-input:focus { border-color: var(--primary, #007AFF); box-shadow: 0 0 0 3px rgba(0,122,255,0.12); background: #fff; }
.field-input--error { border-color: #FF3B30 !important; }

.field-textarea { resize: vertical; min-height: 80px; }
.field-select { appearance: none; cursor: pointer; }

.field-hint { font-size: 12px; color: var(--text-2, #86868B); }
.field-error { font-size: 12px; color: #FF3B30; font-weight: 500; }

/* ── Upload zone ──────────────────────────────── */
.upload-zone {
  border: 2px dashed var(--border, #E5E5E7);
  border-radius: 10px;
  padding: 36px 24px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: border-color 0.12s, background 0.12s;
  color: #86868B;
}
.upload-zone:hover,
.upload-zone--over { border-color: #007AFF; background: rgba(0,122,255,0.04); }

.upload-label { font-size: 14px; color: var(--text, #1D1D1F); }
.upload-label u { color: #007AFF; }
.upload-hint { font-size: 12px; color: #86868B; }

/* ── Image editor ─────────────────────────────── */
.image-editor { display: flex; flex-direction: column; gap: 12px; }

.crop-container {
  position: relative;
  width: 100%;
  height: 300px;
  background: #111;
  border-radius: 10px;
  overflow: hidden;
  cursor: crosshair;
  user-select: none;
}

.crop-img {
  position: absolute;
  top: 50%;
  left: 50%;
  transform-origin: center center;
  max-width: none;
  max-height: none;
  width: auto;
  height: 100%;
  translate: -50% -50%;
  pointer-events: none;
}

.crop-overlay {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.crop-rect {
  position: absolute;
  box-shadow: 0 0 0 9999px rgba(0,0,0,0.55);
  border: 2px solid rgba(255,255,255,0.9);
  cursor: move;
  pointer-events: all;
}

.crop-handle {
  position: absolute;
  width: 10px;
  height: 10px;
  background: #fff;
  border-radius: 2px;
  pointer-events: all;
}
.crop-handle--tl { top: -5px; left: -5px; cursor: nw-resize; }
.crop-handle--tr { top: -5px; right: -5px; cursor: ne-resize; }
.crop-handle--bl { bottom: -5px; left: -5px; cursor: sw-resize; }
.crop-handle--br { bottom: -5px; right: -5px; cursor: se-resize; }

.image-toolbar {
  display: flex;
  gap: 8px;
}

.tool-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 8px;
  border: 1px solid var(--border, #E5E5E7);
  background: #fff;
  color: var(--text-2, #636366);
  cursor: pointer;
  transition: background 0.12s, color 0.12s;
}
.tool-btn:hover { background: #F5F5F7; color: var(--text, #1D1D1F); }
.tool-btn--danger:hover { background: rgba(255,59,48,0.08); color: #FF3B30; border-color: rgba(255,59,48,0.3); }

/* ── Visibility options ───────────────────────── */
.visibility-options { display: flex; flex-direction: column; gap: 8px; }

.visibility-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 10px;
  border: 1.5px solid var(--border, #E5E5E7);
  cursor: pointer;
  transition: border-color 0.12s, background 0.12s;
}
.visibility-option:hover { background: #F5F5F7; }
.visibility-option--active { border-color: var(--primary, #007AFF); background: rgba(0,122,255,0.04); }

.visibility-icon { color: var(--text-2, #86868B); flex-shrink: 0; }
.visibility-option--active .visibility-icon { color: var(--primary, #007AFF); }

.visibility-text { flex: 1; display: flex; flex-direction: column; gap: 1px; }
.visibility-name { font-size: 13px; font-weight: 600; color: var(--text, #1D1D1F); }
.visibility-desc { font-size: 11px; color: var(--text-2, #86868B); }

.radio-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 1.5px solid var(--border, #C7C7CC);
  flex-shrink: 0;
  transition: border-color 0.12s;
}
.radio-dot--active {
  border-color: var(--primary, #007AFF);
  background: var(--primary, #007AFF);
  box-shadow: inset 0 0 0 3px #fff;
}

.sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border-width: 0; }

/* ── Tag input ────────────────────────────────── */
.tag-input-wrap {
  border: 1px solid var(--border, #E5E5E7);
  border-radius: 8px;
  padding: 6px 10px;
  background: #F5F5F7;
  transition: border-color 0.12s, box-shadow 0.12s;
  cursor: text;
}
.tag-input-wrap:focus-within { border-color: var(--primary, #007AFF); box-shadow: 0 0 0 3px rgba(0,122,255,0.12); background: #fff; }

.tag-chips-inline { display: flex; flex-wrap: wrap; gap: 4px; align-items: center; }

.tag-input {
  border: none;
  outline: none;
  font-size: 14px;
  font-family: inherit;
  color: var(--text, #1D1D1F);
  background: transparent;
  flex: 1;
  min-width: 80px;
  padding: 2px 0;
}

/* ── Sticky actions ───────────────────────────── */
.form-actions-sticky {
  background: #fff;
  border: 1px solid var(--border, #E5E5E7);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}

.form-error {
  font-size: 12px;
  color: #FF3B30;
  text-align: center;
  padding: 4px 0;
}

.spinner-icon { animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Detail view ──────────────────────────────── */
.detail-header { display: flex; gap: 16px; align-items: flex-start; margin-top: 16px; }

.detail-cover {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  background: rgba(0,122,255,0.07);
  background-size: cover;
  background-position: center;
  flex-shrink: 0;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}
.detail-cover-icon { color: #007AFF; opacity: 0.5; }

.detail-meta { flex: 1; }

.detail-badges { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; align-items: center; }

.detail-stats {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 16px;
  margin-top: 24px;
}

.stat-card {
  background: #fff;
  border: 1px solid var(--border, #E5E5E7);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}

.stat-value { font-size: 26px; font-weight: 700; letter-spacing: -0.02em; color: var(--text, #1D1D1F); }
.stat-label { font-size: 12px; font-weight: 500; color: var(--text-2, #86868B); letter-spacing: 0.02em; }

/* ── Documents section ────────────────────────── */
.documents-section { margin-top: 32px; }

.documents-list {
  background: #fff;
  border: 1px solid var(--border, #E5E5E7);
  border-radius: 12px;
  overflow: hidden;
}

.doc-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  border-bottom: 1px solid var(--border, #E5E5E7);
}
.doc-row:last-child { border-bottom: none; }
.doc-row:hover { background: rgba(0,0,0,0.02); }
.doc-row.skeleton { background: #f5f5f5; pointer-events: none; }

.doc-info { display: flex; flex-direction: column; gap: 2px; }
.doc-title { font-size: 14px; font-weight: 500; color: var(--text, #1D1D1F); }
.doc-meta { font-size: 12px; color: var(--text-2, #86868B); }
.doc-date { font-size: 12px; color: var(--text-2, #86868B); }

.documents-empty {
  padding: 40px;
  text-align: center;
  color: var(--text-2, #86868B);
  font-size: 14px;
  background: #fff;
  border: 1px solid var(--border, #E5E5E7);
  border-radius: 12px;
}

/* ── Skeleton ─────────────────────────────────── */
.skeleton { animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
</style>
