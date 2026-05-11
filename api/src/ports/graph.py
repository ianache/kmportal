"""
Graph Port - Abstract interface for graph database operations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class OWLClassInfo:
    id: str
    label: str
    uri: str
    domain_id: str
    metadata: dict[str, Any] | None = None
    subclass_of: list[str] = field(default_factory=list)
    equivalent_to: list[str] = field(default_factory=list)
    restrictions: list[dict] = field(default_factory=list)
    annotations: dict[str, str] = field(default_factory=dict)


@dataclass
class OWLPropertyInfo:
    id: str
    label: str
    uri: str
    property_type: str
    domain_id: str
    source_class_id: str
    target_class_id: str
    metadata: dict[str, Any] | None = None


@dataclass
class EntityInfo:
    """An instance (ABox) of an OWL Class."""
    id: str
    label: str  # Name or identifier of the instance
    class_id: str  # Reference to the OWLClass id
    domain_id: str
    document_id: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class RelationInfo:
    """An instance of an OWL Property connecting two Entities."""
    source_entity_id: str
    target_entity_id: str
    property_id: str  # Reference to the OWLProperty id
    domain_id: str
    metadata: dict[str, Any] | None = None


class GraphPort(ABC):
    @abstractmethod
    async def upsert_class(self, class_info: OWLClassInfo) -> None:
        pass

    @abstractmethod
    async def delete_class(self, class_id: str, domain_id: str) -> bool:
        pass

    @abstractmethod
    async def upsert_property(self, property_info: OWLPropertyInfo) -> None:
        pass

    @abstractmethod
    async def delete_property(self, property_id: str, domain_id: str) -> bool:
        pass

    @abstractmethod
    async def upsert_entity(self, entity_info: EntityInfo) -> None:
        """Create or update an instance node and link it to its Class."""
        pass

    @abstractmethod
    async def upsert_relation(self, relation_info: RelationInfo) -> None:
        """Create a relationship between entities based on an OWL Property."""
        pass

    @abstractmethod
    async def get_ontology(self, domain_id: str) -> dict[str, Any]:
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass
