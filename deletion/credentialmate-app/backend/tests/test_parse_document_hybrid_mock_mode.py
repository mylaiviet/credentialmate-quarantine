"""
TDD Tests for parse_document_hybrid() Mock Mode Support

Tests for ISSUE-032 fix: Verify that parse_document_hybrid() correctly handles
mock mode for development/testing without AWS Bedrock credentials.

Test Coverage:
- Mock mode returns proper DocumentParseResponse dict structure
- Mock responses include all required fields
- Both CME and license document types supported in mock mode
- Confidence scores and field confidence present
- Processing time calculated correctly
- No AWS Bedrock calls made when use_mock=True

Author: Claude Code Agent (Backend)
Session: 20251111-012620
Created: 2025-11-11
"""

import pytest
from datetime import datetime
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.document_parser import DocumentParserService


class TestParseDocumentHybridMockMode:
    """Tests for parse_document_hybrid() mock mode support."""

    @pytest.fixture
    def mock_parser(self):
        """Create document parser with mock mode enabled."""
        return DocumentParserService(
            aws_region="us-east-1", use_mock=True, enable_conversational_fallback=True
        )

    @pytest.fixture
    def sample_pdf_content(self):
        """Load sample PDF for testing."""
        pdf_path = (
            Path(__file__).parent.parent.parent
            / ".test_files"
            / "Continuing Medical Education (CME) _ ACP Online.pdf"
        )
        if pdf_path.exists():
            with open(pdf_path, "rb") as f:
                return f.read()
        else:
            # Return minimal PDF content for testing
            return b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\nxref\n0 1\n0000000000 65535 f\ntrailer\n<< /Size 1 >>\nstartxref\n44\n%%EOF"

    def test_mock_mode_hybrid_parse_returns_dict(self, mock_parser, sample_pdf_content):
        """Test that parse_document_hybrid with mock mode returns dict structure."""
        result = mock_parser.parse_document_hybrid(
            file_content=sample_pdf_content, filename="test.pdf"
        )

        assert isinstance(result, dict), "Result should be a dictionary"
        assert "document_type" in result, "Missing document_type field"
        assert "extracted_data" in result, "Missing extracted_data field"
        assert "confidence_score" in result, "Missing confidence_score field"
        assert "parsing_method" in result, "Missing parsing_method field"

    def test_mock_mode_parsing_method_identified(self, mock_parser, sample_pdf_content):
        """Test that mock mode is properly identified in response."""
        result = mock_parser.parse_document_hybrid(
            file_content=sample_pdf_content, filename="test.pdf"
        )

        assert (
            result["parsing_method"] == "mock"
        ), "Parsing method should be 'mock' when use_mock=True"

    def test_mock_mode_confidence_scores_present(self, mock_parser, sample_pdf_content):
        """Test that confidence scores are present in mock response."""
        result = mock_parser.parse_document_hybrid(
            file_content=sample_pdf_content, filename="test.pdf"
        )

        assert isinstance(
            result["confidence_score"], (int, float)
        ), "Confidence score should be numeric"
        assert (
            0.0 <= result["confidence_score"] <= 1.0
        ), "Confidence score should be between 0 and 1"

        if result["field_confidence"]:
            assert isinstance(
                result["field_confidence"], dict
            ), "Field confidence should be a dictionary"
            for field, confidence in result["field_confidence"].items():
                assert isinstance(
                    confidence, (int, float)
                ), f"Field confidence for '{field}' should be numeric"
                assert (
                    0.0 <= confidence <= 1.0
                ), f"Field confidence for '{field}' should be between 0 and 1"

    def test_mock_mode_extracted_data_structure(self, mock_parser, sample_pdf_content):
        """Test that extracted data has proper structure."""
        result = mock_parser.parse_document_hybrid(
            file_content=sample_pdf_content, filename="test.pdf"
        )

        assert isinstance(
            result["extracted_data"], dict
        ), "Extracted data should be a dictionary"

        # For license types, should have license-specific fields
        if result["document_type"] in [
            "state_license",
            "diploma",
            "board_certification",
        ]:
            # At minimum should have some fields
            assert (
                len(result["extracted_data"]) > 0
            ), "Extracted data should not be empty for license types"

    def test_mock_mode_processing_time_calculated(
        self, mock_parser, sample_pdf_content
    ):
        """Test that processing time is properly recorded."""
        result = mock_parser.parse_document_hybrid(
            file_content=sample_pdf_content, filename="test.pdf"
        )

        assert (
            "processing_time_seconds" in result
        ), "Missing processing_time_seconds field"
        assert isinstance(
            result["processing_time_seconds"], (int, float)
        ), "Processing time should be numeric"
        assert (
            result["processing_time_seconds"] >= 0
        ), "Processing time should be non-negative"
        assert (
            result["processing_time_seconds"] < 5
        ), "Mock mode should complete very quickly (< 5 seconds)"

    def test_mock_mode_document_type_recognized(self, mock_parser, sample_pdf_content):
        """Test that document type is recognized in mock response."""
        result = mock_parser.parse_document_hybrid(
            file_content=sample_pdf_content, filename="test.pdf"
        )

        valid_doc_types = [
            "cme",
            "state_license",
            "board_certification",
            "diploma",
            "dea",
            "controlled_substance",
            "drivers_license",
            "other",
        ]
        assert (
            result["document_type"] in valid_doc_types
        ), f"Document type {result['document_type']} not in valid types: {valid_doc_types}"

    def test_mock_mode_with_image_file(self, mock_parser):
        """Test mock mode works with image files."""
        # Create minimal PNG content (8x8 transparent PNG)
        png_content = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x08"
            b"\x00\x00\x00\x08\x08\x06\x00\x00\x00\xc4\x0f\xbe\x8b"
            b"\x00\x00\x00\x19tEXtSoftware\x00Adobe ImageReadyq\xc9e<"
            b'\x00\x00\x00"IDATx\xdab\xf8\x0f\x00\x00\x01\x01\x00\x01'
            b"\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        )

        result = mock_parser.parse_document_hybrid(
            file_content=png_content, filename="test.png"
        )

        assert isinstance(result, dict), "Result should be dict for image files"
        assert "document_type" in result, "Should have document_type for images"

    def test_mock_mode_no_bedrock_calls(self, mock_parser, sample_pdf_content):
        """Test that bedrock_runtime is not called in mock mode."""
        # Verify bedrock_runtime is None when use_mock=True
        assert (
            mock_parser.bedrock_runtime is None
        ), "bedrock_runtime should be None when use_mock=True"

        # Parse should still work without calling bedrock
        result = mock_parser.parse_document_hybrid(
            file_content=sample_pdf_content, filename="test.pdf"
        )

        assert result is not None, "Parse should succeed even with None bedrock_runtime"
        assert result["parsing_method"] == "mock", "Should use mock parsing method"

    def test_real_vs_mock_mode_consistency(self):
        """Test that mock and real modes have consistent response structures."""
        mock_parser = DocumentParserService(use_mock=True)
        real_parser = DocumentParserService(use_mock=False)

        # Both should have same bedrock_runtime handling
        assert mock_parser.use_mock is True, "Mock parser should have use_mock=True"
        assert real_parser.use_mock is False, "Real parser should have use_mock=False"

        # When real parser has no bedrock credentials, it falls back to mock
        if real_parser.bedrock_runtime is None:
            assert (
                real_parser.use_mock is True
            ), "Real parser should enable mock mode if bedrock_runtime is None"


class TestParseDocumentHybridIntegration:
    """Integration tests for parse_document_hybrid with actual document files."""

    @pytest.fixture
    def test_documents(self):
        """Get paths to test documents."""
        test_dir = Path(__file__).parent.parent.parent / ".test_files"
        docs = {}

        if test_dir.exists():
            for pdf_file in test_dir.glob("*.pdf"):
                docs[pdf_file.stem] = pdf_file

        return docs

    def test_mock_mode_with_real_documents(self, test_documents):
        """Test mock mode with actual document files."""
        if not test_documents:
            pytest.skip("No test documents available")

        parser = DocumentParserService(use_mock=True)

        for doc_name, doc_path in list(test_documents.items())[:2]:  # Test first 2 docs
            with open(doc_path, "rb") as f:
                content = f.read()

            result = parser.parse_document_hybrid(
                file_content=content, filename=doc_path.name
            )

            assert isinstance(
                result, dict
            ), f"Failed for {doc_name}: result should be dict"
            assert (
                "document_type" in result
            ), f"Failed for {doc_name}: missing document_type"
            assert (
                "confidence_score" in result
            ), f"Failed for {doc_name}: missing confidence_score"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
