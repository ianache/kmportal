# Script para iniciar todos los servicios correctamente
# Este script hace build de los micro-frontends antes de iniciarlos

echo "=========================================="
echo "  INICIANDO KNOWLEDGE MANAGEMENT"
echo "=========================================="
echo ""

# Paso 1: Build de micro-frontends
echo "📦 Paso 1: Haciendo build de micro-frontends..."
cd frontend

# Build search-ui
echo "   Building search-ui..."
cd apps/search-ui
npm run build
cd ../..

# Build domains-ui
echo "   Building domains-ui..."
cd apps/domains-ui
npm run build
cd ../..

# Build ingestion-ui
echo "   Building ingestion-ui..."
cd apps/ingestion-ui
npm run build
cd ../..

# Build admin-ui
echo "   Building admin-ui..."
cd apps/admin-ui
npm run build
cd ../..

echo "✅ Build completado"
echo ""

# Paso 2: Iniciar servicios en preview mode
echo "🚀 Paso 2: Iniciando servicios..."
echo ""
echo "Ejecuta estos comandos en TERMINALES SEPARADAS:"
echo ""
echo "TERMINAL 1 (BFF):"
echo "  cd bff && npm run dev"
echo ""
echo "TERMINAL 2 (Search UI - preview):"
echo "  cd frontend/apps/search-ui && npm run preview"
echo ""
echo "TERMINAL 3 (Domains UI - preview):"
echo "  cd frontend/apps/domains-ui && npm run preview"
echo ""
echo "TERMINAL 4 (Ingestion UI - preview):"
echo "  cd frontend/apps/ingestion-ui && npm run preview"
echo ""
echo "TERMINAL 5 (Admin UI - preview):"
echo "  cd frontend/apps/admin-ui && npm run preview"
echo ""
echo "TERMINAL 6 (Shell):"
echo "  cd frontend/apps/shell && npm run dev"
echo ""
echo "=========================================="
echo "Después de iniciar todos los servicios:"
echo "  http://localhost:5100"
echo "=========================================="
