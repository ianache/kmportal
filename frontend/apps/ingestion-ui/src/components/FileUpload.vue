<template>
  <BaseCard class="file-upload-card">
    <h3 class="upload-title">New Ingestion</h3>
    
    <div class="upload-form">
      <div class="form-group">
        <label>Target Domain</label>
        <select v-model="selectedDomainId" class="domain-select">
          <option value="" disabled>Select a domain</option>
          <option v-for="d in domains" :key="d.id" :value="d.id">
            {{ d.name }}
          </option>
        </select>
      </div>

      <div 
        class="drop-zone" 
        :class="{ 'is-dragging': isDragging }"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="handleDrop"
        @click="triggerFileInput"
      >
        <input 
          type="file" 
          ref="fileInput" 
          class="hidden" 
          multiple 
          @change="handleFileSelect"
          accept=".pdf,.txt,.docx,.md"
        >
        <div class="drop-content">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
          <span class="drop-text">Click or drag files to upload</span>
          <span class="drop-hint">PDF, TXT, DOCX, Markdown</span>
        </div>
      </div>

      <div v-if="selectedFiles.length > 0" class="file-list">
        <div v-for="(f, i) in selectedFiles" :key="i" class="file-item">
          <div class="file-info">
            <span class="file-name">{{ f.file.name }}</span>
            <span class="file-size">{{ formatSize(f.file.size) }}</span>
          </div>
          <div v-if="f.status === 'uploading'" class="file-progress">
            <div class="progress-bar" :style="{ width: `${f.progress}%` }"></div>
          </div>
          <button v-if="f.status === 'idle'" class="remove-btn" @click.stop="removeFile(i)">✕</button>
          <span v-if="f.status === 'success'" class="success-icon">✓</span>
          <span v-if="f.status === 'error'" class="error-icon" :title="f.error">!</span>
        </div>
      </div>

      <div class="form-actions">
        <BaseButton 
          primary 
          :disabled="!canUpload" 
          :loading="isUploading"
          @click="startUpload"
        >
          {{ isUploading ? 'Uploading...' : 'Start Ingestion' }}
        </BaseButton>
      </div>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ingestionApi } from '../services/ingestionApi'
import BaseCard from 'shell/BaseCard'
import BaseButton from 'shell/BaseButton'

interface PendingFile {
  file: File
  progress: number
  status: 'idle' | 'uploading' | 'success' | 'error'
  error?: string
}

const domains = ref<any[]>([])
const selectedDomainId = ref('')
const selectedFiles = ref<PendingFile[]>([])
const isDragging = ref(false)
const isUploading = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

const canUpload = computed(() => {
  return selectedDomainId.value && selectedFiles.value.some(f => f.status === 'idle')
})

onMounted(async () => {
  try {
    domains.value = await ingestionApi.getDomains()
  } catch (err) {
    console.error('Failed to load domains:', err)
  }
})

function handleFileSelect(event: Event) {
  const files = (event.target as HTMLInputElement).files
  if (files) addFiles(Array.from(files))
}

function triggerFileInput() {
  fileInput.value?.click()
}

function handleDrop(event: DragEvent) {
  isDragging.value = false
  const files = event.dataTransfer?.files
  if (files) addFiles(Array.from(files))
}

function addFiles(files: File[]) {
  files.forEach(file => {
    selectedFiles.value.push({
      file,
      progress: 0,
      status: 'idle'
    })
  })
}

function removeFile(index: number) {
  selectedFiles.value.splice(index, 1)
}

function formatSize(bytes: number) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

async function startUpload() {
  if (!selectedDomainId.value) return
  
  isUploading.value = true
  
  const pending = selectedFiles.value.filter(f => f.status === 'idle')
  
  for (const f of pending) {
    f.status = 'uploading'
    f.progress = 0
    
    try {
      await ingestionApi.uploadDocument(selectedDomainId.value, f.file)
      f.status = 'success'
      f.progress = 100
    } catch (err) {
      f.status = 'error'
      f.error = err instanceof Error ? err.message : 'Upload failed'
    }
  }
  
  isUploading.value = false
  
  // Clear successful uploads after 2 seconds
  setTimeout(() => {
    selectedFiles.value = selectedFiles.value.filter(f => f.status !== 'success')
  }, 2000)
}
</script>

<style scoped>
.file-upload-card {
  padding: 24px;
  position: sticky;
  top: 120px;
}

.upload-title {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 24px;
}

.upload-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 13px;
  font-weight: 600;
  color: var(--on-surface-variant, #86868B);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.domain-select {
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid var(--outline-variant, #E5E5E7);
  background: var(--surface-container-lowest, #ffffff);
  font-size: 15px;
  outline: none;
}

.drop-zone {
  border: 2px dashed var(--outline-variant, #E5E5E7);
  border-radius: 12px;
  padding: 32px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--surface-container-low, #f1f3fe);
}

.drop-zone:hover, .drop-zone.is-dragging {
  border-color: var(--primary, #007AFF);
  background: var(--primary-soft, rgba(0, 122, 255, 0.05));
}

.drop-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--on-surface-variant, #86868B);
}

.drop-text {
  font-weight: 600;
  color: var(--on-surface, #1D1D1F);
}

.drop-hint {
  font-size: 12px;
}

.hidden {
  display: none;
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 200px;
  overflow-y: auto;
}

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  background: var(--surface-container-lowest, #ffffff);
  border: 1px solid var(--outline-variant, #E5E5E7);
  border-radius: 8px;
  position: relative;
  overflow: hidden;
}

.file-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  z-index: 1;
}

.file-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--on-surface, #1D1D1F);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 180px;
}

.file-size {
  font-size: 11px;
  color: var(--on-surface-variant, #86868B);
}

.file-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 2px;
  width: 100%;
  background: rgba(0, 122, 255, 0.1);
}

.progress-bar {
  height: 100%;
  background: var(--primary, #007AFF);
  transition: width 0.3s;
}

.remove-btn {
  background: none;
  border: none;
  color: var(--on-surface-variant, #86868B);
  cursor: pointer;
  padding: 4px;
  z-index: 1;
}

.success-icon { color: #34C759; font-weight: 700; }
.error-icon { color: #FF3B30; font-weight: 700; border: 1px solid currentColor; border-radius: 50%; width: 16px; height: 16px; display: flex; align-items: center; justify-content: center; font-size: 10px; }

.form-actions {
  padding-top: 12px;
}

.form-actions :deep(button) {
  width: 100%;
}
</style>
