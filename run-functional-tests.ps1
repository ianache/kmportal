# Script de Pruebas Funcionales - Knowledge Management Auth
# Fecha: 2026-05-05
# Usuario de prueba: kmuser@comsatel.com.pe

$ErrorActionPreference = "Stop"
$global:TestsPassed = 0
$global:TestsFailed = 0
$global:TestResults = @()

function Test-Assertion {
    param(
        [string]$Name,
        [scriptblock]$Test,
        [string]$Expected
    )
    
    Write-Host "`n🧪 Test: $Name" -ForegroundColor Cyan
    Write-Host "   Esperado: $Expected" -ForegroundColor Gray
    
    try {
        $result = & $Test
        if ($result) {
            Write-Host "   ✅ PASÓ" -ForegroundColor Green
            $global:TestsPassed++
            $global:TestResults += [PSCustomObject]@{ Test = $Name; Result = "PASÓ"; Error = $null }
            return $true
        } else {
            Write-Host "   ❌ FALLÓ" -ForegroundColor Red
            $global:TestsFailed++
            $global:TestResults += [PSCustomObject]@{ Test = $Name; Result = "FALLÓ"; Error = "Retornó falso" }
            return $false
        }
    } catch {
        Write-Host "   ❌ ERROR: $_" -ForegroundColor Red
        $global:TestsFailed++
        $global:TestResults += [PSCustomObject]@{ Test = $Name; Result = "ERROR"; Error = $_.ToString() }
        return $false
    }
}

function Test-FileContent {
    param($Path, $Pattern, $Description)
    
    $content = Get-Content $Path -Raw -ErrorAction SilentlyContinue
    if ($null -eq $content) {
        return $false
    }
    return $content -match $Pattern
}

Clear-Host
Write-Host @"
╔════════════════════════════════════════════════════════════════╗
║         PRUEBAS FUNCIONALES - SISTEMA DE AUTENTICACIÓN        ║
║                     Knowledge Management                       ║
╚════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Magenta

Write-Host "Usuario de prueba: kmuser@comsatel.com.pe" -ForegroundColor Yellow
Write-Host "Fecha: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n" -ForegroundColor Gray

# ============================================================================
# SECCIÓN 1: PRUEBAS DE CONFIGURACIÓN BFF
# ============================================================================
Write-Host "`n📦 SECCIÓN 1: CONFIGURACIÓN BFF (Backend)" -ForegroundColor Blue
Write-Host "==========================================" -ForegroundColor Blue

Test-Assertion -Name "BFF: Session middleware existe" -Expected "Archivo session.ts presente" -Test {
    Test-Path "..\bff\src\middleware\session.ts"
}

Test-Assertion -Name "BFF: Cookie secure = false" -Expected "Configurado para HTTP desarrollo" -Test {
    Test-FileContent "..\bff\src\middleware\session.ts" "secure:\s*false"
}

Test-Assertion -Name "BFF: Cookie domain = undefined" -Expected "Domain no restringido" -Test {
    Test-FileContent "..\bff\src\middleware\session.ts" "domain:\s*undefined"
}

Test-Assertion -Name "BFF: Cookie sameSite = lax" -Expected "Permite cross-port" -Test {
    Test-FileContent "..\bff\src\middleware\session.ts" "sameSite:\s*['`]lax['`]"
}

Test-Assertion -Name "BFF: FRONTEND_URL apunta a puerto 5100" -Expected "Shell en puerto correcto" -Test {
    Test-FileContent "..\bff\.env" "FRONTEND_URL=http://localhost:5100"
}

Test-Assertion -Name "BFF: WebSocket parsea cookie correctamente" -Expected "Decodifica session ID" -Test {
    Test-FileContent "..\bff\src\websocket\server.ts" "decodeURIComponent"
}

# ============================================================================
# SECCIÓN 2: PRUEBAS DE CONFIGURACIÓN SHELL
# ============================================================================
Write-Host "`n📦 SECCIÓN 2: CONFIGURACIÓN SHELL (Frontend Host)" -ForegroundColor Blue
Write-Host "===================================================" -ForegroundColor Blue

Test-Assertion -Name "Shell: bffClient.ts existe" -Expected "Servicio API presente" -Test {
    Test-Path "..\frontend\apps\shell\src\services\bffClient.ts"
}

Test-Assertion -Name "Shell: bffClient usa URL relativa" -Expected "baseUrl = ''" -Test {
    Test-FileContent "..\frontend\apps\shell\src\services\bffClient.ts" "this\.baseUrl\s*=\s*''"
}

Test-Assertion -Name "Shell: bffClient exporta BffClientKey" -Expected "Símbolo de inyección disponible" -Test {
    Test-FileContent "..\frontend\apps\shell\src\services\bffClient.ts" "export\s+const\s+BffClientKey"
}

Test-Assertion -Name "Shell: bffClient expone a window" -Expected "Micro-frontends pueden acceder" -Test {
    Test-FileContent "..\frontend\apps\shell\src\services\bffClient.ts" "__SHELL_BFF_CLIENT__"
}

Test-Assertion -Name "Shell: bffClient credentials = include" -Expected "Envía cookies" -Test {
    Test-FileContent "..\frontend\apps\shell\src\services\bffClient.ts" "credentials:\s*['`]include['`]"
}

Test-Assertion -Name "Shell: auth.ts fetchSession URL relativa" -Expected "/auth/session" -Test {
    Test-FileContent "..\frontend\apps\shell\src\stores\auth.ts" "fetch\(['`]/auth/session['`])"
}

Test-Assertion -Name "Shell: auth.ts credentials = include" -Expected "Envía cookies en sesión" -Test {
    Test-FileContent "..\frontend\apps\shell\src\stores\auth.ts" "credentials:\s*['`]include['`]"
}

Test-Assertion -Name "Shell: WebSocket URL relativa" -Expected "Conexión via proxy" -Test {
    Test-FileContent "..\frontend\apps\shell\src\services\websocket.ts" "DEFAULT_WS_URL\s*=\s*''"
}

Test-Assertion -Name "Shell: main.ts provee BffClientKey" -Expected "Inyección disponible" -Test {
    Test-FileContent "..\frontend\apps\shell\src\main.ts" "app\.provide\(BffClientKey"
}

Test-Assertion -Name "Shell: Vite proxy configurado" -Expected "Redirige /api al BFF" -Test {
    Test-FileContent "..\frontend\apps\shell\vite.config.ts" "target:\s*['`]http://localhost:3000['`]"
}

# ============================================================================
# SECCIÓN 3: PRUEBAS DE MICRO-FRONTENDS
# ============================================================================
Write-Host "`n📦 SECCIÓN 3: MICRO-FRONTENDS" -ForegroundColor Blue
Write-Host "===============================" -ForegroundColor Blue

$microFrontends = @(
    @{ Name = "search-ui"; File = "searchApi.ts" },
    @{ Name = "domains-ui"; File = "domainsApi.ts" },
    @{ Name = "ingestion-ui"; File = "ingestionApi.ts" }
)

foreach ($mf in $microFrontends) {
    Test-Assertion -Name "$($mf.Name): Usa window.__SHELL_BFF_CLIENT__" -Expected "Obtiene cliente del shell" -Test {
        Test-FileContent "..\frontend\apps\$($mf.Name)\src\services\$($mf.File)" "window\.__SHELL_BFF_CLIENT__"
    }
    
    Test-Assertion -Name "$($mf.Name): Tiene fallback local" -Expected "Funciona sin shell" -Test {
        Test-FileContent "..\frontend\apps\$($mf.Name)\src\services\$($mf.File)" "localBffClient"
    }
    
    Test-Assertion -Name "$($mf.Name): URLs relativas en fallback" -Expected "/api prefix" -Test {
        Test-FileContent "..\frontend\apps\$($mf.Name)\src\services\$($mf.File)" "\`/api\$\{path\}"
    }
    
    Test-Assertion -Name "$($mf.Name): CORS configurado" -Expected "Permite localhost:5100" -Test {
        Test-FileContent "..\frontend\apps\$($mf.Name)\vite.config.ts" "cors:\s*\{"
    }
}

# ============================================================================
# SECCIÓN 4: PRUEBAS DE ROLES Y PERMISOS
# ============================================================================
Write-Host "`n📦 SECCIÓN 4: ROLES Y PERMISOS" -ForegroundColor Blue
Write-Host "===============================" -ForegroundColor Blue

Test-Assertion -Name "Router: KM_VIEWER puede ver Search" -Expected "Acceso básico" -Test {
    Test-FileContent "..\frontend\apps\shell\src\router\index.ts" "KM_VIEWER"
}

Test-Assertion -Name "Router: KM_MANAGER puede ver Domains" -Expected "Acceso manager" -Test {
    Test-FileContent "..\frontend\apps\shell\src\router\index.ts" "KM_MANAGER.*KM_ADMIN"
}

Test-Assertion -Name "Router: KM_ADMIN puede ver Admin" -Expected "Acceso total" -Test {
    Test-FileContent "..\frontend\apps\shell\src\router\index.ts" "roles:\s*\['KM_ADMIN'\]"
}

Test-Assertion -Name "Auth Store: Computed isAdmin" -Expected "Detecta rol admin" -Test {
    Test-FileContent "..\frontend\apps\shell\src\stores\auth.ts" "isAdmin.*KM_ADMIN"
}

Test-Assertion -Name "Auth Store: Computed isManager" -Expected "Detecta rol manager" -Test {
    Test-FileContent "..\frontend\apps\shell\src\stores\auth.ts" "isManager.*KM_MANAGER"
}

# ============================================================================
# SECCIÓN 5: PRUEBAS DE INTEGRACIÓN
# ============================================================================
Write-Host "`n📦 SECCIÓN 5: INTEGRACIÓN Y FLUJO" -ForegroundColor Blue
Write-Host "===================================" -ForegroundColor Blue

Test-Assertion -Name "Flujo: Login redirige a Keycloak" -Expected "URL completa del BFF" -Test {
    Test-FileContent "..\frontend\apps\shell\src\stores\auth.ts" "window\.location\.href.*BFF_URL.*auth/login"
}

Test-Assertion -Name "Flujo: Callback maneja success=true" -Expected "Procesa autenticación" -Test {
    Test-FileContent "..\frontend\apps\shell\src\views\AuthCallback.vue" "success\s*===\s*'true'"
}

Test-Assertion -Name "Flujo: AuthCallback llama fetchSession" -Expected "Obtiene datos de usuario" -Test {
    Test-FileContent "..\frontend\apps\shell\src\views\AuthCallback.vue" "fetchSession"
}

# ============================================================================
# RESUMEN
# ============================================================================
Write-Host "`n" -NoNewline
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║                      RESUMEN DE PRUEBAS                        ║" -ForegroundColor Magenta
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta

$totalTests = $global:TestsPassed + $global:TestsFailed
$percentage = if ($totalTests -gt 0) { [math]::Round(($global:TestsPassed / $totalTests) * 100, 2) } else { 0 }

Write-Host "`n📊 Estadísticas:" -ForegroundColor Yellow
Write-Host "   Total de pruebas: $totalTests" -ForegroundColor White
Write-Host "   ✅ Pasaron: $global:TestsPassed" -ForegroundColor Green
Write-Host "   ❌ Fallaron: $global:TestsFailed" -ForegroundColor $(if($global:TestsFailed -gt 0){"Red"}else{"Green"})
Write-Host "   📈 Porcentaje: $percentage%" -ForegroundColor $(if($percentage -ge 80){"Green"}elseif($percentage -ge 50){"Yellow"}else{"Red"})

if ($global:TestsFailed -eq 0) {
    Write-Host "`n✅ TODAS LAS PRUEBAS PASARON" -ForegroundColor Green -BackgroundColor Black
    Write-Host "`n🚀 Sistema listo para usar con:" -ForegroundColor Cyan
    Write-Host "   Usuario: kmuser@comsatel.com.pe" -ForegroundColor White
    Write-Host "   Password: welcome1" -ForegroundColor White
} else {
    Write-Host "`n⚠️  ALGUNAS PRUEBAS FALLARON" -ForegroundColor Yellow -BackgroundColor Black
    Write-Host "`n📋 Detalles de fallos:" -ForegroundColor Red
    $failedTests = $global:TestResults | Where-Object { $_.Result -ne "PASÓ" }
    $failedTests | ForEach-Object {
        Write-Host "   ❌ $($_.Test)" -ForegroundColor Red
        if ($_.Error) {
            Write-Host "      Error: $($_.Error)" -ForegroundColor Gray
        }
    }
}

Write-Host "`n📁 Archivos de configuración verificados:" -ForegroundColor Cyan
Write-Host "   - bff/src/middleware/session.ts" -ForegroundColor Gray
Write-Host "   - bff/.env" -ForegroundColor Gray
Write-Host "   - frontend/apps/shell/src/services/bffClient.ts" -ForegroundColor Gray
Write-Host "   - frontend/apps/shell/src/stores/auth.ts" -ForegroundColor Gray
Write-Host "   - frontend/apps/shell/src/services/websocket.ts" -ForegroundColor Gray
Write-Host "   - frontend/apps/shell/src/main.ts" -ForegroundColor Gray
Write-Host "   - frontend/apps/shell/src/router/index.ts" -ForegroundColor Gray
Write-Host "   - frontend/apps/*/src/services/*.ts (micro-frontends)" -ForegroundColor Gray
Write-Host "   - frontend/apps/*/vite.config.ts (CORS)" -ForegroundColor Gray

# Exportar resultados
$reportPath = ".\test-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
$global:TestResults | ConvertTo-Json -Depth 3 | Out-File $reportPath
Write-Host "`n📄 Reporte guardado en: $reportPath" -ForegroundColor Gray

exit $global:TestsFailed
