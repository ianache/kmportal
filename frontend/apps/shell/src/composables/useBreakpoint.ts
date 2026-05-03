import { ref, computed, onMounted, onUnmounted } from 'vue'

export type Breakpoint = 'mobile' | 'tablet' | 'desktop' | 'large'

const breakpoints = {
  mobile: 0,
  tablet: 768,
  desktop: 1024,
  large: 1440,
}

export function useBreakpoint() {
  const width = ref(window.innerWidth)
  const height = ref(window.innerHeight)

  const breakpoint = computed<Breakpoint>(() => {
    if (width.value >= breakpoints.large) return 'large'
    if (width.value >= breakpoints.desktop) return 'desktop'
    if (width.value >= breakpoints.tablet) return 'tablet'
    return 'mobile'
  })

  const isMobile = computed(() => breakpoint.value === 'mobile')
  const isTablet = computed(() => breakpoint.value === 'tablet')
  const isDesktop = computed(() => breakpoint.value === 'desktop' || breakpoint.value === 'large')
  const isLarge = computed(() => breakpoint.value === 'large')

  function update() {
    width.value = window.innerWidth
    height.value = window.innerHeight
  }

  onMounted(() => {
    window.addEventListener('resize', update)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', update)
  })

  return {
    width,
    height,
    breakpoint,
    isMobile,
    isTablet,
    isDesktop,
    isLarge,
  }
}

export default useBreakpoint
