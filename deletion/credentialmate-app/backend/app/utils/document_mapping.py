"""
Document mapping utilities for batch upload.

Maps parsed AI data to database schemas for different credential types.

Author: Claude Code
Created: 2025-11-06
"""

from typing import Optional, Tuple, Dict, Any
from datetime import date
import logging

from app.schemas.license import LicenseCreate
from app.schemas.cme_activity import CMEActivityCreate
from app.schemas.document_upload import ParsedCMEData

logger = logging.getLogger(__name__)


class DocumentType:
    """Document type constants."""

    CME = "cme"
    LICENSE = "license"
    DEA = "dea"
    CONTROLLED_SUBSTANCE = "controlled_substance"
    BOARD_CERT = "board_certification"
    TRAINING = "training"
    OTHER = "other"


def identify_document_type(parsed_data: ParsedCMEData, filename: str) -> str:
    """
    Identify document type from parsed AI data and filename.

    Args:
        parsed_data: Parsed data from AI
        filename: Original filename

    Returns:
        Document type constant (CME, LICENSE, DEA, etc.)
    """
    filename_lower = filename.lower()
    reasoning = (
        parsed_data.metadata.get("reasoning", "").lower()
        if parsed_data.metadata
        else ""
    )

    # Check reasoning first (AI explicitly identified the document)
    if "license" in reasoning and "controlled substance" not in reasoning:
        return DocumentType.LICENSE
    if "dea" in reasoning or "controlled substance" in reasoning:
        if "state" in reasoning or "missouri" in reasoning:
            return DocumentType.CONTROLLED_SUBSTANCE
        return DocumentType.DEA
    if "board cert" in reasoning or "diplomate" in reasoning:
        return DocumentType.BOARD_CERT
    if (
        "fellowship" in reasoning
        or "residency" in reasoning
        or "medical school" in reasoning
    ):
        return DocumentType.TRAINING

    # Check filename
    if "dea" in filename_lower:
        return DocumentType.DEA
    if "license" in filename_lower:
        return DocumentType.LICENSE
    if "board" in filename_lower or "abim" in filename_lower:
        return DocumentType.BOARD_CERT
    if (
        "residency" in filename_lower
        or "fellowship" in filename_lower
        or "medical school" in filename_lower
    ):
        return DocumentType.TRAINING

    # Check data fields
    if parsed_data.credits and parsed_data.credits > 0:
        return DocumentType.CME

    # Check activity_type field
    if parsed_data.activity_type:
        activity_lower = parsed_data.activity_type.lower()
        if "practitioner" in activity_lower or "medical doctor" in activity_lower:
            return DocumentType.CONTROLLED_SUBSTANCE
        if (
            "fellowship" in activity_lower
            or "residency" in activity_lower
            or "doctor of medicine" in activity_lower
        ):
            return DocumentType.TRAINING

    # Default to OTHER if can't identify
    logger.warning(f"Could not identify document type for {filename}")
    return DocumentType.OTHER


def map_to_license_create(parsed_data: ParsedCMEData) -> Optional[LicenseCreate]:
    """
    Map parsed AI data to LicenseCreate schema.

    Args:
        parsed_data: Parsed data from AI

    Returns:
        LicenseCreate object or None if data is insufficient
    """
    # Extract state from parsed_data
    state = parsed_data.state

    # Extract license type from activity_type or metadata
    license_type = None
    if parsed_data.activity_type:
        # AI might put license type in activity_type field
        activity_lower = parsed_data.activity_type.lower()
        if "md" in activity_lower:
            license_type = "MD"
        elif "do" in activity_lower:
            license_type = "DO"
        elif "np" in activity_lower:
            license_type = "NP"
        elif "pa" in activity_lower:
            license_type = "PA"

    # Extract license number from certificate_number or metadata
    license_number = parsed_data.certificate_number

    # Extract dates
    issue_date = (
        parsed_data.completion_date
    )  # AI may use completion_date for issue_date
    expiration_date = (
        parsed_data.metadata.get("expiration_date") if parsed_data.metadata else None
    )

    # Validate required fields
    if not state or not license_number:
        logger.warning(
            f"Insufficient data for license: state={state}, license_number={license_number}"
        )
        return None

    # Default license_type to MD if not specified
    if not license_type:
        license_type = "MD"
        logger.info(f"Defaulting license_type to MD")

    return LicenseCreate(
        state=state,
        license_type=license_type,
        license_number=license_number,
        issue_date=issue_date,
        expiration_date=None,  # Will need to be parsed separately if available
        renewal_cycle_months=None,  # Optional
        is_verified=True,  # Mark as verified since AI extracted it
    )


def map_to_cme_create(parsed_data: ParsedCMEData) -> Optional[CMEActivityCreate]:
    """
    Map parsed AI data to CMEActivityCreate schema.

    Args:
        parsed_data: Parsed data from AI

    Returns:
        CMEActivityCreate object or None if data is insufficient
    """
    # Validate required fields for CME
    if not parsed_data.credits or parsed_data.credits <= 0:
        logger.warning(f"Insufficient CME data: credits={parsed_data.credits}")
        return None

    # Extract completion date
    completion_date = parsed_data.completion_date
    if not completion_date:
        logger.warning("CME activity missing completion_date")
        return None

    # Validate required fields exist
    if not parsed_data.title:
        logger.warning("CME activity missing title")
        return None
    if not parsed_data.provider:
        logger.warning("CME activity missing provider")
        return None

    # Build CME activity
    return CMEActivityCreate(
        title=parsed_data.title,
        credits=parsed_data.credits,
        completion_date=completion_date,
        activity_type=parsed_data.activity_type or "Other",
        category=parsed_data.category
        or "General",  # Default to General if not specified
        provider=parsed_data.provider,
        state=parsed_data.state,
        certificate_url=None,  # Will be added later if document is stored in S3
        notes=None,
        metadata=parsed_data.metadata,
    )


def store_in_user_metadata(
    user_metadata: Optional[Dict[str, Any]],
    parsed_data: ParsedCMEData,
    doc_type: str,
    filename: str,
) -> Dict[str, Any]:
    """
    Store unsupported document type in user metadata.

    Args:
        user_metadata: Existing user metadata dict (or None)
        parsed_data: Parsed data from AI
        doc_type: Document type
        filename: Original filename

    Returns:
        Updated user metadata dict
    """
    if user_metadata is None:
        user_metadata = {}

    # Initialize credentials array if not exists
    if "credentials" not in user_metadata:
        user_metadata["credentials"] = []

    # Build credential entry
    credential_entry = {
        "type": doc_type,
        "filename": filename,
        "provider": parsed_data.provider,
        "certificate_number": parsed_data.certificate_number,
        "completion_date": str(parsed_data.completion_date)
        if parsed_data.completion_date
        else None,
        "state": parsed_data.state,
        "activity_type": parsed_data.activity_type,
        "category": parsed_data.category,
        "title": parsed_data.title,
        "metadata": parsed_data.metadata,
    }

    # Add to credentials array
    user_metadata["credentials"].append(credential_entry)

    logger.info(f"Stored {doc_type} in user metadata: {filename}")

    return user_metadata
