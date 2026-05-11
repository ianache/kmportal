<template>
  <aside class="owl-panel">
    <!-- Header -->
    <div class="panel-header">
      <h4 class="panel-title">
        {{ store.panelMode === 'create' ? 'New OWL Class Definition' : 'Edit OWL Class' }}
      </h4>
      <button class="close-btn" @click="cancel" title="Close">✕</button>
    </div>

    <div class="panel-body">
      <!-- ── Section 1: Core Identification ─────────────────────────────── -->
      <section class="panel-section">
        <h5 class="section-title">Core Identification</h5>

        <label class="field-label">Label <span class="req">*</span></label>
        <input
          ref="labelInputRef"
          class="field-input"
          v-model="form.label"
          placeholder="e.g. ServiceRequest"
          @input="autoUri"
        />

        <label class="field-label">URI</label>
        <input
          class="field-input"
          v-model="form.uri"
          placeholder="http://km.local/ontology#..."
        />

        <label class="field-label">Comment</label>
        <textarea
          class="field-input"
          rows="2"
          v-model="form.comment"
          placeholder="Optional description"
        />
      </section>

      <!-- ── Section 2: Hierarchy & Logic ───────────────────────────────── -->
      <section class="panel-section">
        <h5 class="section-title">Hierarchy &amp; Logic</h5>

        <!-- Subclass Of -->
        <div class="sub-label-row">
          <label class="field-label">Subclass Of</label>
          <button class="add-btn" @click="showSubclassDropdown = !showSubclassDropdown">+ Add</button>
        </div>
        <div v-if="showSubclassDropdown" class="dropdown-list">
          <input class="dropdown-search" v-model="subclassSearch" placeholder="Search class…" />
          <button
            v-for="c in filteredForSubclass"
            :key="c.id"
            class="dropdown-item"
            @click="addSubclass(c.id)"
          >{{ c.label }}</button>
          <p v-if="!filteredForSubclass.length" class="dropdown-empty">No classes available</p>
        </div>
        <div class="chip-list">
          <span v-for="id in form.subclass_of" :key="id" class="chip">
            {{ conceptLabel(id) }}
            <button class="chip-remove" @click="removeSubclass(id)">×</button>
          </span>
        </div>

        <!-- Equivalent To -->
        <div class="sub-label-row">
          <label class="field-label">Equivalent To</label>
          <button class="add-btn" @click="showEquivDropdown = !showEquivDropdown">+ Add</button>
        </div>
        <div v-if="showEquivDropdown" class="dropdown-list">
          <input class="dropdown-search" v-model="equivSearch" placeholder="Search class…" />
          <button
            v-for="c in filteredForEquiv"
            :key="c.id"
            class="dropdown-item"
            @click="addEquiv(c.id)"
          >{{ c.label }}</button>
          <p v-if="!filteredForEquiv.length" class="dropdown-empty">No classes available</p>
        </div>
        <div v-if="form.equivalent_to.length" class="chip-list">
          <span v-for="id in form.equivalent_to" :key="id" class="chip chip--equiv">
            {{ conceptLabel(id) }}
            <button class="chip-remove" @click="removeEquiv(id)">×</button>
          </span>
        </div>
        <p v-else class="empty-hint">No equivalence rules defined</p>

        <!-- Known Subclasses (read-only, edit mode only) -->
        <template v-if="store.panelMode === 'edit' && knownSubclasses.length">
          <div class="sub-label-row" style="margin-top:8px">
            <label class="field-label">Subclasses (Is Parent Of)</label>
          </div>
          <div class="chip-list">
            <span v-for="c in knownSubclasses" :key="c.id" class="chip chip--child">
              {{ c.label }}
            </span>
          </div>
        </template>
      </section>

      <!-- ── Section 3: Property Restrictions ───────────────────────────── -->
      <section class="panel-section">
        <div class="sub-label-row">
          <h5 class="section-title">Property Restrictions</h5>
          <button class="add-btn" @click="addRestriction">+ Add Restriction</button>
        </div>
        <div v-if="form.restrictions.length" class="restriction-list">
          <div v-for="(r, i) in form.restrictions" :key="i" class="restriction-row">
            <select class="restriction-select" v-model="r.property_id">
              <option value="">— property —</option>
              <option
                v-for="p in objectProperties"
                :key="p.id"
                :value="p.id"
              >{{ p.label }}</option>
            </select>
            <select class="restriction-select restriction-type" v-model="r.restriction_type">
              <option value="some">Some (∃)</option>
              <option value="all">All (∀)</option>
              <option value="cardinality">Cardinality</option>
            </select>
            <button class="chip-remove" @click="removeRestriction(i)">×</button>
          </div>
        </div>
        <p v-else class="empty-hint">No restrictions defined</p>
      </section>

      <!-- ── Section 4: Metadata & Annotations ──────────────────────────── -->
      <section class="panel-section">
        <div class="sub-label-row">
          <h5 class="section-title">Annotations</h5>
          <button class="add-btn" @click="addAnnotation">+ Add Annotation</button>
        </div>
        <div v-if="annotationPairs.length" class="annotation-list">
          <div v-for="(pair, i) in annotationPairs" :key="i" class="annotation-row">
            <input class="annotation-input" v-model="pair.key" placeholder="key" />
            <span class="prop-sep">:</span>
            <input class="annotation-input" v-model="pair.value" placeholder="value" />
            <button class="chip-remove" @click="removeAnnotation(i)">×</button>
          </div>
        </div>
        <p v-else class="empty-hint">No annotations defined</p>

        <label class="has-key-row">
          <input type="checkbox" v-model="form.hasKey" />
          <span class="field-label" style="margin:0">Has Key (owl:hasKey)</span>
        </label>
      </section>
    </div>

    <!-- Footer -->
    <div class="panel-footer">
      <button class="btn-secondary" @click="cancel">Cancel</button>
      <button
        class="btn-primary"
        :disabled="!form.label.trim() || isSaving"
        @click="submit"
      >
        <span v-if="isSaving" class="btn-spinner" />
        {{ store.panelMode === 'create' ? 'Create Class' : 'Save Changes' }}
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useOntologyStore } from '../../stores/ontology'
import type { OWLRestriction } from '../../types/ontology'

const store = useOntologyStore()
const { concepts, properties, selectedConcept, conceptMap } = storeToRefs(store)

const labelInputRef = ref<HTMLInputElement | null>(null)
const isSaving = ref(false)

// ── Local form state ─────────────────────────────────────────────────────────
interface AnnotationPair { key: string; value: string }

const form = reactive({
  label: '',
  uri: '',
  comment: '',
  subclass_of: [] as string[],
  equivalent_to: [] as string[],
  restrictions: [] as OWLRestriction[],
  hasKey: false,
})
const annotationPairs = ref<AnnotationPair[]>([])

// Dropdown visibility & search
const showSubclassDropdown = ref(false)
const showEquivDropdown = ref(false)
const subclassSearch = ref('')
const equivSearch = ref('')

// ── Computed helpers ─────────────────────────────────────────────────────────
const editingId = computed(() =>
  store.panelMode === 'edit' ? selectedConcept.value?.id ?? null : null
)

const otherConcepts = computed(() =>
  concepts.value.filter(c => c.id !== editingId.value)
)

// Classes that declare the current class as their parent (read-only, edit mode)
const knownSubclasses = computed(() => {
  if (!editingId.value) return []
  return concepts.value.filter(c => c.subclass_of?.includes(editingId.value!))
})

const filteredForSubclass = computed(() =>
  otherConcepts.value
    .filter(c => !form.subclass_of.includes(c.id))
    .filter(c => c.label.toLowerCase().includes(subclassSearch.value.toLowerCase()))
)

const filteredForEquiv = computed(() =>
  otherConcepts.value
    .filter(c => !form.equivalent_to.includes(c.id))
    .filter(c => c.label.toLowerCase().includes(equivSearch.value.toLowerCase()))
)

const objectProperties = computed(() =>
  properties.value.filter(p => p.property_type === 'ObjectProperty')
)

function conceptLabel(id: string) {
  return conceptMap.value[id]?.label ?? id
}

// ── Auto-generate URI from label ─────────────────────────────────────────────
function autoUri() {
  if (!form.uri || form.uri === lastAutoUri.value) {
    const slug = form.label.replace(/\s+/g, '_')
    form.uri = `http://km.local/ontology#${slug}`
    lastAutoUri.value = form.uri
  }
}
const lastAutoUri = ref('')

// ── Populate form when mode changes ─────────────────────────────────────────
function resetForm() {
  form.label = ''
  form.uri = ''
  form.comment = ''
  form.subclass_of = []
  form.equivalent_to = []
  form.restrictions = []
  form.hasKey = false
  annotationPairs.value = []
  showSubclassDropdown.value = false
  showEquivDropdown.value = false
  subclassSearch.value = ''
  equivSearch.value = ''
  lastAutoUri.value = ''
}

// Watch BOTH panelMode AND selectedConcept: switching between two classes keeps
// panelMode='edit' without changing it, so watching only panelMode misses the switch.
watch(
  [() => store.panelMode, selectedConcept],
  ([mode, concept]) => {
    if (mode === 'create') {
      resetForm()
      nextTick(() => labelInputRef.value?.focus())
    } else if (mode === 'edit' && concept) {
      const c = concept
      form.label = c.label
      form.uri = c.uri
      form.comment = c.comment ?? ''
      form.subclass_of = [...(c.subclass_of ?? [])]
      form.equivalent_to = [...(c.equivalent_to ?? [])]
      form.restrictions = (c.restrictions ?? []).map(r => ({ ...r }))
      form.hasKey = !!(c.annotations?.['owl:hasKey'])
      annotationPairs.value = Object.entries(c.annotations ?? {})
        .filter(([k]) => k !== 'owl:hasKey')
        .map(([key, value]) => ({ key, value }))
      lastAutoUri.value = ''
    }
  },
  { immediate: true }
)

onMounted(() => {
  if (store.panelMode === 'create') {
    nextTick(() => labelInputRef.value?.focus())
  }
})

// ── Subclass helpers ─────────────────────────────────────────────────────────
function addSubclass(id: string) {
  if (!form.subclass_of.includes(id)) form.subclass_of.push(id)
  showSubclassDropdown.value = false
  subclassSearch.value = ''
}
function removeSubclass(id: string) {
  form.subclass_of = form.subclass_of.filter(x => x !== id)
}

// ── Equiv helpers ────────────────────────────────────────────────────────────
function addEquiv(id: string) {
  if (!form.equivalent_to.includes(id)) form.equivalent_to.push(id)
  showEquivDropdown.value = false
  equivSearch.value = ''
}
function removeEquiv(id: string) {
  form.equivalent_to = form.equivalent_to.filter(x => x !== id)
}

// ── Restriction helpers ───────────────────────────────────────────────────────
function addRestriction() {
  form.restrictions.push({ property_id: '', restriction_type: 'some' })
}
function removeRestriction(i: number) {
  form.restrictions.splice(i, 1)
}

// ── Annotation helpers ────────────────────────────────────────────────────────
function addAnnotation() {
  annotationPairs.value.push({ key: '', value: '' })
}
function removeAnnotation(i: number) {
  annotationPairs.value.splice(i, 1)
}

function buildAnnotations(): Record<string, string> {
  const result: Record<string, string> = {}
  for (const { key, value } of annotationPairs.value) {
    if (key.trim()) result[key.trim()] = value
  }
  if (form.hasKey) result['owl:hasKey'] = 'true'
  return result
}

// ── Submit ─────────────────────────────────────────────────────────────────────
async function submit() {
  if (!form.label.trim()) return
  isSaving.value = true

  const payload = {
    uri: form.uri || `http://km.local/ontology#${form.label.replace(/\s+/g, '_')}`,
    label: form.label.trim(),
    comment: form.comment.trim() || undefined,
    subclass_of: form.subclass_of,
    equivalent_to: form.equivalent_to,
    restrictions: form.restrictions.filter(r => r.property_id),
    annotations: buildAnnotations(),
  }

  try {
    if (store.panelMode === 'create') {
      const concept = await store.createConcept(payload)
      if (concept && store.pendingClassPosition) {
        await store.addClassToCanvas(concept, store.pendingClassPosition)
      }
    } else {
      await store.updateSelectedConcept(payload)
    }
    store.closePanel()
  } finally {
    isSaving.value = false
  }
}

function cancel() {
  store.closePanel()
  if (store.panelMode !== 'edit') store.selectElement(null)
}
</script>

<style scoped>
.owl-panel {
  width: 300px;
  min-width: 300px;
  display: flex;
  flex-direction: column;
  background: var(--surface-container-lowest, #fff);
  border-left: 1px solid var(--outline-variant, #e5e5e7);
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px 10px;
  border-bottom: 1px solid var(--outline-variant, #e5e5e7);
  flex-shrink: 0;
}

.panel-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--on-surface, #1d1d1f);
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 16px;
  color: var(--on-surface-variant, #86868b);
  cursor: pointer;
  padding: 2px 4px;
  line-height: 1;
}
.close-btn:hover { color: var(--on-surface, #1d1d1f); }

.panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 4px 0 8px;
}

.panel-section {
  padding: 12px 16px;
  border-bottom: 1px solid var(--outline-variant, #e5e5e7);
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.section-title {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--on-surface-variant, #86868b);
  margin: 0 0 4px;
}

.field-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--on-surface-variant, #86868b);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-top: 4px;
}
.req { color: #c0392b; }

.field-input {
  padding: 5px 8px;
  border: 1px solid var(--outline-variant, #e5e5e7);
  border-radius: 6px;
  font-size: 12px;
  outline: none;
  resize: vertical;
  width: 100%;
  box-sizing: border-box;
  font-family: inherit;
}
.field-input:focus { border-color: var(--primary, #0058bc); }

/* Sub-label row */
.sub-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 6px;
}
.add-btn {
  font-size: 11px;
  font-weight: 600;
  color: var(--primary, #0058bc);
  background: none;
  border: none;
  cursor: pointer;
  padding: 2px 4px;
}
.add-btn:hover { opacity: 0.7; }

/* Dropdown */
.dropdown-list {
  border: 1px solid var(--outline-variant, #e5e5e7);
  border-radius: 8px;
  background: var(--surface-container-lowest, #fff);
  padding: 6px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  max-height: 160px;
  overflow-y: auto;
}
.dropdown-search {
  padding: 4px 8px;
  border: 1px solid var(--outline-variant, #e5e5e7);
  border-radius: 6px;
  font-size: 12px;
  outline: none;
  margin-bottom: 4px;
}
.dropdown-item {
  text-align: left;
  background: none;
  border: none;
  padding: 5px 8px;
  border-radius: 5px;
  font-size: 12px;
  cursor: pointer;
  color: var(--on-surface, #1d1d1f);
}
.dropdown-item:hover { background: var(--surface-container-low, #f1f3fe); }
.dropdown-empty { font-size: 11px; color: var(--on-surface-variant, #86868b); text-align: center; padding: 4px 0; margin: 0; }

/* Chips */
.chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 4px;
}
.chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px 2px 10px;
  border-radius: 999px;
  background: var(--primary-container, #d8e2ff);
  color: var(--on-primary-fixed, #001a41);
}
.chip--equiv {
  background: var(--tertiary-fixed, #ffdbcc);
  color: var(--on-tertiary-fixed, #351000);
}
.chip--child {
  background: var(--surface-container-high, #e6e8f3);
  color: var(--on-surface-variant, #414755);
  font-weight: 500;
}
.chip-remove {
  background: none;
  border: none;
  font-size: 13px;
  line-height: 1;
  cursor: pointer;
  color: inherit;
  opacity: 0.7;
  padding: 0 1px;
}
.chip-remove:hover { opacity: 1; }

/* Restrictions */
.restriction-list { display: flex; flex-direction: column; gap: 6px; }
.restriction-row {
  display: flex;
  align-items: center;
  gap: 4px;
}
.restriction-select {
  flex: 1;
  padding: 4px 6px;
  border: 1px solid var(--outline-variant, #e5e5e7);
  border-radius: 6px;
  font-size: 11px;
  outline: none;
  background: var(--surface-container-lowest, #fff);
}
.restriction-type { flex: 0 0 auto; width: 90px; }

/* Annotations */
.annotation-list { display: flex; flex-direction: column; gap: 5px; }
.annotation-row {
  display: flex;
  align-items: center;
  gap: 4px;
}
.annotation-input {
  flex: 1;
  padding: 4px 7px;
  border: 1px solid var(--outline-variant, #e5e5e7);
  border-radius: 6px;
  font-size: 11px;
  outline: none;
}
.prop-sep { color: var(--on-surface-variant, #86868b); font-weight: 700; flex-shrink: 0; }

.has-key-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
  cursor: pointer;
}

.empty-hint {
  font-size: 11px;
  color: var(--on-surface-variant, #86868b);
  font-style: italic;
  margin: 2px 0 0;
}

/* Footer */
.panel-footer {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid var(--outline-variant, #e5e5e7);
  flex-shrink: 0;
}
.btn-primary,
.btn-secondary {
  flex: 1;
  padding: 8px 0;
  border-radius: 8px;
  border: none;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
.btn-primary {
  background: var(--primary, #0058bc);
  color: #fff;
}
.btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-secondary {
  background: var(--surface-container-highest, #e0e0e6);
  color: var(--on-surface, #1d1d1f);
}
.btn-spinner {
  width: 12px;
  height: 12px;
  border: 2px solid rgba(255,255,255,0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
