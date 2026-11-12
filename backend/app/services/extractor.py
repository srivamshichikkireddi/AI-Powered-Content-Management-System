"""Text and native-metadata extraction for uploaded documents (US-03).

Supported formats: TXT, DOCX and PDF (AICMS-F-005, AICMS-F-006). Scanned PDFs with
no text layer are flagged with ``needs_ocr`` instead of being OCR'd here (AICMS-F-007,
see docs/ASSUMPTIONS.md). Failures are raised as ``AICMSException`` with a stable code.
"""
from dataclasses import dataclass
import os
from typing import Optional
import docx
import pypdf

from backend.app.core.config import settings
from backend.app.core.errors import AICMSException


@dataclass
class ExtractedContent:
    """Result of extracting one document.

    Attributes:
        text: Full extracted text, stripped of leading/trailing whitespace.
        title: Native title metadata, or None if the file has none (never guessed).
        author: Native author metadata, or None if the file has none (never guessed).
        date: Native creation date as a string, or None if the file has none.
        needs_ocr: True when a PDF yielded no text and needs OCR review.
        word_count: Number of whitespace-separated words in ``text``.
        character_count: Number of characters in ``text``.
    """
    text: str
    title: Optional[str] = None
    author: Optional[str] = None
    date: Optional[str] = None
    needs_ocr: bool = False
    word_count: int = 0
    character_count: int = 0


def extract_document_content(file_path: str, file_type: str) -> ExtractedContent:
    """
    Extract full text and native metadata across supported formats (AICMS-F-005, F-006, TC-EXT-01/02).
    Missing native metadata remains None (no fabrication per Rule 1).
    Honors SIMULATE_PARSER_FAILURE test flag.
    """
    if settings.SIMULATE_PARSER_FAILURE == 1:
        raise AICMSException(
            code="PARSER_FAILURE",
            message="Simulated parser failure during document extraction pipeline.",
            status_code=500,
        )

    if not os.path.exists(file_path):
        raise AICMSException(code="FILE_NOT_FOUND", message="Storage file not found on disk.", status_code=404)

    # File type is matched case-insensitively ("PDF" and "pdf" are the same format).
    ext = file_type.lower()
    text = ""
    title = None
    author = None
    date = None
    needs_ocr = False

    try:
        if ext == "txt":
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                text = f.read().strip()

        elif ext == "docx":
            doc = docx.Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]

            # Table cells are not in doc.paragraphs, so read them separately.
            # Each row becomes one line, with non-empty cells joined by " | ".
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                    if row_text:
                        paragraphs.append(row_text)

            text = "\n\n".join(paragraphs).strip()

            # Native metadata: blank values stay None rather than being invented (TC-EXT-02).
            if doc.core_properties:
                props = doc.core_properties
                if props.title and props.title.strip():
                    title = props.title.strip()
                if props.author and props.author.strip():
                    author = props.author.strip()
                if props.created:
                    date = props.created.isoformat()

        elif ext == "pdf":
            reader = pypdf.PdfReader(file_path)
            pages_text = []
            for page in reader.pages:
                page_content = page.extract_text()
                if page_content:
                    pages_text.append(page_content.strip())

            text = "\n\n".join(pages_text).strip()

            # Native metadata dictionary
            if reader.metadata:
                meta = reader.metadata
                raw_title = getattr(meta, "title", None) or meta.get("/Title")
                if raw_title and str(raw_title).strip():
                    title = str(raw_title).strip()

                raw_author = getattr(meta, "author", None) or meta.get("/Author")
                if raw_author and str(raw_author).strip():
                    author = str(raw_author).strip()

                raw_date = getattr(meta, "creation_date", None) or meta.get("/CreationDate")
                if raw_date:
                    date = str(raw_date)

            # No text layer means a scanned/image-only PDF: flag it for OCR review
            # instead of failing (AICMS-F-007).
            if len(text) == 0:
                needs_ocr = True

        else:
            raise AICMSException(
                code="UNSUPPORTED_FORMAT",
                message=f"Unsupported format '{ext}' for extraction.",
                status_code=400,
            )

    # Our own structured errors (e.g. UNSUPPORTED_FORMAT) pass through unchanged;
    # any other parser exception is wrapped as EXTRACTION_ERROR below.
    except AICMSException:
        raise
    except Exception as e:
        raise AICMSException(
            code="EXTRACTION_ERROR",
            message=f"Failed to parse document content: {str(e)}",
            status_code=500,
        )

    # Counts are computed on the final stripped text.
    words = text.split() if text else []
    return ExtractedContent(
        text=text,
        title=title,
        author=author,
        date=date,
        needs_ocr=needs_ocr,
        word_count=len(words),
        character_count=len(text),
    )
