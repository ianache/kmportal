"""Document chunking strategies."""

import re
from dataclasses import dataclass
from typing import List, Iterator


@dataclass
class Chunk:
    """A text chunk with metadata."""
    text: str
    index: int
    start_pos: int
    end_pos: int
    metadata: dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ChunkingConfig:
    """Configuration for document chunking."""
    chunk_size: int = 1000  # Target chunk size in characters
    chunk_overlap: int = 200  # Overlap between chunks
    min_chunk_size: int = 100  # Minimum chunk size
    strategy: str = "semantic"  # "semantic", "fixed", "recursive"
    respect_paragraphs: bool = True
    respect_sentences: bool = True


class ChunkingError(Exception):
    """Error during document chunking."""
    pass


def chunk_by_paragraphs(text: str) -> List[str]:
    """
    Split text into paragraphs.
    
    Args:
        text: Input text
        
    Returns:
        List of paragraphs
    """
    # Split by multiple newlines (paragraphs)
    paragraphs = re.split(r'\n\s*\n', text.strip())
    return [p.strip() for p in paragraphs if p.strip()]


def chunk_by_sentences(text: str) -> List[str]:
    """
    Split text into sentences.
    
    Args:
        text: Input text
        
    Returns:
        List of sentences
    """
    # Simple sentence splitting (handles common cases)
    # More sophisticated: use NLTK or spaCy
    sentence_endings = r'[.!?]+\s+'
    sentences = re.split(sentence_endings, text)
    return [s.strip() for s in sentences if s.strip()]


def semantic_chunking(text: str, config: ChunkingConfig) -> List[Chunk]:
    """
    Chunk text semantically, respecting paragraphs and sentences.
    
    Strategy:
    1. Split into paragraphs
    2. Merge small paragraphs
    3. Split large paragraphs at sentence boundaries
    
    Args:
        text: Input text
        config: Chunking configuration
        
    Returns:
        List of chunks
    """
    paragraphs = chunk_by_paragraphs(text)
    chunks = []
    current_chunk_text = ""
    current_start = 0
    chunk_index = 0
    
    for paragraph in paragraphs:
        paragraph_len = len(paragraph)
        
        # If paragraph is small and fits in current chunk
        if (len(current_chunk_text) + paragraph_len + 2 <= config.chunk_size and 
            paragraph_len < config.chunk_size * 0.8):
            if current_chunk_text:
                current_chunk_text += "\n\n"
            current_chunk_text += paragraph
        else:
            # Save current chunk if it exists
            if current_chunk_text and len(current_chunk_text) >= config.min_chunk_size:
                chunks.append(Chunk(
                    text=current_chunk_text.strip(),
                    index=chunk_index,
                    start_pos=current_start,
                    end_pos=current_start + len(current_chunk_text),
                    metadata={"strategy": "semantic"}
                ))
                chunk_index += 1
                
                # Calculate overlap for next chunk
                if config.chunk_overlap > 0 and len(current_chunk_text) > config.chunk_overlap:
                    overlap_text = current_chunk_text[-config.chunk_overlap:]
                    current_start += len(current_chunk_text) - len(overlap_text)
                    current_chunk_text = overlap_text
                else:
                    current_start += len(current_chunk_text)
                    current_chunk_text = ""
            
            # Handle large paragraph
            if paragraph_len > config.chunk_size:
                # Split at sentence boundaries
                sentences = chunk_by_sentences(paragraph)
                temp_chunk = ""
                
                for sentence in sentences:
                    if len(temp_chunk) + len(sentence) + 1 <= config.chunk_size:
                        if temp_chunk:
                            temp_chunk += " "
                        temp_chunk += sentence
                    else:
                        # Save sentence chunk
                        if len(temp_chunk) >= config.min_chunk_size:
                            chunks.append(Chunk(
                                text=temp_chunk.strip(),
                                index=chunk_index,
                                start_pos=current_start,
                                end_pos=current_start + len(temp_chunk),
                                metadata={"strategy": "sentence"}
                            ))
                            chunk_index += 1
                        
                        current_start += len(temp_chunk) if temp_chunk else 0
                        temp_chunk = sentence
                
                # Don't forget the last chunk
                if temp_chunk and len(temp_chunk) >= config.min_chunk_size:
                    current_chunk_text = temp_chunk
            else:
                current_chunk_text = paragraph
    
    # Save final chunk
    if current_chunk_text and len(current_chunk_text) >= config.min_chunk_size:
        chunks.append(Chunk(
            text=current_chunk_text.strip(),
            index=chunk_index,
            start_pos=current_start,
            end_pos=current_start + len(current_chunk_text),
            metadata={"strategy": "semantic"}
        ))
    
    return chunks


def fixed_size_chunking(text: str, config: ChunkingConfig) -> List[Chunk]:
    """
    Chunk text into fixed-size chunks with overlap.
    
    Args:
        text: Input text
        config: Chunking configuration
        
    Returns:
        List of chunks
    """
    chunks = []
    start = 0
    chunk_index = 0
    
    while start < len(text):
        end = min(start + config.chunk_size, len(text))
        
        # Try to break at word boundary
        if end < len(text) and config.respect_sentences:
            # Look for sentence ending
            while end > start and text[end-1] not in '.!?\n':
                end -= 1
            
            # If no sentence boundary found, try word boundary
            if end == start:
                end = min(start + config.chunk_size, len(text))
                while end > start and text[end-1].isalnum():
                    end -= 1
        
        chunk_text = text[start:end].strip()
        
        if len(chunk_text) >= config.min_chunk_size:
            chunks.append(Chunk(
                text=chunk_text,
                index=chunk_index,
                start_pos=start,
                end_pos=end,
                metadata={"strategy": "fixed"}
            ))
            chunk_index += 1
        
        # Move start with overlap
        start = end - config.chunk_overlap if end < len(text) else end
        
        # Prevent infinite loop
        if start >= end:
            break
    
    return chunks


def chunk_document(text: str, config: ChunkingConfig = None) -> List[Chunk]:
    """
    Chunk document text using configured strategy.
    
    Args:
        text: Document text
        config: Chunking configuration (default: semantic)
        
    Returns:
        List of chunks
        
    Raises:
        ChunkingError: If chunking fails
    """
    if not text:
        return []
    
    if config is None:
        config = ChunkingConfig()
    
    try:
        if config.strategy == "semantic":
            return semantic_chunking(text, config)
        elif config.strategy == "fixed":
            return fixed_size_chunking(text, config)
        else:
            raise ChunkingError(f"Unknown chunking strategy: {config.strategy}")
    except Exception as e:
        raise ChunkingError(f"Failed to chunk document: {str(e)}")