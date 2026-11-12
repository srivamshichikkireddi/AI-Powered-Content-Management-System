"""Edge-case and error-path tests for the text extractor (AICMS-F-005, F-006, TC-EXT-01/02)."""
import datetime

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


# ---------------------------------------------------------------------------
# DOCX / PDF metadata edge cases (no fabrication of missing metadata)
# ---------------------------------------------------------------------------
def test_docx_blank_metadata_stays_none(tmp_path):
    """Whitespace-only title/author must not be reported as metadata."""
    document = docx.Document()
    document.core_properties.title = "   "
    document.core_properties.author = ""
    document.add_paragraph("Body text only.")
    path = tmp_path / "blank_meta.docx"
    document.save(str(path))

    res = extract_document_content(str(path), "docx")
    assert "Body text only." in res.text
    assert res.title is None
    assert res.author is None


def test_docx_skips_empty_paragraphs_and_joins_table_cells(tmp_path):
    """Empty paragraphs are dropped; table rows are joined with ' | '."""
    document = docx.Document()
    document.add_paragraph("First")
    document.add_paragraph("   ")
    document.add_paragraph("Second")
    table = document.add_table(rows=1, cols=3)
    for cell, value in zip(table.rows[0].cells, ["A", "", "C"]):
        cell.text = value
    path = tmp_path / "structure.docx"
    document.save(str(path))

    res = extract_document_content(str(path), "docx")
    assert res.text.split("\n\n") == ["First", "Second", "A | C"]


def test_pdf_without_metadata_leaves_fields_none(tmp_path):
    """A PDF with no title/author reports None and flags OCR when blank."""
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=72, height=72)
    path = tmp_path / "no_meta.pdf"
    with open(path, "wb") as fh:
        writer.write(fh)

    res = extract_document_content(str(path), "pdf")
    assert res.title is None
    assert res.author is None
    assert res.needs_ocr is True
    assert res.word_count == 0


# ---------------------------------------------------------------------------
# PDF with a real text layer (no OCR needed)
# ---------------------------------------------------------------------------

def _text_pdf(path, text):
    """Write a minimal one-page PDF that contains extractable text."""
    objs = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 100] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        None,
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    stream = f"BT /F1 12 Tf 10 50 Td ({text}) Tj ET".encode()
    objs[3] = b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream"
    out, offsets = b"%PDF-1.4\n", []
    for i, o in enumerate(objs, 1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % i + o + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)
    for off in offsets:
        out += b"%010d 00000 n \n" % off
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF" % (len(objs) + 1, xref)
    path.write_bytes(out)


def test_pdf_with_text_is_extracted_and_not_flagged_for_ocr(tmp_path):
    path = tmp_path / "text.pdf"
    _text_pdf(path, "Quarterly security audit")
    res = extract_document_content(str(path), "pdf")
    assert "Quarterly security audit" in res.text
    assert res.needs_ocr is False
    assert res.word_count == 3


# ---------------------------------------------------------------------------
# Native creation-date metadata
# ---------------------------------------------------------------------------
def test_pdf_creation_date_is_reported(tmp_path):
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.add_metadata({"/CreationDate": "D:20260101120000Z"})
    path = tmp_path / "dated.pdf"
    with open(path, "wb") as fh:
        writer.write(fh)
    assert extract_document_content(str(path), "pdf").date is not None


def test_docx_creation_date_is_iso_formatted(tmp_path):
    document = docx.Document()
    document.core_properties.created = datetime.datetime(2026, 1, 2, 3, 4, 5)
    document.add_paragraph("dated")
    path = tmp_path / "dated.docx"
    document.save(str(path))
    assert extract_document_content(str(path), "docx").date.startswith("2026-01-02T03:04:05")
