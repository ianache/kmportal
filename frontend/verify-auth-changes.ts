# Script de Verificación de Cambios de Autenticación

function verifyFile(filePath, checks) {
  console.log(`\n📄 Verificando: ${filePath}`)
  const content = Deno.readTextFileSync(filePath)
  
  let passed = 0
  let failed = 0
  
  for (const check of checks) {
    const found = check.test(content)
    if (found) {
      console.log(`  ✅ ${check.name}`)
      passed++
    } else {
      console.log(`  ❌ ${check.name}`)
      failed++
    }
  }
  
  return { passed, failed }
}

console.log('🔍 Verificando cambios de autenticación...\n')

let totalPassed = 0
let totalFailed = 0

// 1. Verificar bffClient.ts
const bffClientChecks = verifyFile('apps/shell/src/services/bffClient.ts', [
  { name: 'Exporta BffClientKey', test: (c) => c.includes('export const BffClientKey') },
  { name: 'Usa baseUrl relativo ("")', test: (c) => c.includes("this.baseUrl = ''") },
  { name: 'Credentials include', test: (c) => c.includes("credentials: 'include'") },
  { name: 'Exponer a window', test: (c) => c.includes('__SHELL_BFF_CLIENT__') },
])
totalPassed += bffClientChecks.passed
totalFailed += bffClientChecks.failed

// 2. Verificar auth.ts
const authChecks = verifyFile('apps/shell/src/stores/auth.ts', [
  { name: 'fetchSession usa URL relativa', test: (c) => c.includes("fetch('/auth/session'") },
  { name: 'Credentials include en fetchSession', test: (c) => c.includes("credentials: 'include'") },
  { name: 'Login usa BFF_URL completo', test: (c) => c.includes('window.location.href = `${BFF_URL}/auth/login`') },
])
totalPassed += authChecks.passed
totalFailed += authChecks.failed

// 3. Verificar session.ts (BFF)
const sessionChecks = verifyFile('../../bff/src/middleware/session.ts', [
  { name: 'Cookie secure: false', test: (c) => c.includes('secure: false') },
  { name: 'Cookie domain: undefined', test: (c) => c.includes('domain: undefined') },
  { name: 'Cookie sameSite: lax', test: (c) => c.includes("sameSite: 'lax'") },
])
totalPassed += sessionChecks.passed
totalFailed += sessionChecks.failed

// 4. Verificar searchApi.ts
const searchApiChecks = verifyFile('apps/search-ui/src/services/searchApi.ts', [
  { name: 'Obtiene bffClient de window', test: (c) => c.includes('window.__SHELL_BFF_CLIENT__') },
  { name: 'Usa URL relativa en fallback', test: (c) => c.includes("const url = `/api${path}`") },
  { name: 'Credentials include', test: (c) => c.includes("credentials: 'include'") },
])
totalPassed += searchApiChecks.passed
totalFailed += searchApiChecks.failed

// 5. Verificar vite.config.ts (CORS)
const viteChecks = verifyFile('apps/search-ui/vite.config.ts', [
  { name: 'CORS configurado', test: (c) => c.includes('cors:') },
  { name: 'Origin permitido 5100', test: (c) => c.includes('localhost:5100') },
  { name: 'Credentials true', test: (c) => c.includes('credentials: true') },
])
totalPassed += viteChecks.passed
totalFailed += viteChecks.failed

console.log(`\n${'='.repeat(50)}`)
console.log(`📊 Resultados:`)
console.log(`   ✅ Pasaron: ${totalPassed}`)
console.log(`   ❌ Fallaron: ${totalFailed}`)
console.log(`${'='.repeat(50)}`)

if (totalFailed > 0) {
  console.log('\n⚠️  Algunas verificaciones fallaron')
  Deno.exit(1)
} else {
  console.log('\n✅ Todas las verificaciones pasaron')
  Deno.exit(0)
}
