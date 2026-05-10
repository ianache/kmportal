"""
Ontology Extractor - Uses LLM to extract structured entities and relations 
based on a domain's OWL ontology.
"""

import json
import logging
import os
from typing import Any
from uuid import UUID

from ports.embedding import EmbeddingPort
from schemas import ExtractionResult, ExtractedEntity, ExtractedRelation

logger = logging.getLogger(__name__)

class OntologyExtractor:
    """
    Orchestrates the extraction of knowledge from text using an LLM
    and a specific domain ontology.
    """

    def __init__(self, embedding_provider: EmbeddingPort):
        self.embedding_provider = embedding_provider
        # Prefer the key stored on the embedding adapter (Gemini), fall back to env var.
        self.api_key = (
            getattr(embedding_provider, "_api_key", None)
            or os.getenv("GEMINI_API_KEY")
        )
        self.model = "gemini-2.5-flash"

    async def extract(
        self, 
        text: str, 
        ontology: dict[str, Any],
        domain_id: UUID
    ) -> ExtractionResult:
        """
        Extract entities and relations from text based on ontology.
        """
        if not self.api_key:
            logger.warning(
                "No GEMINI_API_KEY found (embedding provider has no _api_key and "
                "GEMINI_API_KEY env var is unset). Ontology extraction skipped."
            )
            return ExtractionResult(entities=[], relations=[])

        # 1. Prepare ontology context for the prompt
        concepts = [f"- {c['label']} (ID: {c['id']})" for c in ontology.get("concepts", [])]
        properties = []
        for p in ontology.get("properties", []):
            properties.append(
                f"- {p['label']} (ID: {p['id']}): Connects {p['source_class_id']} to {p['target_class_id']}"
            )

        prompt = f"""
        You are a Knowledge Graph expert. Extract structured information from the TEXT below 
        based ONLY on the provided ONTOLOGY.

        ONTOLOGY CONCEPTS (Classes):
        {chr(10).join(concepts)}

        ONTOLOGY PROPERTIES (Relationships):
        {chr(10).join(properties)}

        TEXT:
        \"\"\"{text}\"\"\"

        INSTRUCTIONS:
        1. Identify specific instances of the CONCEPTS mentioned in the text.
        2. Identify relationships between these instances based on the PROPERTIES.
        3. For each entity, provide a clear label (the name as it appears in the text).
        4. Provide the result in VALID JSON format.

        JSON FORMAT:
        {{
            "entities": [
                {{"label": "Entity Name", "class_id": "concept_id_from_ontology", "metadata": {{}}}}
            ],
            "relations": [
                {{"source_label": "Source Entity Name", "target_label": "Target Entity Name", "property_id": "property_id_from_ontology", "metadata": {{}}}}
            ]
        }}
        """

        try:
            import httpx
            async with httpx.AsyncClient(timeout=60.0) as client:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
                
                payload = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "response_mime_type": "application/json",
                    }
                }
                
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                result_data = response.json()
                content = result_data["candidates"][0]["content"]["parts"][0]["text"]
                
                # Parse JSON
                extraction_dict = json.loads(content)
                
                return ExtractionResult(
                    entities=[ExtractedEntity(**e) for e in extraction_dict.get("entities", [])],
                    relations=[ExtractedRelation(**r) for r in extraction_dict.get("relations", [])]
                )

        except Exception as e:
            logger.error(f"Error during ontology-driven extraction: {e}")
            # Fail gracefully returning empty result
            return ExtractionResult(entities=[], relations=[])
