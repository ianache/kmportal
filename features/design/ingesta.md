# Especificación Técnica: Ingesta de Contenidos Orientada a Ontologías

**Estado:** Implementado (v1.0)
**Fecha:** 2026-05-07
**Componentes Clave:** FastAPI, Neo4j, ChromaDB, Gemini LLM

## 1. Visión General

La solución transforma el proceso de ingesta de documentos de una simple indexación vectorial a una construcción automatizada de Grafos de Conocimiento (Knowledge Graphs). Al procesar un documento, el sistema realiza una extracción dual:
1.  **Representación Vectorial (Sintáctica):** Fragmentación y embeddings para búsqueda semántica.
2.  **Representación en Grafo (Semántica):** Extracción estructurada de entidades y relaciones basada estrictamente en la ontología (OWL) definida para el dominio.

## 2. Arquitectura del Pipeline

El `IngestionService` orquestra dos ramas de procesamiento paralelo tras la extracción inicial de texto plano:

### Rama A: Almacenamiento Vectorial (RAG Tradicional)
- **Motor:** ChromaDB.
- **Proceso:** 
    - Segmentación (Chunking) semántica de 1000 caracteres con 200 de solapamiento.
    - Generación de embeddings mediante `GeminiAdapter`.
    - Almacenamiento en colecciones aisladas por `domain_id`.

### Rama B: Extracción de Conocimiento (Knowledge Graph)
- **Motor:** Neo4j.
- **Proceso:**
    1.  **Carga de Ontología (TBox):** Se recuperan las `OWLClass` y `OWLProperty` del dominio desde Neo4j.
    2.  **Extracción Estructurada:** El `OntologyExtractor` utiliza el modelo `gemini-1.5-flash` con un prompt dinámico que inyecta el esquema de la ontología.
    3.  **Registro de Instancias (ABox):** Los datos extraídos se guardan como nodos `:Entity` vinculados a sus clases `:OWLClass` mediante la relación `:INSTANCE_OF`.

## 3. Modelo de Datos en Neo4j (Patrón de Reificación)

Para maximizar la potencia de consulta y mantener la integridad semántica, se utiliza el patrón de **Reificación de Propiedades**:

### TBox (Esquema)
- `(c:OWLClass {id, label, uri})`
- `(p:OWLProperty {id, label, uri, property_type})`
- Relaciones de esquema: `(:OWLClass)-[:HAS_DOMAIN]->(:OWLProperty)-[:HAS_RANGE]->(:OWLClass)`

### ABox (Datos/Instancias)
- `(e:Entity {id, label, source_document_id})`
- Vínculo semántico: `(e:Entity)-[:INSTANCE_OF]->(c:OWLClass)`
- Relaciones dinámicas: `(e1:Entity)-[:TIPO_RELACION]->(e2:Entity)` donde `TIPO_RELACION` es el label de la `OWLProperty` normalizado.

## 4. Resolución de Entidades (Entity Resolution)

En esta fase inicial, la resolución de entidades se gestiona mediante un **Hash Determinista**:
- `ID = SHA256(label + class_id)`
Esto asegura que si el "Vehículo ABC-123" se menciona en varios documentos o párrafos del mismo dominio, se mapee al mismo nodo único en Neo4j, permitiendo que el grafo se conecte orgánicamente.

## 5. Detalles de Implementación: `OntologyExtractor`

El extractor utiliza el modo JSON de Gemini para garantizar que la salida sea procesable:

```python
# Prompt Logic
prompt = f"""
Extrae información basada SOLAMENTE en esta ONTOLOGÍA:
Conceptos: {concepts}
Propiedades: {properties}
Texto: {text}
"""
```

### Límites de Contexto
Se procesan los primeros **15,000 caracteres** del documento para la extracción de grafo, lo que optimiza costos y asegura que las entidades principales (generalmente presentadas al inicio) sean capturadas.

## 6. Beneficios de la Solución
- **Búsqueda Híbrida:** Permite combinar la flexibilidad de los vectores con la precisión de los grafos.
- **Razonamiento:** Posibilita consultas de tipo "Encuentra todos los conductores que han reportado incidentes en camiones de la marca X", imposibles con solo búsqueda vectorial.
- **Trazabilidad:** Cada nodo de instancia sabe exactamente de qué documento (`source_document_id`) proviene.
