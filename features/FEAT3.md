# Feature:Ontología KMPortal

## 1. Visión General
KMPortal requiere una capacidad avanzada de gestión de conocimiento basada en semántica formal. Cada **Dominio** dentro de la plataforma debe poseer una **Ontología (modelo conceptual)** única, la cual puede ser visualizada y editada a través de múltiples **Diagramas (vistas)**.

## 2. Arquitectura de Datos y Separación de Conceptos
Se debe implementar una separación estricta entre la lógica semántica y la representación gráfica:

*   **Modelo Semántico (La Ontología):** Contiene la "verdad" del conocimiento (Clases OWL, Object Properties, Data Properties). Persistido en Python/FastAPI usando **RDFLib**.
*   **Modelo de Diagrama (La Vista):** Contiene coordenadas (x, y), zoom, colores y estilos. Cada dominio puede tener $N$ diagramas. Persistido como objetos JSON vinculados al dominio.

## 3. Requerimientos Funcionales

### 3.1. Editor Visual (XYFlow / Vue Flow)
*   **Canvas Principal:** Uso de `Vue Flow` (XYFlow) para el renderizado de nodos y aristas.
*   **Gestión de Diagramas (Tabs):**
    *   Interfaz basada en pestañas (Tabs) superiores.
    *   Botón "+" para crear nuevos diagramas con un nombre corto.
    *   **Eliminación Segura:** Icono "x" en cada tab. Al activarse, mostrar un modal donde el usuario debe escribir obligatoriamente la palabra **"delete"** para confirmar la destrucción del diagrama.
*   **Toolbox Flotante (Draggable):**
    *   Botones de control: **Zoom In**, **Zoom Out**, **Snap to Grid** (ajuste a rejilla) y **Fit to Window** (encuadre automático).
*   **Paleta de Elementos (Sidebar Izquierdo):**
    *   Herramientas para arrastrar y soltar (Drag & Drop): *Nueva Clase (Nodo)* y *Nueva Relación (Arista)*.
*   **Panel de Propiedades (Sidebar Derecho):**
    *   Panel expandible/retraíble para editar los metadatos del elemento seleccionado (URI, Label, Range, Domain, etc.).

### 3.2. Capacidades OWL/RDF
*   **Importación:** Carga de archivos `.owl` o `.rdf`. El backend debe procesar el archivo y generar los conceptos en la base de datos.
*   **Exportación:** Descarga de la ontología del dominio en formatos OWL o RDF.
*   **Consistencia:** Las exportaciones deben ignorar los datos visuales (coordenadas) para mantener el estándar semántico puro.

### 3.3. Integración con el Card de Dominio
*   Cada Card de Dominio en el Dashboard principal debe incluir un icono de **"Ontology"** en la esquina inferior derecha.
*   Al hacer clic, debe redirigir al editor visual cargando el contexto específico de ese dominio.

## 4. Especificación Técnica (Stack)

*   **Frontend:** Vue 3, Pinia (Estado), XYFlow (Motor de Grafos), Tailwind CSS.
*   **BFF (NodeJS):** Orquestador que realiza el *merge* entre la data semántica (Python) y la data visual (JSON).
*   **Backend (Python):** Gestión de la ontología mediante **RDFLib** u **Owlready2**.
*   **Persistencia:**
    *   Ontología: Neo4j (GraphRAG Ready).
    *   Diagramas: PostgreSQL (Campo JSONB) o Documental.

## 5. Diseño de API

### 5.1. API de Ontología (Semántica)
*   `GET /dominios/{id}/ontologia`: Retorna conceptos puros.
*   `POST /dominios/{id}/ontologia/importar`: Procesa archivo OWL.
*   `GET /dominios/{id}/ontologia/exportar`: Genera archivo OWL/RDF.

### 5.2. API de Diseñador (Visual)
*   `GET /dominios/{id}/diagramas`: Lista de tabs.
*   `GET /diagramas/{diagram_id}`: Carga `nodes` y `edges` con posiciones.
*   `POST /diagramas`: Crea una nueva vista visual.
*   `DELETE /diagramas/{id}`: Elimina solo la representación visual.

## 6. Reglas de Validación
*   Un dominio no puede existir sin al menos un diagrama (se crea uno por defecto al inicio).
*   La eliminación de un concepto en la ontología debe limpiar en cascada las referencias en todos los diagramas asociados.
*   El botón de confirmación de eliminación de diagrama debe estar `disabled` hasta que el input sea exactamente igual a `"delete"`.

---
**Instrucción para la IA:** *Implementa los componentes de Vue 3 siguiendo esta estructura, asegurando que el Store de Pinia mantenga los conceptos y las posiciones en estados separados para garantizar la interoperabilidad del modelo OWL.*