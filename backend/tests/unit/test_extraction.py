import io
import os
import tempfile
import docx
import pypdf
import pytest

from backend.app.core.config import settings
from backend.app.core.errors import AICMSException
from backend.app.services.extractor import extract_document_content


def test_txt_extraction_tc_ext_01():
    """TC-EXT-01: Extract text from TXT file."""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w", encoding="utf-8") as f:
        f.write("Artificial Intelligence in Content Management Systems\nKey concepts and architectures.")
        temp_path = f.name

    try:
        res = extract_document_content(temp_path, "txt")
        assert "Artificial Intelligence in Content Management Systems" in res.text
        assert res.word_count > 5
        assert res.title is None  # Plain text has no native metadata header (TC-EXT-02)
        assert res.author is None
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_docx_extraction_and_metadata_tc_ext_01_02():
    """TC-EXT-01 & TC-EXT-02: Extract text and native metadata from DOCX file."""
    doc = docx.Document()
    doc.core_properties.title = "Software Architecture Document"
    doc.core_properties.author = "Engineering Team"
    doc.add_heading("1. Introduction", level=1)
    doc.add_paragraph("This document specifies the system architecture and component interactions.")
    
    table = doc.add_table(rows=1, cols=2)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Component"
    hdr_cells[1].text = "Technology"

    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        temp_path = f.name
    doc.save(temp_path)

    try:
        res = extract_document_content(temp_path, "docx")
        assert "1. Introduction" in res.text
        assert "system architecture" in res.text
        assert "Component | Technology" in res.text
        # Metadata checks (TC-EXT-02)
        assert res.title == "Software Architecture Document"
        assert res.author == "Engineering Team"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_pdf_extraction_and_metadata_tc_ext_01_02():
    """TC-EXT-01 & TC-EXT-02: Extract text and metadata from PDF."""
    writer = pypdf.PdfWriter()
    writer.add_metadata({
        "/Title": "Financial Quarterly Report",
        "/Author": "Finance Dept",
    })
    page = writer.add_blank_page(width=72, height=72)
    # Note: pypdf blank page has no text, so test blank pdf OCR flag
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        temp_path = f.name
    with open(temp_path, "wb") as f:
        writer.write(f)

    try:
        res = extract_document_content(temp_path, "pdf")
        assert res.title == "Financial Quarterly Report"
        assert res.author == "Finance Dept"
        assert res.needs_ocr is True  # Blank / scanned page triggers OCR fallback (AICMS-F-007)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_simulate_parser_failure_flag():
    """Verify SIMULATE_PARSER_FAILURE=1 flag raises structured error."""
    settings.SIMULATE_PARSER_FAILURE = 1
    try:
        with pytest.raises(AICMSException) as exc_info:
            extract_document_content("dummy.txt", "txt")
        assert exc_info.value.code == "PARSER_FAILURE"
    finally:
        settings.SIMULATE_PARSER_FAILURE = 0
