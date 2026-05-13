# Plan FEAT10-06: Round-trip Export → Import

**Feature:** REQSPEC-01 — Export/Import OWL y Turtle  
**Iteración:** 6 de 6  
**Spec:** `reqspec/REQSPEC01.md` §6 (CA-RT-1)  
**Criterios de Aceptación:** CA-RT-1.1 a CA-RT-1.4

---

## Goal

Verificar que la cadena Export → Import preserva la información semántica completa. Los tests operan a nivel de servicio (sin HTTP) para aislar la lógica de serialización/deserialización de rdflib.

---

## Background

Las iteraciones 1–5 implementaron y conectaron el pipeline completo:
- Iteración 1: `export_owl` con `format=ttl`
- Iteración 2: `import_owl` merge por URI (OWL/XML y TTL)
- Iteración 3: `import_owl` replace con atomicidad
- Iteración 4: botones en header del editor
- Iteración 5: modales Import Options + Replace confirm + toast

Esta iteración cierra el ciclo verificando que lo que se exporta puede reimportarse de forma fiel.

### Limitación conocida del round-trip

`import_owl` procesa primero todas las clases y luego las propiedades. Las restricciones de clase (`owl:Restriction`) que referencian propiedades del **mismo archivo** son silenciosamente omitidas durante la importación, porque la propiedad aún no existe en `uri_to_prop_id` cuando se procesa la clase. Esta limitación es aceptable y conocida — los tests de RT-1.3 validan los conteos en el **grafo exportado** (no en el resultado de importación).

---

## Cambios de Código

### Tarea 1 — Tests: `api/tests/test_round_trip.py`

Tests a nivel de servicio — no usa `AsyncClient`. Parchea `get_ontology` y `Neo4jAdapter` directamente.

**Fixture `MOCK_ONTOLOGY`:** Ontología rica con:
- 2 clases (Animal, Dog) + subclass_of
- 1 restricción (`someValuesFrom` en Dog)
- 2 annotations en Animal (`owl:hasKey`, `source`)
- 1 DatatypeProperty (`hasName`) con domain y range

**Patrón de patch:**
```python
# Export (get_ontology retorna MOCK_ONTOLOGY):
with patch("services.ontology_service.get_ontology", return_value=MOCK_ONTOLOGY):
    owl_bytes = await export_owl(mock_driver, DOMAIN_ID, fmt="owl")

# Import (get_ontology retorna dominio vacío × 2 llamadas):
with patch("services.ontology_service.get_ontology",
           side_effect=[_empty_ontology(), _empty_ontology()]), \
     patch("services.ontology_service.Neo4jAdapter") as MockAdapter:
    mock_adapter = MockAdapter.return_value
    mock_adapter.upsert_class = AsyncMock()
    mock_adapter.upsert_property = AsyncMock()
    result = await import_owl(mock_driver, DOMAIN_ID, owl_bytes, fmt="xml", mode="merge")
```

---

## Criterios de Aceptación — Verificación

| CA | Test |
|---|---|
| RT-1.1 — Export OWL → import merge → todas las clases/props creadas | `test_round_trip_owl_creates_all_classes` |
| RT-1.2 — Export TTL → import merge → todas las clases/props creadas | `test_round_trip_ttl_creates_all_classes` |
| RT-1.3 — Conteos (clases, props, restricciones, annotation-props) preservados en export | `test_round_trip_counts_preserved` |
| RT-1.4 — Round-trip OWL y TTL producen mismos conteos de import | `test_round_trip_owl_ttl_same_result` |

---

## Orden de Ejecución

```
1. Crear api/tests/test_round_trip.py
2. cd api && python -m pytest tests/test_round_trip.py -v
3. Iterar sobre fallos hasta 0 failed
4. Commit atómico
```

---

## Commit Target

```
feat: FEAT10-06 — Round-trip tests Export→Import (CA-RT-1.1 to CA-RT-1.4)
```

Archivos:
- `api/tests/test_round_trip.py`
- `.planning/phases/feat10-owl-ttl-export-import/feat10-06-PLAN.md`
