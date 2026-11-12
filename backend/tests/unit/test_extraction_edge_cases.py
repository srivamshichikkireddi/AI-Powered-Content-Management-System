"""Edge-case and error-path tests for the text extractor (AICMS-F-005, F-006, TC-EXT-01/02)."""
import docx
import pypdf
import pytest

from backend.app.core.errors import AICMSException
from backend.app.services.extractor import extract_document_content


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------
def test_missing_file_raises_file_not_found(tmp_path):
    """A path that does not exist must raise a structured 404, not a raw OSError."""
    with pytest.raises(AICMSException) as exc_info:
        extract_document_content(str(tmp_path / "does_not_exist.txt"), "txt")
    assert exc_info.value.code == "FILE_NOT_FOUND"
    assert exc_info.value.status_code == 404


def test_unsupported_format_raises_400(tmp_path):
    """Formats outside txt/docx/pdf are rejected with UNSUPPORTED_FORMAT."""
    path = tmp_path / "data.xyz"
    path.write_text("content")
    with pytest.raises(AICMSException) as exc_info:
        extract_document_content(str(path), "xyz")
    assert exc_info.value.code == "UNSUPPORTED_FORMAT"
    assert exc_info.value.status_code == 400


def test_corrupt_docx_raises_extraction_error(tmp_path):
    """Garbage bytes with a .docx type surface as EXTRACTION_ERROR (500)."""
    path = tmp_path / "corrupt.docx"
    path.write_bytes(b"this is not a real docx archive")
    with pytest.raises(AICMSException) as exc_info:
        extract_document_content(str(path), "docx")
    assert exc_info.value.code == "EXTRACTION_ERROR"
    assert exc_info.value.status_code == 500


def test_corrupt_pdf_raises_extraction_error(tmp_path):
    """Garbage bytes with a .pdf type surface as EXTRACTION_ERROR (500)."""
    path = tmp_path / "corrupt.pdf"
    path.write_bytes(b"not a pdf at all")
    with pytest.raises(AICMSException) as exc_info:
        extract_document_content(str(path), "pdf")
    assert exc_info.value.code == "EXTRACTION_ERROR"
