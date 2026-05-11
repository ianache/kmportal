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
        query = """
        MERGE (c:OWLClass {id: $id, domain_id: $domain_id})
        SET c.label = $label,
            c.uri = $uri,
            c.updated_at = datetime()
        """
        if info.metadata:
            for k in info.metadata:
                query += f"\nSET c.{k} = $metadata.{k}"
        
        async with self._driver.session() as session:
            await session.run(query, id=info.id, domain_id=info.domain_id, 
                              label=info.label, uri=info.uri, metadata=info.metadata or {})

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
        if info.property_type == "DatatypeProperty":
            query = """
            MERGE (s:OWLClass {id: $source_id, domain_id: $domain_id})
            MERGE (p:OWLProperty {id: $id, domain_id: $domain_id})
            SET p.label = $label,
                p.uri = $uri,
                p.property_type = $property_type,
                p.range_xsd = $target_id,
                p.updated_at = datetime()
            MERGE (s)-[:HAS_DOMAIN]->(p)
            """
        else:
            query = """
            MERGE (s:OWLClass {id: $source_id, domain_id: $domain_id})
            MERGE (t:OWLClass {id: $target_id, domain_id: $domain_id})
            MERGE (p:OWLProperty {id: $id, domain_id: $domain_id})
            SET p.label = $label,
                p.uri = $uri,
                p.property_type = $property_type,
                p.updated_at = datetime()
            MERGE (s)-[:HAS_DOMAIN]->(p)
            MERGE (p)-[:HAS_RANGE]->(t)
            """
        async with self._driver.session() as session:
            await session.run(
                query,
                id=info.id, domain_id=info.domain_id,
                label=info.label, uri=info.uri,
                property_type=info.property_type,
                source_id=info.source_class_id,
                target_id=info.target_class_id
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

    async def get_ontology(self, domain_id: str) -> dict[str, Any]:
        async with self._driver.session() as session:
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
                domain_id=domain_id
            )
            concepts = []
            async for record in c_res:
                node = record["c"]
                concepts.append({
                    "id": node["id"],
                    "uri": node.get("uri") or "",
                    "label": node.get("label") or "Unknown",
                    "comment": node.get("comment"),
                    "domain_id": domain_id
                })

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
                node = record["p"]
                properties.append({
                    "id": node["id"],
                    "uri": node.get("uri") or "",
                    "label": node.get("label") or "Unknown",
                    "property_type": node.get("property_type") or "ObjectProperty",
                    "source_class_id": record["source_id"],
                    "target_class_id": record["target_id"],
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
