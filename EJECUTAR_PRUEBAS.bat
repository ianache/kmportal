@echo off
chcp 65001
cls

echo ╔════════════════════════════════════════════════════════════════╗
echo ║     PRUEBAS FUNCIONALES - KNOWLEDGE MANAGEMENT                 ║
echo ║     Usuario: kmuser@comsatel.com.pe                           ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

echo 📋 PASOS PARA EJECUTAR PRUEBAS:
echo.
echo 1. INSTALAR DEPENDENCIAS:
echo    cd frontend
echo    npm install
echo.
echo 2. INSTALAR PLAYWRIGHT:
echo    npx playwright install chromium
echo.
echo 3. INICIAR TODOS LOS SERVICIOS (6 terminales):
echo    Terminal 1: cd bff ^&^& npm run dev
echo    Terminal 2: cd frontend/apps/shell ^&^& npm run dev
echo    Terminal 3: cd frontend/apps/search-ui ^&^& npm run dev
echo    Terminal 4: cd frontend/apps/domains-ui ^&^& npm run dev
echo    Terminal 5: cd frontend/apps/ingestion-ui ^&^& npm run dev
echo    Terminal 6: cd frontend/apps/admin-ui ^&^& npm run dev
echo.
echo 4. EJECUTAR PRUEBAS (desde frontend):
echo    npx playwright test
echo.
echo    O con interfaz visual:
echo    npx playwright test --ui
echo.
echo    O en modo debug:
echo    npx playwright test --debug
echo.
echo ════════════════════════════════════════════════════════════════════
echo.
echo 📁 ARCHIVOS DE PRUEBA CREADOS:
echo    - frontend/playwright.config.ts
echo    - frontend/e2e/auth.spec.ts
echo.
echo 🧪 TESTS INCLUIDOS:
echo    TC-001: Login exitoso redirige al dashboard
echo    TC-002: Sesión persiste al navegar entre páginas
echo    TC-003: Acceso a Admin solo para KM_ADMIN
echo    TC-004: APIs retornan 401 sin sesión
echo    TC-005: Logout cierra sesión correctamente
echo    TC-006: Cookie de sesión presente después de login
echo.
pause
