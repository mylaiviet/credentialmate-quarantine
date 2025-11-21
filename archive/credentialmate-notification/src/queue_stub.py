"""
SOC2 Compliance: No external calls or data transmission
Security: Stub implementation for testing only
Audit: All enqueue operations logged but not executed
Privacy: No data leaves the application boundary

TIMESTAMP: 2025-11-15T15:00:00Z
ORIGIN: credentialmate-notification
UPDATED_FOR: Phase 2 Step 7 - Notification Engine Integration (STUB ONLY)

Queue stub for notification sending (STUBS ONLY).

This module provides placeholder implementations for notification queue operations.
NO actual delivery logic - STUB ONLY for Phase 2 Step 7.

NOTE: Actual queue integration (SQS/Celery) is OUT OF SCOPE for Phase 2 Step 7.
"""

from typing import Dict, Any, Optional
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


class NotificationQueueStub:
    """
    STUB IMPLEMENTATION - Phase 2 Step 7

    Placeholder for notification queue operations.
    NO actual SQS, Celery, or external service calls.
    """

    def enqueue_notification_send(
        self,
        notification_id: UUID,
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """
        STUB: Enqueue a single notification for sending.

        Args:
            notification_id: Notification UUID to send
            priority: Priority level (normal, high, urgent)

        Returns:
            Dict with status and metadata (placeholder)
        """
        logger.info(
            f"STUB: Would enqueue notification {notification_id} "
            f"with priority {priority}"
        )

        return {
            "status": "enqueued",
            "notification_id": str(notification_id),
            "priority": priority,
            "queue": "notification-queue-stub",
            "message": "STUB: Notification queued (no actual delivery)"
        }

    def enqueue_bulk_message_job(
        self,
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        STUB: Enqueue a bulk message job.

        Args:
            job_data: Bulk job configuration including provider list,
                     message template, and delivery settings

        Returns:
            Dict with job status (placeholder)
        """
        provider_count = len(job_data.get("provider_ids", []))
        logger.info(
            f"STUB: Would enqueue bulk message job for {provider_count} providers"
        )

        return {
            "status": "enqueued",
            "job_id": job_data.get("job_id", "stub-job-id"),
            "provider_count": provider_count,
            "queue": "bulk-message-queue-stub",
            "message": "STUB: Bulk job queued (no actual delivery)"
        }

    def get_queue_status(self) -> Dict[str, Any]:
        """
        STUB: Get queue status metrics.

        Returns:
            Dict with queue metrics (placeholder)
        """
        return {
            "queue_name": "notification-queue-stub",
            "messages_visible": 0,
            "messages_in_flight": 0,
            "messages_delayed": 0,
            "status": "STUB - no actual queue"
        }


# Singleton instance for import convenience
notification_queue = NotificationQueueStub()


def enqueue_notification_send(
    notification_id: UUID,
    priority: str = "normal"
) -> Dict[str, Any]:
    """
    Convenience function for enqueueing notifications.

    Args:
        notification_id: Notification UUID
        priority: Priority level

    Returns:
        Enqueue result (stub)
    """
    return notification_queue.enqueue_notification_send(
        notification_id,
        priority
    )


def enqueue_bulk_message_job(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function for enqueueing bulk jobs.

    Args:
        job_data: Bulk job configuration

    Returns:
        Enqueue result (stub)
    """
    return notification_queue.enqueue_bulk_message_job(job_data)
