#!/usr/bin/env python3
"""
Compare actual extraction vs ground truth for low-accuracy documents
Identifies where model is correct but ground truth says "null"
"""

import json
from pathlib import Path
from typing import Dict, Any
import sys
import io

# Import services
from app.services.document_type_detector import DocumentTypeDetector
from app.services.conversational_parser import ConversationalDocumentParser

def load_document(file_path: str) -> bytes:
    """Load document bytes"""
    doc_path = Path(__file__).parent.parent / file_path
    if not doc_path.exists():
        doc_path = Path(file_path)
    return doc_path.read_bytes()

try:
    import fitz  # PyMuPDF
    PDF_CONVERSION_AVAILABLE = True
except ImportError:
    PDF_CONVERSION_AVAILABLE = False

def convert_pdf_to_image(pdf_bytes: bytes, dpi: int = 150):
    """Convert first page of PDF to PNG image"""
    from PIL import Image
    pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = pdf_doc[0]
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat)
    img_data = pix.tobytes("png")
    pdf_doc.close()
    return img_data, "image/png"

def prepare_document_for_parsing(file_path: str, doc_bytes: bytes):
    """Convert document to image format"""
    ext = file_path.lower().split(".")[-1]
    if ext == "pdf":
        return convert_pdf_to_image(doc_bytes)
    elif ext in ["jpg", "jpeg"]:
        return doc_bytes, "image/jpeg"
    elif ext == "png":
        return doc_bytes, "image/png"
    return doc_bytes, "image/jpeg"

def analyze_document(data_id: str):
    """Analyze a single document"""
    print(f"\n{'='*80}")
    print(f"Analyzing {data_id}")
    print(f"{'='*80}\n")

    # Load ground truth
    gt_path = Path(__file__).parent / f"tests/fixtures/ground_truth/{data_id}_ground_truth.json"
    with open(gt_path, 'r') as f:
        gt_data = json.load(f)

    file_path = gt_data['file_path']
    expected = gt_data.get('expected_extraction', {})

    print(f"File: {file_path}")
    print()

    # Load and parse document
    try:
        doc_bytes = load_document(file_path)
        img_bytes, content_type = prepare_document_for_parsing(file_path, doc_bytes)

        parser = ConversationalDocumentParser(use_mock=False)
        result = parser.parse_document(img_bytes, content_type, "cme")

        print("EXTRACTION RESULTS:")
        print(json.dumps(result, indent=2))
        print()

        # Compare
        print("COMPARISON:")
        print(f"{'Field':<50} {'Ground Truth':<20} {'Extracted':<20} {'Match'}")
        print("-" * 120)

        def compare_fields(expected_dict, extracted_dict, prefix=""):
            for key, expected_val in expected_dict.items():
                current_key = f"{prefix}.{key}" if prefix else key
                if isinstance(expected_val, dict):
                    extracted_val = extracted_dict.get(key, {}) if isinstance(extracted_dict, dict) else {}
                    compare_fields(expected_val, extracted_val, current_key)
                else:
                    extracted_val = extracted_dict.get(key) if isinstance(extracted_dict, dict) else None

                    expected_str = str(expected_val)[:18] if expected_val is not None else "NULL"
                    extracted_str = str(extracted_val)[:18] if extracted_val is not None else "NULL"

                    if expected_val is None and extracted_val is not None:
                        match = "❌ GT=NULL, Model found data"
                    elif expected_val is not None and extracted_val is None:
                        match = "❌ GT has data, Model=NULL"
                    elif expected_val == extracted_val:
                        match = "✅ Match"
                    else:
                        match = "⚠️  Mismatch"

                    print(f"{current_key:<50} {expected_str:<20} {extracted_str:<20} {match}")

        compare_fields(expected, result)

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Test one document
    analyze_document("TD-012")
