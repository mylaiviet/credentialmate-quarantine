"""
Discrepancy Taxonomy for Field Extraction Errors

Classifies field extraction errors into structured categories to enable
systematic root cause analysis and targeted improvements.

Error Categories:
- FORMAT_MISMATCH: AI returned wrong format (e.g., date format)
- MISSING_DATA: Field not present on document (null when should extract)
- OCR_FAILURE: Text not readable by OCR
- INFERENCE_ERROR: AI guessed wrong interpretation
- SCHEMA_MISMATCH: Field name confusion or incorrect mapping
- PUNCTUATION_VARIANCE: Minor differences in punctuation/ordering
"""

from enum import Enum
from typing import Optional, Dict, Any
import re


class ErrorType(Enum):
    """Classification of field extraction errors"""
    FORMAT_MISMATCH = "format_mismatch"
    MISSING_DATA = "missing_data"
    OCR_FAILURE = "ocr_failure"
    INFERENCE_ERROR = "inference_error"
    SCHEMA_MISMATCH = "schema_mismatch"
    PUNCTUATION_VARIANCE = "punctuation_variance"
    NUMERIC_TYPO = "numeric_typo"
    PARTIAL_EXTRACTION = "partial_extraction"


class DiscrepancyClassifier:
    """Classifies field extraction discrepancies by error type"""

    @staticmethod
    def classify_error(
        field_name: str,
        ai_value: Any,
        ground_truth_value: Any,
        field_category: str,
        document_type: str
    ) -> tuple[ErrorType, str]:
        """
        Classify an extraction error and provide reasoning.

        Args:
            field_name: Name of the field
            ai_value: Value extracted by AI
            ground_truth_value: Expected ground truth value
            field_category: Category of field (provider_info, credential_details)
            document_type: Type of document (cme, dea, etc.)

        Returns:
            Tuple of (ErrorType, reason_string)
        """
        # Convert to strings for comparison
        ai_str = str(ai_value) if ai_value is not None else "null"
        gt_str = str(ground_truth_value) if ground_truth_value is not None else "null"

        # Rule 1: Missing data (AI returned null when it shouldn't)
        if ai_value is None and ground_truth_value is not None:
            return ErrorType.MISSING_DATA, f"AI failed to extract {field_name}, returned null"

        # Rule 2: Schema mismatch (AI extracted something when field doesn't exist)
        if ai_value is not None and ground_truth_value is None:
            return ErrorType.SCHEMA_MISMATCH, f"AI extracted {field_name} but field doesn't exist in document"

        # Rule 3: Date format mismatch
        if field_name in ['date_range', 'completion_date', 'issue_date', 'expiration_date']:
            if DiscrepancyClassifier._is_date_format_mismatch(ai_str, gt_str):
                return ErrorType.FORMAT_MISMATCH, f"Date format differs: AI='{ai_str}' vs GT='{gt_str}'"

        # Rule 4: Punctuation/ordering variance (content same, format different)
        if DiscrepancyClassifier._is_punctuation_variance(ai_str, gt_str):
            return ErrorType.PUNCTUATION_VARIANCE, f"Word order or punctuation differs: AI='{ai_str}' vs GT='{gt_str}'"

        # Rule 5: Numeric typo (single digit error)
        if field_name in ['certificate_number', 'credential_number']:
            if DiscrepancyClassifier._is_numeric_typo(ai_str, gt_str):
                return ErrorType.NUMERIC_TYPO, f"Numeric OCR error: AI='{ai_str}' vs GT='{gt_str}'"

        # Rule 6: Partial extraction (AI got part of the value)
        if DiscrepancyClassifier._is_partial_extraction(ai_str, gt_str):
            return ErrorType.PARTIAL_EXTRACTION, f"AI extracted partial value: AI='{ai_str}' vs GT='{gt_str}'"

        # Rule 7: Inference error (completely different values)
        return ErrorType.INFERENCE_ERROR, f"AI inference incorrect: AI='{ai_str}' vs GT='{gt_str}'"

    @staticmethod
    def _is_date_format_mismatch(ai: str, gt: str) -> bool:
        """Check if values represent same date in different formats"""
        # Extract all date-like patterns
        ai_dates = re.findall(r'\d{4}|\d{1,2}/\d{1,2}/\d{2,4}|\d{1,2}-\d{1,2}-\d{2,4}', ai)
        gt_dates = re.findall(r'\d{4}|\d{1,2}/\d{1,2}/\d{2,4}|\d{1,2}-\d{1,2}-\d{2,4}', gt)

        # If both contain dates but formats differ
        return len(ai_dates) > 0 and len(gt_dates) > 0

    @staticmethod
    def _is_punctuation_variance(ai: str, gt: str) -> bool:
        """Check if values differ only in punctuation/word order"""
        # Normalize: lowercase, remove punctuation, sort words
        normalize = lambda s: sorted(re.sub(r'[^\w\s]', '', s.lower()).split())

        ai_norm = normalize(ai)
        gt_norm = normalize(gt)

        # Same words, different order/punctuation
        return ai_norm == gt_norm and ai != gt

    @staticmethod
    def _is_numeric_typo(ai: str, gt: str) -> bool:
        """Check if numeric values differ by 1-2 digits (OCR error)"""
        # Extract digits only
        ai_digits = re.sub(r'\D', '', ai)
        gt_digits = re.sub(r'\D', '', gt)

        if len(ai_digits) != len(gt_digits):
            return False

        # Count differing digits
        diff_count = sum(1 for a, g in zip(ai_digits, gt_digits) if a != g)

        return 1 <= diff_count <= 2

    @staticmethod
    def _is_partial_extraction(ai: str, gt: str) -> bool:
        """Check if AI value is substring or partial match of ground truth"""
        ai_clean = ai.lower().strip()
        gt_clean = gt.lower().strip()

        # AI is substring of GT, or shares significant overlap
        if ai_clean in gt_clean or gt_clean in ai_clean:
            return True

        # Check word overlap (at least 50% overlap)
        ai_words = set(re.sub(r'[^\w\s]', '', ai_clean).split())
        gt_words = set(re.sub(r'[^\w\s]', '', gt_clean).split())

        if len(ai_words) == 0 or len(gt_words) == 0:
            return False

        overlap = len(ai_words & gt_words) / max(len(ai_words), len(gt_words))

        return overlap >= 0.5


def classify_all_errors(db_session) -> Dict[str, Dict[str, int]]:
    """
    Classify all errors in field_accuracy_logs table.

    Returns:
        Dictionary with error type counts by field name
    """
    from app.models.field_accuracy_log import FieldAccuracyLog

    # Query all incorrect extractions
    incorrect_logs = db_session.query(FieldAccuracyLog).filter(
        FieldAccuracyLog.is_correct == False
    ).all()

    # Classify each error
    error_counts = {}

    for log in incorrect_logs:
        field_name = log.field_name

        if field_name not in error_counts:
            error_counts[field_name] = {}

        error_type, reason = DiscrepancyClassifier.classify_error(
            field_name=log.field_name,
            ai_value=log.ai_value,
            ground_truth_value=log.ground_truth_value,
            field_category=log.field_category,
            document_type=log.document_type
        )

        error_type_str = error_type.value

        if error_type_str not in error_counts[field_name]:
            error_counts[field_name][error_type_str] = 0

        error_counts[field_name][error_type_str] += 1

    return error_counts


if __name__ == "__main__":
    # Test the classifier with sample data
    test_cases = [
        # Missing data
        ("title", None, "UpToDate", "credential_details", "cme"),
        # Date format mismatch
        ("date_range", "2024-05-29 to 2024-05-29", "May 29, 2024 - May 29, 2024", "credential_details", "cme"),
        # Punctuation variance
        ("issuing_authority", "Quality Interactions and Amedco LLC", "Amedco LLC and Quality Interactions", "credential_details", "cme"),
        # Numeric typo
        ("certificate_number", "11017658082", "11017655802", "credential_details", "cme"),
        # Partial extraction
        ("title", "Implicit Bias Training", "Recognizing & Responding to Implicit Bias (CME/CEU/CCM/CDE)", "credential_details", "cme"),
    ]

    print("Discrepancy Taxonomy Test Results\n" + "="*60)

    for field_name, ai_value, gt_value, field_cat, doc_type in test_cases:
        error_type, reason = DiscrepancyClassifier.classify_error(
            field_name, ai_value, gt_value, field_cat, doc_type
        )

        print(f"\nField: {field_name}")
        print(f"AI Value: {ai_value}")
        print(f"Ground Truth: {gt_value}")
        print(f"Classification: {error_type.value}")
        print(f"Reason: {reason}")
        print("-" * 60)