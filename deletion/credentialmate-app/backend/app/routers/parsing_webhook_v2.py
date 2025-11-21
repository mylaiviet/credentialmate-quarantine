# TIMESTAMP: 2025-11-16T00:00:00Z
# ORIGIN: credentialmate-app/backend
# UPDATED_FOR: soc2-deployment-hardening
# CONTRACT_VERSION: v2.0

"""
Parsing webhook router for external parsing pipeline integration.

Endpoint:
- POST /api/v1/parsing/webhook

Purpose:
- Accept status updates from external parsing services
- Validate webhook signatures (HMAC-SHA256)
- Prevent replay attacks (timestamp + request ID validation)
- Update parsing job status in database

SOC2 Compliance:
- CC6.1 - Logical access controls (signature validation)
- CC9.3 - Contingency planning (replay prevention)
"""

from fastapi import APIRouter, Depends, status, HTTPException, Request, Header
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import logging

from app.core.dependencies import get_db
from app.core.config import settings
from app.services.webhook_security import (
    get_webhook_security_service,
    WebhookSignatureError,
    WebhookReplayError,
)

logger = logging.getLogger(__name__)

# Import models from credentialmate-schemas
import sys

sys.path.append("../../../credentialmate-schemas")
from app.models import ParsingJob

router = APIRouter(prefix="/api/v1/parsing", tags=["parsing"])


class ParsingWebhookPayload(BaseModel):
    """
    Webhook payload from parsing pipeline.

    NOTE: This is a STUB schema. Actual payload structure
    will be defined when parsing pipeline is implemented.
    """

    parsing_job_id: int
    status: str  # pending, in_progress, completed, failed
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def parsing_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_signature: str = Header(None),
    x_timestamp: str = Header(None),
    x_request_id: str = Header(None),
):
    """
    Webhook endpoint for parsing pipeline status updates.

    Security:
    - Requires HMAC-SHA256 signature validation (X-Signature header)
    - Validates timestamp (X-Timestamp header) to prevent stale requests
    - Tracks request IDs (X-Request-Id header) to prevent replay attacks

    Headers Required:
    - X-Signature: sha256=<HMAC_SHA256(secret, body)>
    - X-Timestamp: Unix timestamp (must be within ±5 minutes)
    - X-Request-Id: UUID (must be unique)

    Body:
    - parsing_job_id: int
    - status: str (pending, in_progress, completed, failed)
    - error_message: str (optional, if status=failed)
    - metadata: dict (optional)

    Args:
        request: HTTP request (for body)
        db: Database session
        x_signature: HMAC-SHA256 signature header
        x_timestamp: Request timestamp header
        x_request_id: Request ID header

    Returns:
        Success confirmation

    Raises:
        HTTPException: 401 if signature invalid, 400 if replay detected
    """
    # Validate required headers
    if not x_signature:
        logger.warning(
            f"[WEBHOOK_MISSING_SIGNATURE] Missing X-Signature header | "
            f"request_id={x_request_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Signature header",
        )

    if not x_timestamp:
        logger.warning(
            f"[WEBHOOK_MISSING_TIMESTAMP] Missing X-Timestamp header | "
            f"request_id={x_request_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Timestamp header",
        )

    if not x_request_id:
        logger.warning("[WEBHOOK_MISSING_REQUEST_ID] Missing X-Request-Id header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Request-Id header",
        )

    # Get request body
    body = await request.body()

    # Validate webhook signature and timestamp
    try:
        webhook_secret = settings.WEBHOOK_SECRET_KEY or "default-dev-secret"
        security_service = get_webhook_security_service(webhook_secret)

        security_service.validate_webhook(
            body=body,
            signature=x_signature,
            timestamp=x_timestamp,
            request_id=x_request_id,
        )

        logger.info(
            f"[WEBHOOK_SECURITY_PASSED] Signature and timestamp validated | "
            f"request_id={x_request_id}"
        )

    except WebhookSignatureError as e:
        logger.warning(
            f"[WEBHOOK_SIGNATURE_ERROR] {str(e)} | request_id={x_request_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature",
        )

    except WebhookReplayError as e:
        logger.warning(
            f"[WEBHOOK_REPLAY_ERROR] {str(e)} | request_id={x_request_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook request rejected (possible replay attack)",
        )

    except ValueError as e:
        logger.warning(
            f"[WEBHOOK_VALIDATION_ERROR] {str(e)} | request_id={x_request_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook headers",
        )

    # Parse payload
    try:
        import json

        payload = ParsingWebhookPayload(**json.loads(body))
    except Exception as e:
        logger.warning(
            f"[WEBHOOK_PARSE_ERROR] Failed to parse payload: {str(e)} | "
            f"request_id={x_request_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook payload",
        )

    # Validate status
    valid_statuses = ["pending", "in_progress", "completed", "failed"]
    if payload.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {payload.status}. Must be one of: {valid_statuses}",
        )

    # Get parsing job
    parsing_job = (
        db.query(ParsingJob).filter(ParsingJob.id == payload.parsing_job_id).first()
    )

    if not parsing_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parsing job {payload.parsing_job_id} not found",
        )

    # Update job status
    parsing_job.status = payload.status
    if payload.error_message:
        parsing_job.error_message = payload.error_message
    parsing_job.updated_at = datetime.utcnow()

    logger.info(
        f"[WEBHOOK_JOB_UPDATED] Parsing job updated | "
        f"job_id={payload.parsing_job_id} | "
        f"status={payload.status} | "
        f"request_id={x_request_id}"
    )

    if payload.status == "in_progress":
        parsing_job.started_at = datetime.utcnow()
    elif payload.status in ["completed", "failed"]:
        parsing_job.completed_at = datetime.utcnow()

    if payload.error_message:
        parsing_job.error_message = payload.error_message

    db.commit()

    return {
        "status": "success",
        "message": f"Parsing job {payload.parsing_job_id} updated to status: {payload.status}",
        "job_id": parsing_job.id,
    }
