"""
Batch credential upload with checkpoint system.

Processes documents in batches of 5, reports progress after each batch,
and saves checkpoints for recovery.

Usage:
    # For Tricia Nguyen
    python batch_upload_with_checkpoints.py --user-email tricia.nguyen@example.com \
        --documents-dir "C:\\Users\\mylai\\OneDrive - Delightful Healthcare\\CredentialMate\\.test_files"

    # For training data
    python batch_upload_with_checkpoints.py --training-data \
        --documents-dir "C:\\Users\\mylai\\OneDrive - Delightful Healthcare\\CredentialMate\\.test_files\\training_data"

Author: Claude Code
Created: 2025-11-06
"""

import sys
from pathlib import Path
import argparse
import json
import time
from typing import List, Dict, Any
from datetime import datetime
from uuid import UUID

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

load_dotenv()

from sqlalchemy.orm import Session
from app.core.database import engine
from app.models.user import User
from app.models.license import License
from app.models.cme_activity import CMEActivity
from app.services.document_parser import DocumentParserService
from app.utils.document_mapping import (
    identify_document_type,
    map_to_license_create,
    map_to_cme_create,
    store_in_user_metadata,
    DocumentType,
)
from app.schemas.license import LicenseCreate
from app.schemas.cme_activity import CMEActivityCreate


class CheckpointManager:
    """Manages checkpoint file for batch processing."""

    def __init__(self, checkpoint_dir: Path, checkpoint_name: str):
        """Initialize checkpoint manager."""
        self.checkpoint_dir = checkpoint_dir
        self.checkpoint_dir.mkdir(exist_ok=True)
        self.checkpoint_file = self.checkpoint_dir / f"{checkpoint_name}.json"

    def load(self) -> Dict[str, Any]:
        """Load checkpoint from file."""
        if not self.checkpoint_file.exists():
            return {
                "processed_files": [],
                "successful": 0,
                "failed": 0,
                "last_batch": 0,
                "timestamp": None,
            }

        with open(self.checkpoint_file, "r") as f:
            return json.load(f)

    def save(self, checkpoint_data: Dict[str, Any]):
        """Save checkpoint to file."""
        checkpoint_data["timestamp"] = datetime.utcnow().isoformat()
        with open(self.checkpoint_file, "w") as f:
            json.dump(checkpoint_data, f, indent=2)

    def clear(self):
        """Clear checkpoint file."""
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()


class BatchUploadProcessor:
    """Processes credential documents in batches."""

    def __init__(
        self,
        user_id: UUID,
        documents_dir: Path,
        batch_size: int = 5,
        checkpoint_name: str = "batch_upload",
    ):
        """Initialize batch processor."""
        self.user_id = user_id
        self.documents_dir = documents_dir
        self.batch_size = batch_size

        # Initialize services
        self.db = Session(engine)
        self.parser = DocumentParserService(use_mock=False)
        self.checkpoint_manager = CheckpointManager(
            checkpoint_dir=Path(__file__).parent / ".checkpoint",
            checkpoint_name=checkpoint_name,
        )

        # Statistics
        self.stats = {
            "total": 0,
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "licenses_inserted": 0,
            "cme_inserted": 0,
            "stored_in_metadata": 0,
        }

    def get_document_files(self) -> List[Path]:
        """Get all document files in directory."""
        files = []
        for ext in ["*.pdf", "*.png", "*.jpg", "*.jpeg"]:
            files.extend(self.documents_dir.glob(ext))
        return sorted(files)

    def process_batch(
        self, batch_files: List[Path], batch_num: int, total_batches: int
    ):
        """
        Process a batch of documents.

        Args:
            batch_files: List of file paths to process
            batch_num: Current batch number (1-indexed)
            total_batches: Total number of batches
        """
        print("=" * 80)
        print(f"BATCH {batch_num}/{total_batches} ({len(batch_files)} documents)")
        print("=" * 80)
        print()

        batch_results = []

        for i, file_path in enumerate(batch_files, 1):
            print(f"[{i}/{len(batch_files)}] Processing: {file_path.name}")
            print("-" * 80)

            # Add small delay to avoid rate limiting
            if i > 1:
                time.sleep(2)  # 2 second delay between documents

            try:
                result = self.process_document(file_path)
                batch_results.append(result)

                # Print result
                if result["success"]:
                    print(f"[OK] {result['action']}")
                    if result.get("db_id"):
                        print(f"   Record ID: {result['db_id']}")
                else:
                    print(f"[ERR] {result['error']}")

            except Exception as e:
                print(f"[ERR] ERROR: {str(e)[:200]}")
                batch_results.append(
                    {
                        "success": False,
                        "filename": file_path.name,
                        "error": str(e)[:200],
                        "action": "error",
                    }
                )

            print()

        # Print batch summary
        self.print_batch_summary(batch_results, batch_num, total_batches)

        # Save checkpoint
        checkpoint_data = self.checkpoint_manager.load()
        checkpoint_data["processed_files"].extend(
            [r["filename"] for r in batch_results]
        )
        checkpoint_data["successful"] += sum(1 for r in batch_results if r["success"])
        checkpoint_data["failed"] += sum(1 for r in batch_results if not r["success"])
        checkpoint_data["last_batch"] = batch_num
        self.checkpoint_manager.save(checkpoint_data)

        # Pause between batches
        if batch_num < total_batches:
            print(f"[PAUSE]  Pausing 5 seconds before next batch...\n")
            time.sleep(5)

    def process_document(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a single document.

        Args:
            file_path: Path to document file

        Returns:
            Result dictionary with success status and action taken
        """
        # Read file
        with open(file_path, "rb") as f:
            file_content = f.read()

        # Parse with AI
        parse_result = self.parser.parse_cme_certificate(file_content, file_path.name)

        if not parse_result.success:
            return {
                "success": False,
                "filename": file_path.name,
                "error": parse_result.error,
                "action": "parse_failed",
            }

        # Identify document type
        doc_type = identify_document_type(parse_result.cme_data, file_path.name)

        # Process based on type
        if doc_type == DocumentType.LICENSE:
            return self.insert_license(parse_result.cme_data, file_path.name)
        elif doc_type == DocumentType.CME:
            return self.insert_cme(parse_result.cme_data, file_path.name)
        else:
            return self.store_in_metadata(
                parse_result.cme_data, doc_type, file_path.name
            )

    def insert_license(self, parsed_data, filename: str) -> Dict[str, Any]:
        """Insert license into database."""
        try:
            # Map to LicenseCreate
            license_create = map_to_license_create(parsed_data)

            if not license_create:
                # Store in metadata instead
                return self.store_in_metadata(
                    parsed_data, DocumentType.LICENSE, filename
                )

            # Create License model
            license_obj = License(
                user_id=self.user_id, **license_create.model_dump(exclude_unset=True)
            )

            self.db.add(license_obj)
            self.db.commit()
            self.db.refresh(license_obj)

            self.stats["licenses_inserted"] += 1

            return {
                "success": True,
                "filename": filename,
                "action": f"License inserted ({license_create.state} - {license_create.license_number})",
                "db_id": str(license_obj.id),
                "type": "license",
            }

        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "filename": filename,
                "error": f"License insertion failed: {str(e)[:100]}",
                "action": "db_error",
            }

    def insert_cme(self, parsed_data, filename: str) -> Dict[str, Any]:
        """Insert CME activity into database."""
        try:
            # Map to CMEActivityCreate
            cme_create = map_to_cme_create(parsed_data)

            if not cme_create:
                # Store in metadata instead
                return self.store_in_metadata(parsed_data, DocumentType.CME, filename)

            # Create CMEActivity model
            cme_obj = CMEActivity(
                user_id=self.user_id, **cme_create.model_dump(exclude_unset=True)
            )

            self.db.add(cme_obj)
            self.db.commit()
            self.db.refresh(cme_obj)

            self.stats["cme_inserted"] += 1

            return {
                "success": True,
                "filename": filename,
                "action": f"CME activity inserted ({cme_create.credits} credits - {cme_create.title[:40]}...)",
                "db_id": str(cme_obj.id),
                "type": "cme",
            }

        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "filename": filename,
                "error": f"CME insertion failed: {str(e)[:100]}",
                "action": "db_error",
            }

    def store_in_metadata(
        self, parsed_data, doc_type: str, filename: str
    ) -> Dict[str, Any]:
        """Store document in user metadata."""
        try:
            # Get user
            user = self.db.query(User).filter(User.id == self.user_id).first()

            if not user:
                return {
                    "success": False,
                    "filename": filename,
                    "error": "User not found",
                    "action": "user_not_found",
                }

            # Update metadata
            updated_metadata = store_in_user_metadata(
                user_metadata=user.user_metadata,
                parsed_data=parsed_data,
                doc_type=doc_type,
                filename=filename,
            )

            user.user_metadata = updated_metadata
            self.db.commit()

            self.stats["stored_in_metadata"] += 1

            return {
                "success": True,
                "filename": filename,
                "action": f"Stored in metadata ({doc_type})",
                "type": "metadata",
            }

        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "filename": filename,
                "error": f"Metadata storage failed: {str(e)[:100]}",
                "action": "db_error",
            }

    def print_batch_summary(
        self, batch_results: List[Dict], batch_num: int, total_batches: int
    ):
        """Print summary for batch."""
        print("=" * 80)
        print(f"BATCH {batch_num}/{total_batches} COMPLETE")
        print("=" * 80)

        success_count = sum(1 for r in batch_results if r["success"])
        failure_count = sum(1 for r in batch_results if not r["success"])

        licenses = sum(1 for r in batch_results if r.get("type") == "license")
        cmes = sum(1 for r in batch_results if r.get("type") == "cme")
        metadata = sum(1 for r in batch_results if r.get("type") == "metadata")

        print(f"Success: {success_count}/{len(batch_results)}")
        print(f"Failures: {failure_count}/{len(batch_results)}")
        print(f"Database: {licenses} licenses, {cmes} CME activities")
        print(f"Metadata: {metadata} documents")
        print("=" * 80)
        print()

    def run(self):
        """Run batch processing."""
        print("=" * 80)
        print("BATCH CREDENTIAL UPLOAD")
        print("=" * 80)
        print(f"User ID: {self.user_id}")
        print(f"Documents directory: {self.documents_dir}")
        print(f"Batch size: {self.batch_size}")
        print()

        # Get all files
        all_files = self.get_document_files()
        print(f"Total files found: {len(all_files)}")
        print()

        # Load checkpoint
        checkpoint = self.checkpoint_manager.load()
        processed_files = set(checkpoint["processed_files"])

        # Filter out already processed files
        files_to_process = [f for f in all_files if f.name not in processed_files]

        if not files_to_process:
            print("[OK] All files already processed!")
            print(
                f"Checkpoint: {checkpoint['successful']} successful, {checkpoint['failed']} failed"
            )
            return

        print(f"Files to process: {len(files_to_process)}")
        if processed_files:
            print(
                f"Resuming from checkpoint (already processed: {len(processed_files)})"
            )
        print()

        # Process in batches
        total_batches = (len(files_to_process) + self.batch_size - 1) // self.batch_size

        for batch_num in range(1, total_batches + 1):
            start_idx = (batch_num - 1) * self.batch_size
            end_idx = min(start_idx + self.batch_size, len(files_to_process))
            batch_files = files_to_process[start_idx:end_idx]

            self.process_batch(batch_files, batch_num, total_batches)

        # Final summary
        self.print_final_summary()

    def print_final_summary(self):
        """Print final summary."""
        checkpoint = self.checkpoint_manager.load()

        print("=" * 80)
        print("FINAL SUMMARY")
        print("=" * 80)
        print(f"Total files processed: {len(checkpoint['processed_files'])}")
        print(f"Successful: {checkpoint['successful']}")
        print(f"Failed: {checkpoint['failed']}")
        print()
        print(f"Database records created:")
        print(f"  Licenses: {self.stats['licenses_inserted']}")
        print(f"  CME Activities: {self.stats['cme_inserted']}")
        print(f"  Stored in metadata: {self.stats['stored_in_metadata']}")
        print("=" * 80)
        print()
        print("[OK] Batch upload complete!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Batch credential upload with checkpoints"
    )
    parser.add_argument("--user-email", help="User email for single-user upload")
    parser.add_argument(
        "--documents-dir", required=True, help="Directory containing documents"
    )
    parser.add_argument(
        "--batch-size", type=int, default=5, help="Batch size (default: 5)"
    )
    parser.add_argument(
        "--training-data",
        action="store_true",
        help="Process training data (multiple users)",
    )

    args = parser.parse_args()

    documents_dir = Path(args.documents_dir)
    if not documents_dir.exists():
        print(f"[ERR] Directory not found: {documents_dir}")
        sys.exit(1)

    # Create database session
    db = Session(engine)

    try:
        if args.training_data:
            print("Training data mode not yet implemented")
            # TODO: Implement multi-user batch processing
            sys.exit(1)
        else:
            # Single user mode
            if not args.user_email:
                print("[ERR] --user-email required for single-user mode")
                sys.exit(1)

            # Get user
            user = db.query(User).filter(User.email == args.user_email).first()
            if not user:
                print(f"[ERR] User not found: {args.user_email}")
                print("Run verify_and_create_users.py first")
                sys.exit(1)

            # Run batch processor
            processor = BatchUploadProcessor(
                user_id=user.id,
                documents_dir=documents_dir,
                batch_size=args.batch_size,
                checkpoint_name=f"batch_upload_{user.email.replace('@', '_at_')}",
            )

            processor.run()

    finally:
        db.close()


if __name__ == "__main__":
    main()
