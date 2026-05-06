# Script de Prueba de Autenticación
# Este script verifica que toda la configuración esté correcta

$ErrorActionPreference = "Stop"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  PRUEBAS DE AUTENTICACIÓN" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$testsPassed = 0
$testsFailed = 0

function Test-FileContains {
    param($Path, $Pattern, $Description)
    
    Write-Host "Test: $Description" -NoNewline
    $content = Get-Content $Path -Raw
    if ($content -match $Pattern) {
        Write-Host " ✅" -ForegroundColor Green
        $script:testsPassed++
        return $true
    } else {
        Write-Host " ❌" -ForegroundColor Red
        $script:testsFailed++
        return $false
    }
}

# 1. Verificar BFF - Configuración de Cookies
Write-Host "`n📋 BFF - Session Middleware:" -ForegroundColor Yellow
Test-FileContains "..\bff\src\middleware\session.ts" "secure:\s*false" "Cookie secure: false"
Test-FileContains "..\bff\src\middleware\session.ts" "domain:\s*undefined" "Cookie domain: undefined"
Test-FileContains "..\bff\src\middleware\session.ts" "sameSite:\s*['`]lax['`]" "Cookie sameSite: lax"

# 2. Verificar Shell - bffClient.ts
Write-Host "`n📋 Shell - bffClient.ts:" -ForegroundColor Yellow
Test-FileContains "..\frontend\apps\shell\src\services\bffClient.ts" "export\s+const\s+BffClientKey" "Exporta BffClientKey"
Test-FileContains "..\frontend\apps\shell\src\services\bffClient.ts" "this\.baseUrl\s*=\s*''" "Usa URL relativa"
Test-FileContains "..\frontend\apps\shell\src\services\bffClient.ts" "credentials:\s*['`]include['`]" "Credentials include"
Test-FileContains "..\frontend\apps\shell\src\services\bffClient.ts" "__SHELL_BFF_CLIENT__" "Expone a window"

# 3. Verificar Shell - auth.ts
Write-Host "`n📋 Shell - auth.ts:" -ForegroundColor Yellow
Test-FileContains "..\frontend\apps\shell\src\stores\auth.ts" "fetch\(['`]/auth/session['`])" "fetchSession URL relativa"
Test-FileContains "..\frontend\apps\shell\src\stores\auth.ts" "credentials:\s*['`]include['`]" "fetchSession credentials"

# 4. Verificar Micro-frontends
Write-Host "`n📋 Micro-frontends - Uso de bffClient:" -ForegroundColor Yellow
Test-FileContains "..\frontend\apps\search-ui\src\services\searchApi.ts" "window\.__SHELL_BFF_CLIENT__" "Search UI usa window.__SHELL_BFF_CLIENT__"
Test-FileContains "..\frontend\apps\domains-ui\src\services\domainsApi.ts" "window\.__SHELL_BFF_CLIENT__" "Domains UI usa window.__SHELL_BFF_CLIENT__"
Test-FileContains "..\frontend\apps\ingestion-ui\src\services\ingestionApi.ts" "window\.__SHELL_BFF_CLIENT__" "Ingestion UI usa window.__SHELL_BFF_CLIENT__"

# 5. Verificar CORS en vite.config.ts
Write-Host "`n📋 CORS Configuration:" -ForegroundColor Yellow
Test-FileContains "..\frontend\apps\search-ui\vite.config.ts" "cors:\s*{" "Search UI tiene CORS"
Test-FileContains "..\frontend\apps\domains-ui\vite.config.ts" "cors:\s*{" "Domains UI tiene CORS"
Test-FileContains "..\frontend\apps\ingestion-ui\vite.config.ts" "cors:\s*{" "Ingestion UI tiene CORS"
Test-FileContains "..\frontend\apps\admin-ui\vite.config.ts" "cors:\s*{" "Admin UI tiene CORS"

# Resumen
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  RESULTADOS:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Tests Pasados: $testsPassed" -ForegroundColor Green
Write-Host "Tests Fallidos: $testsFailed" -ForegroundColor $(if($testsFailed -gt 0){"Red"}else{"Green"})

if ($testsFailed -eq 0) {
    Write-Host "`n✅ TODAS LAS PRUEBAS PASARON" -ForegroundColor Green
    Write-Host "`nPara probar manualmente:" -ForegroundColor Yellow
    Write-Host "  1. Abre 6 terminales y ejecuta en cada una:" -ForegroundColor White
    Write-Host "     Terminal 1 (BFF):       cd bff && npm run dev" -ForegroundColor Gray
    Write-Host "     Terminal 2 (Shell):     cd frontend/apps/shell && npm run dev" -ForegroundColor Gray
    Write-Host "     Terminal 3 (Search):    cd frontend/apps/search-ui && npm run dev" -ForegroundColor Gray
    Write-Host "     Terminal 4 (Domains):   cd frontend/apps/domains-ui && npm run dev" -ForegroundColor Gray
    Write-Host "     Terminal 5 (Ingestion): cd frontend/apps/ingestion-ui && npm run dev" -ForegroundColor Gray
    Write-Host "     Terminal 6 (Admin):     cd frontend/apps/admin-ui && npm run dev" -ForegroundColor Gray
    Write-Host "`n  2. Limpia cookies de localhost en tu navegador" -ForegroundColor White
    Write-Host "  3. Ve a http://localhost:5100" -ForegroundColor White
    Write-Host "  4. Inicia sesión con Keycloak" -ForegroundColor White
    Write-Host "  5. Verifica que puedes navegar entre todas las páginas" -ForegroundColor White
    exit 0
} else {
    Write-Host "`n❌ HAY TESTS FALLIDOS - Revisa los archivos marcados con ❌" -ForegroundColor Red
    exit 1
}
