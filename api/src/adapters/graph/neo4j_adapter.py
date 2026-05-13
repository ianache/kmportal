"""
Neo4j Adapter - Implementation of GraphPort using Neo4j with Reification pattern.
"""

import logging
from typing import Any
from neo4j import AsyncDriver

from ports.graph import GraphPort, OWLClassInfo, OWLPropertyInfo, EntityInfo, RelationInfo

logger = logging.getLogger(__name__)


class Neo4jAdapter(GraphPort):
    def __init__(self, driver: AsyncDriver):
        self._driver = driver

    async def upsert_class(self, info: OWLClassInfo) -> None:
        import json

        comment = (info.metadata or {}).get("comment")
        restrictions_json = json.dumps(info.restrictions or [])
        annotations_json = json.dumps(info.annotations or {})

        async with self._driver.session() as session:
            # 1. Upsert the class node with all scalar fields
            await session.run(
                """
                MERGE (c:OWLClass {id: $id, domain_id: $domain_id})
                SET c.label = $label,
                    c.uri = $uri,
                    c.comment = $comment,
                    c.restrictions = $restrictions,
                    c.annotations = $annotations,
                    c.updated_at = datetime()
                """,
                id=info.id, domain_id=info.domain_id,
                label=info.label, uri=info.uri,
                comment=comment,
                restrictions=restrictions_json,
                annotations=annotations_json,
            )
            # 2. Remove stale SUBCLASS_OF relationships
            await session.run(
                """
                MATCH (c:OWLClass {id: $id, domain_id: $domain_id})
                OPTIONAL MATCH (c)-[r:SUBCLASS_OF]->()
                DELETE r
                """,
                id=info.id, domain_id=info.domain_id,
            )
            # 3. Create new SUBCLASS_OF relationships
            if info.subclass_of:
                await session.run(
                    """
                    MATCH (c:OWLClass {id: $id, domain_id: $domain_id})
                    UNWIND $parents AS parent_id
                    MERGE (p:OWLClass {id: parent_id, domain_id: $domain_id})
                    MERGE (c)-[:SUBCLASS_OF]->(p)
                    """,
                    id=info.id, domain_id=info.domain_id, parents=info.subclass_of,
                )
            # 4. Remove stale EQUIVALENT_TO relationships
            await session.run(
                """
                MATCH (c:OWLClass {id: $id, domain_id: $domain_id})
                OPTIONAL MATCH (c)-[r:EQUIVALENT_TO]->()
                DELETE r
                """,
                id=info.id, domain_id=info.domain_id,
            )
            # 5. Create new EQUIVALENT_TO relationships
            if info.equivalent_to:
                await session.run(
                    """
                    MATCH (c:OWLClass {id: $id, domain_id: $domain_id})
                    UNWIND $equivs AS equiv_id
                    MERGE (e:OWLClass {id: equiv_id, domain_id: $domain_id})
                    MERGE (c)-[:EQUIVALENT_TO]->(e)
                    """,
                    id=info.id, domain_id=info.domain_id, equivs=info.equivalent_to,
                )

    async def delete_class(self, class_id: str, domain_id: str) -> bool:
        query = """
        MATCH (c:OWLClass {id: $id, domain_id: $domain_id})
        DETACH DELETE c
        RETURN count(c) as deleted
        """
        async with self._driver.session() as session:
            result = await session.run(query, id=class_id, domain_id=domain_id)
            record = await result.single()
            return record["deleted"] > 0 if record else False

    async def upsert_property(self, info: OWLPropertyInfo) -> None:
        # Reification: (Source:OWLClass)-[:HAS_DOMAIN]->(Prop:OWLProperty)-[:HAS_RANGE]->(Target:OWLClass)
        # DatatypeProperty ranges are XSD URIs, NOT OWL classes — store them as a property on
        # the OWLProperty node (range_xsd) to avoid creating phantom :OWLClass nodes.
        async with self._driver.session() as session:
            # Upsert the property node
            await session.run(
                """
                MERGE (p:OWLProperty {id: $id, domain_id: $domain_id})
                SET p.label = $label, p.uri = $uri,
                    p.property_type = $property_type, p.updated_at = datetime()
                """,
                id=info.id, domain_id=info.domain_id,
                label=info.label, uri=info.uri, property_type=info.property_type,
            )
            # Remove stale HAS_DOMAIN (prevents duplicate edges on re-save)
            await session.run(
                """
                MATCH (p:OWLProperty {id: $id, domain_id: $domain_id})
                OPTIONAL MATCH ()-[r:HAS_DOMAIN]->(p) DELETE r
                """,
                id=info.id, domain_id=info.domain_id,
            )
            # Re-create HAS_DOMAIN from the correct source class
            await session.run(
                """
                MATCH (s:OWLClass {id: $source_id, domain_id: $domain_id})
                MATCH (p:OWLProperty {id: $id, domain_id: $domain_id})
                MERGE (s)-[:HAS_DOMAIN]->(p)
                """,
                id=info.id, domain_id=info.domain_id, source_id=info.source_class_id,
            )
            if info.property_type == "DatatypeProperty":
                await session.run(
                    "MATCH (p:OWLProperty {id: $id, domain_id: $domain_id}) SET p.range_xsd = $target_id",
                    id=info.id, domain_id=info.domain_id, target_id=info.target_class_id,
                )
            else:
                # Remove stale HAS_RANGE then re-create
                await session.run(
                    """
                    MATCH (p:OWLProperty {id: $id, domain_id: $domain_id})
                    OPTIONAL MATCH (p)-[r:HAS_RANGE]->() DELETE r
                    """,
                    id=info.id, domain_id=info.domain_id,
                )
                await session.run(
                    """
                    MERGE (t:OWLClass {id: $target_id, domain_id: $domain_id})
                    WITH t
                    MATCH (p:OWLProperty {id: $id, domain_id: $domain_id})
                    MERGE (p)-[:HAS_RANGE]->(t)
                    """,
                    id=info.id, domain_id=info.domain_id, target_id=info.target_class_id,
                )

    async def upsert_entity(self, info: "EntityInfo") -> None:
        query = """
        MATCH (c:OWLClass {id: $class_id, domain_id: $domain_id})
        MERGE (e:Entity {id: $id, domain_id: $domain_id})
        SET e.label = $label,
            e.updated_at = datetime()
        
        // Link to its class (ABox -> TBox)
        MERGE (e)-[:INSTANCE_OF]->(c)
        """
        
        if info.document_id:
            query += "\nSET e.source_document_id = $doc_id"
            
        if info.metadata:
            for k in info.metadata:
                query += f"\nSET e.{k} = $metadata.{k}"
                
        async with self._driver.session() as session:
            await session.run(
                query,
                id=info.id, domain_id=info.domain_id,
                label=info.label, class_id=info.class_id,
                doc_id=info.document_id,
                metadata=info.metadata or {}
            )

    async def upsert_relation(self, info: "RelationInfo") -> None:
        # Dynamic relationship type based on the OWLProperty label
        # We fetch the property label first
        async with self._driver.session() as session:
            prop_res = await session.run(
                "MATCH (p:OWLProperty {id: $id, domain_id: $domain_id}) RETURN p.label as type",
                id=info.property_id, domain_id=info.domain_id
            )
            record = await prop_res.single()
            rel_type = record["type"].upper().replace(" ", "_") if record else "RELATED_TO"
            
            query = f"""
            MATCH (s:Entity {{id: $source_id, domain_id: $domain_id}})
            MATCH (t:Entity {{id: $target_id, domain_id: $domain_id}})
            MATCH (p:OWLProperty {{id: $prop_id, domain_id: $domain_id}})
            
            // Create the relation
            MERGE (s)-[r:{rel_type}]->(t)
            SET r.property_id = $prop_id,
                r.updated_at = datetime()
            """
            
            if info.metadata:
                for k in info.metadata:
                    query += f"\nSET r.{k} = $metadata.{k}"
                    
            await session.run(
                query,
                source_id=info.source_entity_id,
                target_id=info.target_entity_id,
                prop_id=info.property_id,
                domain_id=info.domain_id,
                metadata=info.metadata or {}
            )

    async def delete_property(self, property_id: str, domain_id: str) -> bool:
        query = """
        MATCH (p:OWLProperty {id: $id, domain_id: $domain_id})
        DETACH DELETE p
        RETURN count(p) as deleted
        """
        async with self._driver.session() as session:
            result = await session.run(query, id=property_id, domain_id=domain_id)
            record = await result.single()
            return record["deleted"] > 0 if record else False

    async def delete_all_ontology(self, domain_id: str) -> tuple[int, int]:
        """Delete all OWLClass and OWLProperty nodes for a domain in one pass."""
        async with self._driver.session() as session:
            c_result = await session.run(
                """
                MATCH (c:OWLClass {domain_id: $domain_id})
                WITH collect(c) AS nodes, count(c) AS n
                FOREACH (c IN nodes | DETACH DELETE c)
                RETURN n
                """,
                domain_id=domain_id,
            )
            c_record = await c_result.single()
            classes_deleted = c_record["n"] if c_record else 0

            p_result = await session.run(
                """
                MATCH (p:OWLProperty {domain_id: $domain_id})
                WITH collect(p) AS nodes, count(p) AS n
                FOREACH (p IN nodes | DETACH DELETE p)
                RETURN n
                """,
                domain_id=domain_id,
            )
            p_record = await p_result.single()
            props_deleted = p_record["n"] if p_record else 0

        return classes_deleted, props_deleted

    async def get_ontology(self, domain_id: str) -> dict[str, Any]:
        async with self._driver.session() as session:
            import json as _json

            # Exclude phantom XSD nodes — real domain classes use UUID4 as id,
            # XSD phantom nodes have URIs (e.g. http://www.w3.org/2001/XMLSchema#string)
            c_res = await session.run(
                """
                MATCH (c:OWLClass {domain_id: $domain_id})
                WHERE NOT c.id STARTS WITH 'http://'
                  AND NOT c.id STARTS WITH 'https://'
                  AND c.label IS NOT NULL
                RETURN c
                """,
                domain_id=domain_id,
            )
            concepts_raw = []
            async for record in c_res:
                node = record["c"]
                try:
                    restrictions = _json.loads(node.get("restrictions") or "[]")
                except Exception:
                    restrictions = []
                try:
                    annotations = _json.loads(node.get("annotations") or "{}")
                except Exception:
                    annotations = {}
                concepts_raw.append({
                    "id": node["id"],
                    "uri": node.get("uri") or "",
                    "label": node.get("label") or "Unknown",
                    "comment": node.get("comment"),
                    "domain_id": domain_id,
                    "subclass_of": [],
                    "equivalent_to": [],
                    "restrictions": restrictions,
                    "annotations": annotations,
                })

            concept_map = {c["id"]: c for c in concepts_raw}

            # Collect SUBCLASS_OF relationships
            sc_res = await session.run(
                """
                MATCH (c:OWLClass {domain_id: $domain_id})-[:SUBCLASS_OF]->(p:OWLClass)
                WHERE NOT c.id STARTS WITH 'http://'
                RETURN c.id AS child_id, collect(p.id) AS parent_ids
                """,
                domain_id=domain_id,
            )
            async for record in sc_res:
                if record["child_id"] in concept_map:
                    concept_map[record["child_id"]]["subclass_of"] = list(record["parent_ids"])

            # Collect EQUIVALENT_TO relationships
            eq_res = await session.run(
                """
                MATCH (c:OWLClass {domain_id: $domain_id})-[:EQUIVALENT_TO]->(e:OWLClass)
                WHERE NOT c.id STARTS WITH 'http://'
                RETURN c.id AS class_id, collect(e.id) AS equiv_ids
                """,
                domain_id=domain_id,
            )
            async for record in eq_res:
                if record["class_id"] in concept_map:
                    concept_map[record["class_id"]]["equivalent_to"] = list(record["equiv_ids"])

            concepts = list(concept_map.values())

            # OPTIONAL MATCH covers both ObjectProperties (HAS_RANGE → OWLClass)
            # and DatatypeProperties (range stored as p.range_xsd, no HAS_RANGE edge)
            p_res = await session.run(
                """
                MATCH (s:OWLClass)-[:HAS_DOMAIN]->(p:OWLProperty {domain_id: $domain_id})
                OPTIONAL MATCH (p)-[:HAS_RANGE]->(t:OWLClass)
                RETURN p, s.id as source_id,
                       coalesce(t.id, p.range_xsd) as target_id
                """,
                domain_id=domain_id
            )
            properties = []
            async for record in p_res:
                target_id = record["target_id"]
                if not target_id:
                    # Skip dangling properties with no resolvable range (no HAS_RANGE and no range_xsd).
                    # This preserves the previous behaviour of the required MATCH.
                    continue
                node = record["p"]
                properties.append({
                    "id": node["id"],
                    "uri": node.get("uri") or "",
                    "label": node.get("label") or "Unknown",
                    "property_type": node.get("property_type") or "ObjectProperty",
                    "source_class_id": record["source_id"],
                    "target_class_id": target_id,
                    "comment": node.get("comment"),
                    "domain_id": domain_id
                })
                
            return {
                "domain_id": domain_id,
                "concepts": concepts,
                "properties": properties
            }

    async def health_check(self) -> bool:
        try:
            async with self._driver.session() as session:
                await session.run("RETURN 1")
                return True
        except Exception:
            return False

    async def close(self) -> None:
        await self._driver.close()
