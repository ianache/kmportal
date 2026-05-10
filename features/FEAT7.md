# REQSPEC: KMPortal Frontend - Visualizador de Linaje Semántico (Semantic Search MicroUI)

## 1. Contexto del Sistema y Objetivo
Se requiere actualizar la MicroUI de búsqueda en el frontend (`kmportal`) para consumir el nuevo endpoint híbrido de FastAPI (`/search/hybrid`) y visualizar la procedencia ontológica (provenance) de cada resultado mediante un grafo interactivo.

**Stack Tecnológico:**
* Framework: Vue 3 (Composition API, `<script setup>`)
* Manejo de Estado: Pinia
* Estilos: Tailwind CSS
* Visualización de Grafo: `cytoscape` (versión 3.x)
* Iconografía: `lucide-vue-next` (Requeridos: `Network`, `ShieldCheck`, `FileText`)

---

## 2. Definición de Tipos (TypeScript)
Crear/Actualizar las interfaces en `src/types/semantic.ts`:

```typescript
export interface GraphNode {
  id: string;
  label: string; // Clase OWL (ej: Control_Seguridad)
  name: string;
}

export interface GraphEdge {
  source: string;
  target: string;
  relation_type: string;
}

export interface SemanticProvenance {
  owl_class: string;
  iso_compliance: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface HybridSearchResult {
  link_id: string; // UUID
  content: string;
  score: number;
  source_file: string;
  provenance: SemanticProvenance;
}

## 3. Componente 1: SearchCard.vue (Actualización)
​
Modificar el componente existente para que acepte el tipo HybridSearchResult como prop.
​Requerimientos Estrictos de UI:
​Badges Superiores: Mostrar provenance.owl_class (fondo azul claro) y provenance.iso_compliance (color dinámico: Verde si es "PÚBLICO", Naranja si es "CONFIDENCIAL").
​Score: Mostrar el score en formato porcentaje (ej: (score * 100).toFixed(1)%).
​Botón de Acción: En la esquina inferior derecha, añadir un botón con el texto "Lineage" y el icono Network.
​Evento: Al hacer clic en el botón "Lineage", emitir el evento @show-lineage enviando el objeto HybridSearchResult completo.
​
## 4. Componente 2: LineageGraphModal.vue (Nuevo)

​Crear un componente modal que actúe como contenedor para el grafo de Cytoscape.
​
Props:
- ​isOpen (Boolean)
- ​resultData (Type: HybridSearchResult | null)
​
Lógica de Cytoscape Estricta (onMounted / watchEffect):

1. ​Contenedor: Utilizar una referencia de plantilla (ref="cyContainer") con dimensiones fijas (ej. h-96 w-full).
​2. Mapeo de Datos: Transformar resultData.provenance a elementos de Cytoscape:
​   - Nodo Raíz: { data: { id: 'root', label: 'Resultado de Búsqueda', classType: 'Root' } }
​   - Nodos Hijos: Iterar sobre provenance.nodes -> { data: { id: n.id, label: n.name, classType: n.label } }
   ​- Aristas: Iterar sobre provenance.edges -> { data: { source: e.source, target: e.target, label: e.relation_type } }. (Nota: Para las conexiones directas al resultado, usar 'root' como source).
​
3. Hoja de Estilos (Stylesheet):
​   - Nodos por defecto: Círculos, fondo gris, texto oscuro.
   - ​Nodo Raíz (node[classType="Root"]): Forma hexágono, fondo amarillo (#F59E0B).
   - ​Nodos de Control/Norma (node[classType*="Control"], node[classType*="ISO"]): Forma cuadrado redondeado, fondo azul (#3B82F6).
   - ​Aristas: Línea gris clara, flechas direccionales (target-arrow-shape: triangle), texto de la etiqueta pequeño y con fondo.
4. ​Layout: Utilizar el layout breadthfirst dirigido (directed: true).

​## 5. Criterios de Aceptación y Manejo de Errores
- ​Limpieza de Memoria: Destruir la instancia de cytoscape (cy.destroy()) en el hook onUnmounted del modal para evitar fugas de memoria.
- ​Manejo de Estado Nulo: Si resultData.provenance.nodes está vacío, mostrar un mensaje amistoso dentro del modal: "No se encontraron relaciones estructurales en la Ontología para este resultado." en lugar de renderizar un lienzo vacío.
​- Estilos Nativos: Asegurar que el modal tenga un z-index superior y un overlay oscuro semitransparente usando clases de Tailwind.
