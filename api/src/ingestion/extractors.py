"""Document text extraction utilities."""

import io
from pathlib import Path


class TextExtractionError(Exception):
    """Error extracting text from document."""
    pass


class UnsupportedFormatError(TextExtractionError):
    """Unsupported document format."""
    pass


def extract_text_from_pdf(file_content: bytes) -> str:
    """
    Extract text from PDF using PyMuPDF.

    Args:
        file_content: PDF file bytes

    Returns:
        Extracted text

    Raises:
        TextExtractionError: If extraction fails
    """
    try:
        import fitz  # PyMuPDF

        # Open PDF from bytes
        pdf_document = fitz.open(stream=file_content, filetype="pdf")

        text_parts = []
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text_parts.append(page.get_text())

        pdf_document.close()

        return "\n".join(text_parts)

    except Exception as e:
        raise TextExtractionError(f"Failed to extract PDF text: {str(e)}")


def extract_text_from_docx(file_content: bytes) -> str:
    """
    Extract text from DOCX file.

    Args:
        file_content: DOCX file bytes

    Returns:
        Extracted text
    """
    try:
        from docx import Document

        # Load from bytes
        doc = Document(io.BytesIO(file_content))

        text_parts = []
        for paragraph in doc.paragraphs:
            text_parts.append(paragraph.text)

        return "\n".join(text_parts)

    except Exception as e:
        raise TextExtractionError(f"Failed to extract DOCX text: {str(e)}")


def extract_text_from_txt(file_content: bytes) -> str:
    """
    Extract text from TXT file.

    Args:
        file_content: TXT file bytes

    Returns:
        Extracted text (UTF-8 decoded)
    """
    try:
        # Try UTF-8 first
        return file_content.decode('utf-8')
    except UnicodeDecodeError:
        # Fallback to latin-1
        try:
            return file_content.decode('latin-1')
        except Exception as e:
            raise TextExtractionError(f"Failed to decode text file: {str(e)}")


def extract_text(file_content: bytes, filename: str) -> str:
    """
    Extract text from document based on file extension.

    Args:
        file_content: File bytes
        filename: Original filename (for extension detection)

    Returns:
        Extracted text

    Raises:
        UnsupportedFormatError: If file format not supported
        TextExtractionError: If extraction fails
    """
    extension = Path(filename).suffix.lower()

    extractors = {
        '.pdf': extract_text_from_pdf,
        '.docx': extract_text_from_docx,
        '.txt': extract_text_from_txt,
        '.md': extract_text_from_txt,
        '.text': extract_text_from_txt,
    }

    extractor = extractors.get(extension)

    if not extractor:
        supported = ", ".join(extractors.keys())
        raise UnsupportedFormatError(
            f"Unsupported file format: '{extension}'. "
            f"Supported extensions: {supported}"
        )

    try:
        return extractor(file_content)
    except TextExtractionError:
        raise
    except Exception as e:
        raise TextExtractionError(f"Extraction failed for {extension}: {str(e)}")


def detect_file_type(filename: str) -> str:
    """
    Detect MIME type from filename.

    Args:
        filename: File name

    Returns:
        MIME type string
    """
    extension = Path(filename).suffix.lower()

    mime_types = {
        '.pdf': 'application/pdf',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.txt': 'text/plain',
        '.md': 'text/markdown',
    }

    return mime_types.get(extension, 'application/octet-stream')
