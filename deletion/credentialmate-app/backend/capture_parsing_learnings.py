"""
Structured learning capture system for document parsing edge cases.

This script processes documents and captures detailed learnings about:
- Parsing failures and reasons
- Edge cases discovered
- AI response patterns
- Data quality issues
- Suggested improvements

Used by multiple AI agents (Claude Code, Cursor AI, ChatGPT Codex) to build
a comprehensive knowledge base of parsing patterns.

Author: Claude Code
Created: 2025-11-06
"""

import sys
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import argparse
import time

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

load_dotenv()

from app.services.document_parser import DocumentParserService
from app.utils.document_mapping import identify_document_type


class ParsingLearning:
    """Structured learning from a single document parse attempt."""

    def __init__(self, filename: str):
        self.filename = filename
        self.timestamp = datetime.utcnow().isoformat()
        self.file_size = None
        self.file_type = None
        self.success = False
        self.error_type = None
        self.error_message = None
        self.ai_response_raw = None
        self.parsed_data = None
        self.confidence_score = None
        self.document_type_identified = None
        self.edge_cases = []
        self.data_quality_issues = []
        self.parsing_challenges = []
        self.ai_reasoning = None
        self.field_confidence = None
        self.suggested_improvements = []
        self.agent_name = "claude_code"  # Default

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "filename": self.filename,
            "timestamp": self.timestamp,
            "agent_name": self.agent_name,
            "file_metadata": {"size_bytes": self.file_size, "type": self.file_type},
            "parsing_result": {
                "success": self.success,
                "confidence_score": self.confidence_score,
                "document_type": self.document_type_identified,
            },
            "error_info": {"type": self.error_type, "message": self.error_message}
            if self.error_type
            else None,
            "ai_analysis": {
                "reasoning": self.ai_reasoning,
                "field_confidence": self.field_confidence,
                "parsed_data_summary": self._summarize_parsed_data(),
            },
            "learnings": {
                "edge_cases": self.edge_cases,
                "data_quality_issues": self.data_quality_issues,
                "parsing_challenges": self.parsing_challenges,
                "suggested_improvements": self.suggested_improvements,
            },
        }

    def _summarize_parsed_data(self) -> Optional[Dict[str, Any]]:
        """Summarize parsed data without exposing full content."""
        if not self.parsed_data:
            return None

        return {
            "title": self.parsed_data.title
            if hasattr(self.parsed_data, "title")
            else None,
            "provider": self.parsed_data.provider
            if hasattr(self.parsed_data, "provider")
            else None,
            "credits": self.parsed_data.credits
            if hasattr(self.parsed_data, "credits")
            else None,
            "has_completion_date": bool(self.parsed_data.completion_date)
            if hasattr(self.parsed_data, "completion_date")
            else None,
            "has_certificate_number": bool(self.parsed_data.certificate_number)
            if hasattr(self.parsed_data, "certificate_number")
            else None,
            "fields_present": [
                k for k, v in self.parsed_data.__dict__.items() if v is not None
            ]
            if hasattr(self.parsed_data, "__dict__")
            else [],
        }


class LearningCaptureProcessor:
    """Processes documents and captures structured learnings."""

    def __init__(self, agent_name: str = "claude_code", use_mock: bool = False):
        self.agent_name = agent_name
        self.parser = DocumentParserService(use_mock=use_mock)
        self.learnings: List[ParsingLearning] = []

    def process_document(self, file_path: Path) -> ParsingLearning:
        """
        Process a single document and capture learnings.

        Args:
            file_path: Path to document file

        Returns:
            ParsingLearning object with structured insights
        """
        learning = ParsingLearning(file_path.name)
        learning.agent_name = self.agent_name

        # Read file
        with open(file_path, "rb") as f:
            content = f.read()

        learning.file_size = len(content)
        learning.file_type = file_path.suffix

        # Attempt parsing
        try:
            result = self.parser.parse_cme_certificate(content, file_path.name)

            if result.success:
                learning.success = True
                learning.parsed_data = result.cme_data
                learning.confidence_score = result.cme_data.confidence_score
                learning.ai_reasoning = (
                    result.cme_data.metadata.get("reasoning")
                    if result.cme_data.metadata
                    else None
                )
                learning.field_confidence = result.cme_data.field_confidence

                # Identify document type
                learning.document_type_identified = identify_document_type(
                    result.cme_data, file_path.name
                )

                # Analyze for edge cases
                self._detect_edge_cases(learning, result.cme_data)

                # Analyze data quality
                self._detect_data_quality_issues(learning, result.cme_data)

            else:
                learning.success = False
                learning.error_type = "parsing_failed"
                learning.error_message = result.error

                # Categorize error
                self._categorize_error(learning, result.error)

        except Exception as e:
            learning.success = False
            learning.error_type = "exception"
            learning.error_message = str(e)

            # Analyze exception
            self._analyze_exception(learning, e)

        self.learnings.append(learning)
        return learning

    def _detect_edge_cases(self, learning: ParsingLearning, parsed_data):
        """Detect edge cases in successfully parsed data."""

        # Multiple activities in one document
        if learning.ai_reasoning and "multiple" in learning.ai_reasoning.lower():
            learning.edge_cases.append(
                {
                    "type": "multiple_activities_in_document",
                    "description": "Document contains multiple credential activities",
                    "impact": "Only first activity captured",
                    "suggested_fix": "Support array of activities in response",
                }
            )

        # Missing optional fields
        optional_fields = ["category", "state", "certificate_number"]
        missing_fields = [
            f for f in optional_fields if not getattr(parsed_data, f, None)
        ]
        if len(missing_fields) >= 2:
            learning.edge_cases.append(
                {
                    "type": "sparse_optional_fields",
                    "description": f"Multiple optional fields missing: {', '.join(missing_fields)}",
                    "impact": "Reduced data richness",
                    "suggested_fix": "Enhance AI prompt to extract optional fields",
                }
            )

        # Low confidence on specific fields
        if learning.field_confidence:
            low_conf_fields = {
                k: v for k, v in learning.field_confidence.items() if v and v < 0.7
            }
            if low_conf_fields:
                learning.edge_cases.append(
                    {
                        "type": "low_field_confidence",
                        "description": f"Low confidence on fields: {', '.join(low_conf_fields.keys())}",
                        "impact": "Data may be inaccurate",
                        "suggested_fix": "Review AI extraction for these field types",
                    }
                )

        # Non-CME document parsed as CME
        if (
            learning.document_type_identified
            and learning.document_type_identified not in ["cme"]
        ):
            learning.edge_cases.append(
                {
                    "type": "document_type_mismatch",
                    "description": f"Document type is '{learning.document_type_identified}' but parsed as CME",
                    "impact": "Wrong schema used",
                    "suggested_fix": "Pre-classify document type before parsing",
                }
            )

    def _detect_data_quality_issues(self, learning: ParsingLearning, parsed_data):
        """Detect data quality issues."""

        # Very short titles
        if parsed_data.title and len(parsed_data.title) < 10:
            learning.data_quality_issues.append(
                {
                    "field": "title",
                    "issue": "Title is very short (< 10 chars)",
                    "value_length": len(parsed_data.title),
                }
            )

        # Zero credits
        if parsed_data.credits is not None and parsed_data.credits == 0:
            learning.data_quality_issues.append(
                {
                    "field": "credits",
                    "issue": "Credits is 0 (likely missing data)",
                    "suggested_fix": "Mark as None if not found",
                }
            )

        # Missing provider
        if not parsed_data.provider or parsed_data.provider.lower() in [
            "unknown",
            "n/a",
        ]:
            learning.data_quality_issues.append(
                {
                    "field": "provider",
                    "issue": "Provider missing or generic",
                    "suggested_fix": "Extract from issuing organization",
                }
            )

    def _categorize_error(self, learning: ParsingLearning, error_msg: str):
        """Categorize parsing errors."""

        error_lower = error_msg.lower()

        if "json" in error_lower and "extra data" in error_lower:
            learning.parsing_challenges.append(
                {
                    "type": "multiple_json_objects",
                    "description": "AI returned multiple JSON objects instead of one",
                    "root_cause": "Document contains multiple activities",
                    "current_fix": "Extract first JSON object only",
                    "improvement_needed": "Support array responses from AI",
                }
            )

        elif "validation" in error_lower and "field_confidence" in error_lower:
            learning.parsing_challenges.append(
                {
                    "type": "field_confidence_validation",
                    "description": "AI returned None for field_confidence values",
                    "root_cause": "AI cannot assess confidence for non-applicable fields",
                    "current_fix": "Convert None to 0.0",
                    "improvement_needed": "Make field_confidence optional",
                }
            )

        elif "image exceeds 5 mb" in error_lower:
            learning.parsing_challenges.append(
                {
                    "type": "image_size_limit",
                    "description": "Image exceeds AWS Bedrock 5MB limit",
                    "root_cause": "Large image from phone/screenshot",
                    "current_fix": "Compress images before sending to LLM",
                    "improvement_needed": "Already implemented",
                }
            )

        elif "validation" in error_lower:
            learning.parsing_challenges.append(
                {
                    "type": "schema_validation_error",
                    "description": "Parsed data doesn't match expected schema",
                    "error_details": error_msg,
                    "suggested_fix": "Review AI prompt and schema alignment",
                }
            )

        else:
            learning.parsing_challenges.append(
                {
                    "type": "unknown_error",
                    "description": error_msg,
                    "suggested_fix": "Investigate and categorize",
                }
            )

    def _analyze_exception(self, learning: ParsingLearning, exception: Exception):
        """Analyze exceptions."""

        exc_type = type(exception).__name__
        exc_msg = str(exception)

        learning.parsing_challenges.append(
            {
                "type": "exception",
                "exception_type": exc_type,
                "message": exc_msg,
                "suggested_fix": "Add error handling for this case",
            }
        )

    def save_learnings(self, output_file: Path):
        """Save all learnings to JSON file."""

        output_data = {
            "metadata": {
                "agent_name": self.agent_name,
                "timestamp": datetime.utcnow().isoformat(),
                "total_documents": len(self.learnings),
                "successful_parses": sum(1 for l in self.learnings if l.success),
                "failed_parses": sum(1 for l in self.learnings if not l.success),
            },
            "learnings": [l.to_dict() for l in self.learnings],
        }

        with open(output_file, "w") as f:
            json.dump(output_data, f, indent=2)

        print(f"[OK] Saved {len(self.learnings)} learnings to {output_file}")

    def print_summary(self):
        """Print summary of learnings."""

        print("\n" + "=" * 80)
        print("LEARNING CAPTURE SUMMARY")
        print("=" * 80)
        print(f"Agent: {self.agent_name}")
        print(f"Total documents: {len(self.learnings)}")
        print(f"Successful: {sum(1 for l in self.learnings if l.success)}")
        print(f"Failed: {sum(1 for l in self.learnings if not l.success)}")
        print()

        # Edge cases summary
        all_edge_cases = [ec for l in self.learnings for ec in l.edge_cases]
        edge_case_types = {}
        for ec in all_edge_cases:
            ec_type = ec.get("type", "unknown")
            edge_case_types[ec_type] = edge_case_types.get(ec_type, 0) + 1

        if edge_case_types:
            print("Edge Cases Discovered:")
            for ec_type, count in sorted(edge_case_types.items(), key=lambda x: -x[1]):
                print(f"  - {ec_type}: {count} occurrences")
            print()

        # Error patterns
        error_types = {}
        for l in self.learnings:
            if not l.success and l.error_type:
                error_types[l.error_type] = error_types.get(l.error_type, 0) + 1

        if error_types:
            print("Error Patterns:")
            for err_type, count in sorted(error_types.items(), key=lambda x: -x[1]):
                print(f"  - {err_type}: {count} occurrences")
            print()

        print("=" * 80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Capture structured learnings from document parsing"
    )
    parser.add_argument(
        "--documents-dir", required=True, help="Directory containing documents"
    )
    parser.add_argument(
        "--output", default="parsing_learnings.json", help="Output JSON file"
    )
    parser.add_argument(
        "--agent-name",
        default="claude_code",
        help="Agent name (claude_code, cursor_ai, codex)",
    )
    parser.add_argument(
        "--file-pattern", help="Process only files matching pattern (e.g., '*.pdf')"
    )

    args = parser.parse_args()

    documents_dir = Path(args.documents_dir)
    if not documents_dir.exists():
        print(f"[ERR] Directory not found: {documents_dir}")
        sys.exit(1)

    # Get files to process
    if args.file_pattern:
        files = list(documents_dir.glob(args.file_pattern))
    else:
        files = []
        for ext in ["*.pdf", "*.png", "*.jpg", "*.jpeg"]:
            files.extend(documents_dir.glob(ext))

    files = sorted(files)

    print("=" * 80)
    print("LEARNING CAPTURE - DOCUMENT PARSING")
    print("=" * 80)
    print(f"Agent: {args.agent_name}")
    print(f"Documents: {len(files)}")
    print(f"Output: {args.output}")
    print()

    # Process documents
    processor = LearningCaptureProcessor(agent_name=args.agent_name)

    for i, file_path in enumerate(files, 1):
        print(
            f"[{i}/{len(files)}] Processing: {file_path.name}... ", end="", flush=True
        )

        # Add delay to avoid rate limiting (skip for first file)
        if i > 1:
            time.sleep(3)  # 3 second delay between API calls

        try:
            learning = processor.process_document(file_path)
            status = "[OK]" if learning.success else "[FAIL]"
            print(status)
        except Exception as e:
            print(f"[ERR] {str(e)[:50]}")

    # Save learnings
    output_file = Path(args.output)
    processor.save_learnings(output_file)

    # Print summary
    processor.print_summary()


if __name__ == "__main__":
    main()
