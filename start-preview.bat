@echo off
echo ========================================
echo  INICIAR SISTEMA - MODO PREVIEW
echo ========================================
echo.
echo Este script inicia los micro-frontends en modo preview
echo (requiere build previo de cada micro-frontend)
echo.

cd /d "%~dp0"

echo Paso 1: Verificando builds...
echo.

if not exist "frontend\apps\search-ui\dist\remoteEntry.js" (
    echo [WARNING] search-ui no tiene build. Ejecutando build...
    cd frontend\apps\search-ui
    call npm run build
    cd ..\..\..
)

if not exist "frontend\apps\domains-ui\dist\remoteEntry.js" (
    echo [WARNING] domains-ui no tiene build. Ejecutando build...
    cd frontend\apps\domains-ui
    call npm run build
    cd ..\..\..
)

if not exist "frontend\apps\ingestion-ui\dist\remoteEntry.js" (
    echo [WARNING] ingestion-ui no tiene build. Ejecutando build...
    cd frontend\apps\ingestion-ui
    call npm run build
    cd ..\..\..
)

if not exist "frontend\apps\admin-ui\dist\remoteEntry.js" (
    echo [WARNING] admin-ui no tiene build. Ejecutando build...
    cd frontend\apps\admin-ui
    call npm run build
    cd ..\..\..
)

echo.
echo ========================================
echo  INICIANDO SERVICIOS
echo ========================================
echo.
echo Abre estas terminales:
echo.
echo TERMINAL 1 - BFF:
echo   cd bff ^&^& npm run dev
echo.
echo TERMINAL 2 - Search UI (Preview):
echo   cd frontend\apps\search-ui ^&^& npm run preview
echo.
echo TERMINAL 3 - Domains UI (Preview):
echo   cd frontend\apps\domains-ui ^&^& npm run preview
echo.
echo TERMINAL 4 - Ingestion UI (Preview):
echo   cd frontend\apps\ingestion-ui ^&^& npm run preview
echo.
echo TERMINAL 5 - Admin UI (Preview):
echo   cd frontend\apps\admin-ui ^&^& npm run preview
echo.
echo TERMINAL 6 - Shell (Dev):
echo   cd frontend\apps\shell ^&^& npm run dev
echo.
echo ========================================
echo  ACCESO: http://localhost:5100
echo ========================================

pause
