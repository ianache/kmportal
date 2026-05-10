# REQSPEC: KMPortal Frontend - Ingesta Dual (Quick vs. Semantic)

## 1. Objetivo y Contexto
Implementar una interfaz de carga versátil en `kmportal` que soporte dos flujos de trabajo:
1. **Quick RAG**: Ingesta rápida únicamente en la base de datos vectorial (ChromaDB) para documentos informativos.
2. **Semantic Atomic**: Ingesta estructurada vinculando el documento a la Ontología OWL y al grafo de Neo4j para conocimiento normativo (ISO 27001/BASC).

---

## 2. Componente de UI: `IngestionForm.vue`

### A. Control de Modo (The Semantic Switch)
*   **Elemento**: Toggle o Switch de Tailwind UI.
*   **Estado**: `isSemanticMode` (Boolean, default: false).
*   **Etiqueta**: "Activar Clasificación Ontológica (Alta Fidelidad)".

### B. Campos Dinámicos (Validación Condicional)
1. **Sección Común (Siempre Visible)**:
    *   `FileUploader`: Dropzone para archivos PDF/TXT.
    *   `ExtractionPreview`: Área de texto para visualizar/editar el contenido extraído.
2. **Sección Semántica (Visible solo si `isSemanticMode` es TRUE)**:
    *   `OWLClassSelector`: Dropdown que debe incluir clases como 'Control', 'Procedimiento', 'Arquitectura'.
    *   `GovernanceSelector`: Opciones de radio: 'PÚBLICO', 'INTERNO', 'CONFIDENCIAL'.
    *   `PropertyManager`: Lista dinámica para añadir pares clave-valor (ej: `version: 1.0`, `autor: IAP`).

---

## 3. Lógica de Envío (Integration Logic)

Dependiendo del estado de `isSemanticMode`, el componente debe invocar el endpoint correspondiente:

### Escenario 1: Quick RAG (`isSemanticMode == false`)
*   **Endpoint**: `POST /ingest/vector`
*   **Payload**: 
    ```json
    {
      "content": "string",
      "metadata": { "source": "filename.pdf", "type": "quick_rag" }
    }
```

### Escenario 2: Semantic Atomic (`isSemanticMode == true`)
*   **Endpoint**: `POST /ingest/semantic`
*   **Payload**: (basdo en el modelo IngestionPayload)
    ```json
    {
      "content": "string",
      "metadata": {
        "owl_class": "Control",
        "governance_level": "CONFIDENCIAL",
        "source_ref": "filename.pdf"
      },
      "graph_properties": { "version": "1.0", "author": "IAP" }
    }
```

---

## 4. Requisitos de Experiencia de Usuario (UX)
*   **Feedback de Proceso**: 
    *   Si es Quick: "Indexando fragmentos...".
    *   Si es Atomic: "Validando integridad en Grafo y Vectores...".
*   **Manejo de Errores**: Si la transacción atómica falla en Neo4j, el frontend debe capturar el error 500 y notificar: "Error de consistencia ontológica. El documento no fue indexado".
*   **Limpieza de Estado**: Tras un éxito, resetear los campos semánticos pero mantener el modo elegido para cargas masivas.

---

## 5. Criterios de Aceptación para Gemini Code Assist
*   El código debe usar **Vue 3 Composition API** (`<script setup>`).
*   Los estilos deben ser 100% **Tailwind CSS**.
*   Implementar una validación que impida el envío si `isSemanticMode` es true pero no se ha seleccionado una `owl_class`.

