"""Document ingestion module."""

from ingestion.chunking import Chunk, ChunkingConfig, chunk_document
from ingestion.extractors import TextExtractionError, UnsupportedFormatError, extract_text

__all__ = [
    "extract_text",
    "UnsupportedFormatError",
    "TextExtractionError",
    "chunk_document",
    "ChunkingConfig",
    "Chunk",
]
