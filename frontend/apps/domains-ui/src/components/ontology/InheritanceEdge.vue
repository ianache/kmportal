<script setup lang="ts">
import { computed } from 'vue'
import { getBezierPath, Position } from '@vue-flow/core'

const props = defineProps<{
  id: string
  sourceX: number
  sourceY: number
  targetX: number
  targetY: number
  sourcePosition?: Position
  targetPosition?: Position
}>()

const markerId = computed(() => `inh-${props.id.replace(/[^a-zA-Z0-9]/g, '-')}`)

const edgePath = computed(() => {
  const [path] = getBezierPath({
    sourceX: props.sourceX,
    sourceY: props.sourceY,
    sourcePosition: props.sourcePosition ?? Position.Bottom,
    targetX: props.targetX,
    targetY: props.targetY,
    targetPosition: props.targetPosition ?? Position.Top,
  })
  return path
})
</script>

<template>
  <defs>
    <!-- UML inheritance: solid line, hollow (white-filled) triangular arrowhead -->
    <marker
      :id="markerId"
      markerWidth="12"
      markerHeight="10"
      refX="11"
      refY="5"
      orient="auto"
      markerUnits="userSpaceOnUse"
    >
      <path d="M0,0 L0,10 L12,5 Z" fill="white" stroke="#1D1D1F" stroke-width="1.5" />
    </marker>
  </defs>
  <path
    :d="edgePath"
    stroke="#1D1D1F"
    stroke-width="2"
    fill="none"
    :marker-end="`url(#${markerId})`"
  />
</template>
