"""Document ingestion module."""

from ingestion.extractors import extract_text, UnsupportedFormatError, TextExtractionError
from ingestion.chunking import chunk_document, ChunkingConfig, Chunk

__all__ = [
    "extract_text",
    "UnsupportedFormatError",
    "TextExtractionError",
    "chunk_document",
    "ChunkingConfig",
    "Chunk",
]