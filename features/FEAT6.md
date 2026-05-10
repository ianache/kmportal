# REQSPEC: KMPortal - Ingesta Atómica y Búsqueda Híbrida Semántica

## 1. Contexto del Sistema y Objetivo
Se requiere implementar el motor de persistencia y recuperación híbrida para `kmportal` (Knowledge Management Platform). El objetivo es cerrar la brecha entre la búsqueda vectorial y el contexto estructural de la ontología, garantizando que cada resultado entregado tenga un linaje semántico verificable.

**Stack Tecnológico:**
* Backend: Python 3.10+, FastAPI
* Validación: Pydantic v2
* Base de Datos Vectorial: ChromaDB
* Base de Datos de Grafo: Neo4j (neo4j-driver)
* Gobernanza: Alineación con ISO 27001 (control de acceso y etiquetado).

---

## 2. Modelos de Datos (Pydantic)
Generar los siguientes modelos de validación en `models/semantic.py`:

1. `SemanticLink`: Contiene `link_id` (UUID4 autogenerado), `owl_class` (str), `governance_level` (str, default "CONFIDENCIAL"), `source_ref` (str).
2. `IngestionPayload`: Contiene `content` (str), `metadata` (SemanticLink), `graph_properties` (Dict[str, str]).
3. `GraphNode`: Contiene `id` (str), `label` (str), `name` (str).
4. `GraphEdge`: Contiene `source` (str), `target` (str), `relation_type` (str).
5. `SemanticProvenance`: Contiene `owl_class` (str), `iso_compliance` (str), `nodes` (List[GraphNode]), `edges` (List[GraphEdge]).
6. `HybridSearchResult`: Contiene `link_id` (UUID), `content` (str), `score` (float), `source_file` (str), `provenance` (SemanticProvenance).

---

## 3. Componente 1: IngestionCoordinator (Servicio)
Crear la clase `IngestionCoordinator` en `services/ingestion.py`.

**Responsabilidad:** Garantizar la integridad referencial (Transacción Atómica) entre ChromaDB y Neo4j usando el `link_id`.

**Método Principal:** `async def execute_atomic_ingestion(self, payload: IngestionPayload)`
**Lógica de Ejecución Estricta:**
1. Extraer el `link_id` (como string) del payload.
2. **FASE 1 (Neo4j):** Ejecutar una escritura síncrona. 
   * Cypher Query Esperado: 
     `MERGE (c:OWLClass {name: $owl_class}) `
     `CREATE (n:KnowledgeItem {id: $link_id}) `
     `SET n += $props `
     `CREATE (n)-[:INSTANCE_OF]->(c)`
   * Si falla Neo4j, lanzar excepción y abortar (NO escribir en ChromaDB).
3. **FASE 2 (ChromaDB):** Insertar en la colección de ChromaDB.
   * `documents`: [payload.content]
   * `ids`: [link_id]
   * `metadatas`: Diccionario inyectando `link_id`, `owl_class`, `governance`, `source`.
4. Retornar status success y el `link_id`.

---

## 4. Componente 2: Endpoint de Búsqueda Híbrida
Crear el router en `api/routes/search.py`.

**Endpoint:** `GET /search/hybrid`
**Response Model:** `List[HybridSearchResult]`

**Lógica de Ejecución Estricta:**
1. Recibir `q` (str, query) y `limit` (int, default 5).
2. Consultar ChromaDB (`collection.query`) usando `q`. Retornar `documents`, `metadatas`, y `distances`.
3. Iterar sobre los resultados. Extraer el `link_id` del metadato.
4. Con el `link_id`, consultar Neo4j mediante la siguiente query:
   * Cypher Query Esperado:
     `MATCH (n:KnowledgeItem {id: $link_id})-[:INSTANCE_OF]->(c:OWLClass) `
     `OPTIONAL MATCH (n)-[r]->(related:KnowledgeItem) `
     `RETURN c.name as owl_class, `
     `collect(DISTINCT {id: related.id, label: labels(related)[0], name: related.name}) as related_nodes, `
     `collect(DISTINCT {source: $link_id, target: related.id, type: type(r)}) as relations`
5. Mapear los resultados de Neo4j a los esquemas `GraphNode` y `GraphEdge`.
6. Ensamblar y retornar la lista de `HybridSearchResult`. La puntuación (`score`) debe calcularse como `1.0 - distance`.

---

## 5. Criterios de Aceptación y Restricciones (Reglas del Agente)
* **Manejo de Errores:** Implementar bloques try/except. Los fallos en la base de datos deben retornar un `HTTPException` 500 con un detalle claro.
* **Tipado Estricto:** Usar Type Hints en todas las firmas de funciones.
* **Async/Await:** El endpoint de FastAPI debe ser asíncrono. Asegurar que las llamadas I/O a Neo4j no bloqueen el event loop (considerar usar el driver async de Neo4j si es posible, o ejecutar en threadpool).
* **Gobernanza:** No mutar ni obviar el campo `governance_level` o `iso_compliance`. Es vital para la seguridad.
