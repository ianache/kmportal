# REQSPEC: Ontology Editor — Panel "OWL Class Definition" + Herencia Visual

## 1. Objetivo y Contexto

Reemplazar el actual flujo de creación de clases OWL (basado en `window.prompt()`) por un panel lateral derecho estructurado que soporte el ciclo de vida completo de una clase: **crear**, **editar** y **visualizar** su definición formal.

El panel es activado por dos eventos:
1. **Drag & drop** del elemento "Class" desde la paleta al canvas → modo *Create*.
2. **Click en un nodo de clase** existente en el canvas → modo *Edit*.

Adicionalmente, las relaciones `subClassOf` declaradas en el panel deben dibujarse automáticamente en el canvas usando la notación UML de herencia (flecha sólida con punta vacía/hueca apuntando al padre, sin etiqueta de texto).

---

## 2. Diseño de referencia

Pantalla Stitch: `projects/4870672725458937620/screens/ebfbbbcbf641483cac453e090dd05b14`  
Título: **"Ontology Editor: New Class Definition"**

---

## 3. Componente de UI: Panel `OWLClassPanel.vue`

Panel deslizante lateral derecho (reemplaza el actual `OntologyProperties.vue` cuando hay una clase seleccionada o se está creando una).

### 3.1 Cabecera del panel

| Elemento | Detalle |
|---|---|
| Título | "New OWL Class Definition" (modo create) / "Edit OWL Class" (modo edit) |
| Botón X | Cierra el panel y deselecciona |

### 3.2 Sección 1 — Core Identification

| Campo | Tipo | Requerido | Notas |
|---|---|---|---|
| `uri` | Text input | Sí | Auto-generado como `http://km.local/ontology#{label_slug}` si se deja vacío al crear |
| `label` | Text input | Sí | Nombre legible de la clase |
| `comment` | Textarea | No | Descripción / anotación `rdfs:comment` |

### 3.3 Sección 2 — Hierarchy & Logic

#### Subclass Of
- **Campo**: selector múltiple de clases existentes del dominio.
- **Interacción**: botón `+ Add` abre un dropdown con búsqueda de las clases disponibles. Las clases seleccionadas se muestran como chips removibles (`×`).
- **Efecto en canvas**: por cada clase padre seleccionada que ya esté presente en el diagrama activo, se dibuja automáticamente una **flecha de herencia UML** entre la clase hijo y la clase padre (ver §5).
- **Persistencia**: se almacena como relaciones `SUBCLASS_OF` en Neo4j.

#### Equivalent To
- **Campo**: selector múltiple de clases (misma interacción que Subclass Of).
- **Estado vacío**: texto "No equivalence rules defined".
- **Persistencia**: relaciones `EQUIVALENT_TO` en Neo4j.

### 3.4 Sección 3 — Property Restrictions

Lista de restricciones OWL sobre propiedades existentes del dominio.

Cada restricción tiene:
| Sub-campo | Tipo | Opciones |
|---|---|---|
| ObjectProperty | Dropdown | Propiedades del dominio (tipo ObjectProperty) |
| Restriction Type | Dropdown | `Some (∃)`, `All (∀)`, `Cardinality` |

- Botón `+ Add Restriction` añade una fila nueva.
- Cada fila tiene botón `×` para eliminar.
- **Persistencia**: almacenadas como propiedad JSON `restrictions` en el nodo `OWLClass` de Neo4j.

### 3.5 Sección 4 — Metadata & Annotations

| Elemento | Tipo | Notas |
|---|---|---|
| Annotations | Lista key-value dinámica | Botón `+ Add Annotation` añade par clave/valor |
| Has Key | Checkbox | Flag booleano `owl:hasKey` |

- Las annotations se almacenan como propiedad JSON `annotations` en el nodo `OWLClass`.

### 3.6 Sección 5 — Data Attributes (no se implementará en esta etapa pues ya se implementa a través del editor visual de ontologia)

Lista de `DatatypeProperty` declaradas para esta clase.

- **Estado vacío**: "No data attributes defined yet".
- Cada atributo muestra: nombre, tipo XSD, opcional flag de cardinalidad.
- Botón `+ Add Attribute` abre inline form: nombre, tipo XSD (dropdown: `string`, `integer`, `boolean`, `date`, `decimal`).
- **Persistencia**: crea un `DatatypeProperty` en Neo4j vinculado a la clase como `source_class_id`.

### 3.7 Footer del panel

| Botón | Modo Create | Modo Edit |
|---|---|---|
| Primary | "Create Class" | "Save Changes" |
| Secondary | "Cancel" | "Cancel" |

---

## 4. Notación Visual de Herencia en el Canvas

### 4.1 Tipo de arista

Las relaciones `SUBCLASS_OF` se representan con un tipo de edge distinto a las relaciones de propiedad:

| Atributo | Valor |
|---|---|
| Línea | Sólida (no punteada) |
| Color | `#1D1D1F` (negro/gris oscuro, diferente al azul de las propiedades) |
| Grosor | `2px` |
| Marcador final | Flecha triangular **hueca/vacía** apuntando al nodo padre (`markerEnd: 'arrowclosed'` con fill transparente) |
| Etiqueta | **Ninguna** (el símbolo ya significa "Is-A") |
| `edgeType` interno | `'subclass'` |

### 4.2 Renderizado en `OntologyCanvas.vue`

`flowEdges` debe diferenciar entre edges de propiedad (actuales) y edges de herencia (nuevos):

```
edges de propiedad → azul (#0058bc), label con nombre de propiedad
edges de herencia  → negro (#1D1D1F), sin label, punta hueca
```

### 4.3 Auto-derivación vs. almacenamiento en diagrama

Las aristas de herencia **se auto-derivan** del campo `subclass_of` de cada clase:
- Si la clase A tiene `subclass_of: [B]` y ambas (A y B) están presentes en el diagrama activo como nodos, se genera automáticamente un edge `subclass` de A → B.
- **No se almacenan** en la tabla `diagrams` de PostgreSQL como DiagramEdge; se calculan en tiempo de renderizado por el computed `flowEdges`.
- Esto evita inconsistencias cuando se actualiza la jerarquía y el diagrama no fue guardado.

---

## 5. Cambios Necesarios en Backend

### 5.1 `ports/graph.py` — `OWLClassInfo`

Añadir campos opcionales:

```python
@dataclass
class OWLClassInfo:
    id: str
    label: str
    uri: str
    domain_id: str
    metadata: dict[str, Any] | None = None
    # Nuevos:
    subclass_of: list[str] = field(default_factory=list)   # IDs de clases padre
    equivalent_to: list[str] = field(default_factory=list) # IDs de clases equivalentes
    restrictions: list[dict] = field(default_factory=list) # [{property_id, type}]
    annotations: dict[str, str] = field(default_factory=list) # {key: value}
```

### 5.2 `adapters/graph/neo4j_adapter.py` — `upsert_class`

Extender el Cypher para:
1. Crear/actualizar relaciones `SUBCLASS_OF` hacia las clases padre.
2. Crear/actualizar relaciones `EQUIVALENT_TO`.
3. Almacenar `restrictions` y `annotations` como propiedades JSON en el nodo.

Limpiar relaciones previas antes de re-crear (DETACH + re-MERGE) para soportar edición.

### 5.3 `adapters/graph/neo4j_adapter.py` — `get_ontology`

La query de concepts debe incluir para cada clase:
- `subclass_of`: lista de IDs de clases padre (follow `SUBCLASS_OF` edges)
- `equivalent_to`: lista de IDs de clases equivalentes
- `restrictions`: property JSON del nodo
- `annotations`: property JSON del nodo

### 5.4 `schemas/__init__.py`

Extender `OntologyConceptResponse` y `OntologyConceptCreate`/`Update`:

```python
class OntologyConceptResponse(BaseModel):
    id: str
    domain_id: str
    uri: str
    label: str
    comment: str | None = None
    # Nuevos:
    subclass_of: list[str] = []
    equivalent_to: list[str] = []
    restrictions: list[dict] = []
    annotations: dict[str, str] = {}
```

---

## 6. Cambios Necesarios en Frontend (`domains-ui`)

### 6.1 `OntologyCanvas.vue`

| Cambio | Detalle |
|---|---|
| Eliminar `window.prompt()` en `onDrop` para tipo `class` | Reemplazar por: activar el panel lateral en modo Create, pasando la posición del drop |
| Eliminar `window.prompt()` en `onDrop` para tipo `property` | No cambia (se mantiene el form inline existente) |
| `flowEdges` computed | Añadir auto-derivación de edges `subclass` desde `store.concepts[].subclass_of` |
| Render de edge `subclass` | Línea sólida negra, punta hueca, sin label |

### 6.2 `stores/ontology.ts`

| Cambio | Detalle |
|---|---|
| `createConcept` | Aceptar el payload completo con `subclass_of`, `restrictions`, `annotations` |
| `updateSelectedConcept` | Idem, pasar todos los campos del panel |
| `pendingClassPosition` | Nueva ref `{x, y}` para pasar la posición del drop al panel |
| `panelMode` | Nueva ref `'create' | 'edit' | null'` para controlar visibilidad del panel |

### 6.3 Nuevo componente `OWLClassPanel.vue`

Implementa el panel descrito en §3. Se integra en `OntologyEditor.vue` como una columna lateral derecha que aparece/desaparece según `store.panelMode`.

### 6.4 `OntologyEditor.vue` (layout)

Cuando `panelMode !== null`, la columna derecha muestra `OWLClassPanel.vue` en lugar de `OntologyProperties.vue`.

---

## 7. Criterios de Aceptación

1. **AC-1 Create**: Arrastrar "Class" al canvas abre el panel. Completar URI + Label + "Create Class" añade el nodo al canvas y la clase en Neo4j.
2. **AC-2 Edit**: Hacer click en un nodo existente abre el panel con los datos actuales precargados. "Save Changes" persiste en Neo4j.
3. **AC-3 Subclass arrow**: Declarar `subClassOf: GPS Device` en una clase y tener ambas en el canvas dibuja una flecha sólida con punta hueca de hijo a padre, sin label.
4. **AC-4 No label en herencia**: La flecha de herencia no muestra texto en ningún estado.
5. **AC-5 Validación**: El botón "Create Class" / "Save Changes" está deshabilitado si `label` está vacío.
6. **AC-6 Data attributes**: Añadir un Data Attribute crea el `DatatypeProperty` correspondiente en Neo4j vinculado a la clase.
7. **AC-7 Cancel**: El botón Cancel cierra el panel sin persistir cambios; si fue drag & drop, el nodo no se añade al canvas.
8. **AC-8 Distinción visual**: Las flechas de herencia son visualmente distintas de las de propiedad (color, punta).
9. **AC-9 Consistencia**: Al editar una clase y eliminar un `subClassOf`, la flecha correspondiente desaparece del canvas en tiempo real.
