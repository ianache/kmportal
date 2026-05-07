<template>
  <div class="toolbox" :style="{ top: `${pos.y}px`, left: `${pos.x}px` }" @mousedown.stop="startDrag">
    <button class="tool-btn" title="Zoom In" @click="$emit('zoom-in')">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        <line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/>
      </svg>
    </button>
    <button class="tool-btn" title="Zoom Out" @click="$emit('zoom-out')">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        <line x1="8" y1="11" x2="14" y2="11"/>
      </svg>
    </button>
    <div class="divider"/>
    <button
      class="tool-btn"
      :class="{ active: snapActive }"
      title="Snap to Grid"
      @click="$emit('toggle-snap')"
    >
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
        <rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/>
      </svg>
    </button>
    <button class="tool-btn" title="Fit to Window" @click="$emit('fit')">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/>
        <line x1="21" y1="3" x2="14" y2="10"/><line x1="3" y1="21" x2="10" y2="14"/>
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'

defineProps<{ snapActive: boolean }>()
defineEmits<{
  (e: 'zoom-in'): void
  (e: 'zoom-out'): void
  (e: 'toggle-snap'): void
  (e: 'fit'): void
}>()

const pos = reactive({ x: 16, y: 80 })
let dragging = false
let startMouse = { x: 0, y: 0 }
let startPos = { x: 0, y: 0 }

function startDrag(e: MouseEvent) {
  dragging = true
  startMouse = { x: e.clientX, y: e.clientY }
  startPos = { x: pos.x, y: pos.y }
  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', stopDrag)
}

function onMove(e: MouseEvent) {
  if (!dragging) return
  pos.x = startPos.x + (e.clientX - startMouse.x)
  pos.y = startPos.y + (e.clientY - startMouse.y)
}

function stopDrag() {
  dragging = false
  window.removeEventListener('mousemove', onMove)
  window.removeEventListener('mouseup', stopDrag)
}
</script>

<style scoped>
.toolbox {
  position: absolute;
  z-index: 20;
  background: var(--surface-container-lowest, #fff);
  border: 1px solid var(--outline-variant, #e5e5e7);
  border-radius: 10px;
  padding: 6px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  cursor: grab;
  user-select: none;
}

.toolbox:active {
  cursor: grabbing;
}

.tool-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--on-surface-variant, #414755);
  transition: background 0.15s, color 0.15s;
}

.tool-btn:hover {
  background: var(--surface-container, #ecedf9);
  color: var(--primary, #0058bc);
}

.tool-btn.active {
  background: var(--primary-soft, rgba(0, 88, 188, 0.12));
  color: var(--primary, #0058bc);
}

.divider {
  height: 1px;
  background: var(--outline-variant, #e5e5e7);
  margin: 2px 4px;
}
</style>
