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


# ---------------------------------------------------------------------------
# TXT edge cases
# ---------------------------------------------------------------------------
def test_empty_txt_returns_empty_content(tmp_path):
    """An empty TXT file yields empty text and zero counts without failing."""
    path = tmp_path / "empty.txt"
    path.write_text("")
    res = extract_document_content(str(path), "txt")
    assert res.text == ""
    assert res.word_count == 0
    assert res.character_count == 0
    assert res.needs_ocr is False


def test_txt_with_invalid_utf8_is_decoded_with_replacement(tmp_path):
    """Invalid UTF-8 bytes are replaced instead of crashing the pipeline."""
    path = tmp_path / "latin1.txt"
    path.write_bytes(b"caf\xe9 report")
    res = extract_document_content(str(path), "txt")
    assert "report" in res.text
    assert "\ufffd" in res.text


def test_txt_word_and_character_counts(tmp_path):
    """Counts reflect the stripped text."""
    path = tmp_path / "counts.txt"
    path.write_text("  one two  three\n")
    res = extract_document_content(str(path), "txt")
    assert res.text == "one two  three"
    assert res.word_count == 3
    assert res.character_count == len("one two  three")


def test_file_type_is_case_insensitive(tmp_path):
    """'TXT' and 'txt' are treated the same."""
    path = tmp_path / "upper.txt"
    path.write_text("hello world")
    assert extract_document_content(str(path), "TXT").text == "hello world"
