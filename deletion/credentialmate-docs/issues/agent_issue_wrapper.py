#!/usr/bin/env python3
"""
Automated Global Issues Log - Agent Issue Wrapper

TIMESTAMP: 2025-11-16T00:00:00Z
ORIGIN: credentialmate-docs/issues
UPDATED_FOR: Phase 6 – BugFix / UAT
STATUS: Active
CLASSIFICATION: Development-Time Only (Never executed in production)

PURPOSE:
A deterministic Python helper for appending issues to auto_issues_log.jsonl.
Implements simple validation and append-only writing without external dependencies.

DESIGN CONSTRAINTS:
- No external dependencies beyond Python stdlib
- Never deletes or modifies prior entries
- Validates required fields before appending
- Dev-time only (never executed in production)
- Deterministic output for audit trail compliance
"""

import json
import uuid
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


# SOC2 COMPLIANCE HEADER
ISSUES_LOG_HEADER = """# SOC2 TYPE II COMPLIANT ISSUE LOG
# ORIGIN: Automated Global Issues Log (Auto-Issues Engine)
# TIMESTAMP: 2025-11-16T00:00:00Z
# SCHEMA_VERSION: 1.0
# UPDATED_FOR: Phase 6 – BugFix / UAT
# ACCESS_CONTROL: credentialmate-docs repository only
# RETENTION: Indefinite (audit trail)
# INTEGRITY: Append-only JSONL, never modify prior entries
# CLASSIFICATION: Internal Development

"""


class IssueValidationError(Exception):
    """Raised when issue fails schema validation."""
    pass


class IssueAppender:
    """Helper class for validating and appending issues to auto_issues_log.jsonl."""

    # Required fields and their types
    REQUIRED_FIELDS = {
        "issue_id": str,
        "timestamp_utc": str,
        "repo": str,
        "agent": str,
        "severity": str,
        "type": str,
        "status": str,
        "title": str,
        "description": str,
        "repro": str,
        "root_cause_guess": str,
        "blocked_by": list,
        "depends_on": list,
        "attempts": int,
        "fix_summary": str,
    }

    # Enum values for validation
    VALID_REPOS = {
        "credentialmate-app",
        "credentialmate-infra",
        "credentialmate-rules",
        "credentialmate-notification",
        "credentialmate-schemas",
        "credentialmate-ai",
        "credentialmate-docs",
    }

    VALID_SEVERITIES = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}

    VALID_TYPES = {
        "bug",
        "enhancement",
        "tech_debt",
        "security",
        "documentation",
        "performance",
        "compliance",
    }

    VALID_STATUSES = {
        "NEW",
        "TRIAGED",
        "IN_PROGRESS",
        "FIXED",
        "VERIFIED",
        "CLOSED",
        "WONTFIX",
    }

    def __init__(self, log_path: Optional[str] = None):
        """
        Initialize the issue appender.

        Args:
            log_path: Path to auto_issues_log.jsonl. If None, uses default location.
        """
        if log_path:
            self.log_path = Path(log_path)
        else:
            # Default: assume script is in credentialmate-docs/issues/
            script_dir = Path(__file__).parent
            self.log_path = script_dir / "auto_issues_log.jsonl"

    def validate_issue(self, issue: Dict[str, Any]) -> None:
        """
        Validate that an issue conforms to the schema.

        Args:
            issue: Dictionary representing an issue.

        Raises:
            IssueValidationError: If validation fails.
        """
        # Check for required fields
        missing_fields = set(self.REQUIRED_FIELDS.keys()) - set(issue.keys())
        if missing_fields:
            raise IssueValidationError(
                f"Missing required fields: {', '.join(sorted(missing_fields))}"
            )

        # Check field types
        for field, expected_type in self.REQUIRED_FIELDS.items():
            value = issue[field]
            if not isinstance(value, expected_type):
                raise IssueValidationError(
                    f"Field '{field}' must be {expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )

        # Validate UUID format
        if not self._is_valid_uuid4(issue["issue_id"]):
            raise IssueValidationError(
                f"Field 'issue_id' must be a valid UUID4: {issue['issue_id']}"
            )

        # Validate timestamp format (ISO 8601 UTC)
        if not self._is_valid_timestamp(issue["timestamp_utc"]):
            raise IssueValidationError(
                f"Field 'timestamp_utc' must be ISO 8601 UTC "
                f"(YYYY-MM-DDTHH:MM:SSZ): {issue['timestamp_utc']}"
            )

        # Validate enum fields
        if issue["repo"] not in self.VALID_REPOS:
            raise IssueValidationError(
                f"Field 'repo' must be one of: {', '.join(sorted(self.VALID_REPOS))}. "
                f"Got: {issue['repo']}"
            )

        if issue["severity"] not in self.VALID_SEVERITIES:
            raise IssueValidationError(
                f"Field 'severity' must be one of: {', '.join(sorted(self.VALID_SEVERITIES))}. "
                f"Got: {issue['severity']}"
            )

        if issue["type"] not in self.VALID_TYPES:
            raise IssueValidationError(
                f"Field 'type' must be one of: {', '.join(sorted(self.VALID_TYPES))}. "
                f"Got: {issue['type']}"
            )

        if issue["status"] not in self.VALID_STATUSES:
            raise IssueValidationError(
                f"Field 'status' must be one of: {', '.join(sorted(self.VALID_STATUSES))}. "
                f"Got: {issue['status']}"
            )

        # Validate string length constraints
        if len(issue["title"]) < 10 or len(issue["title"]) > 200:
            raise IssueValidationError(
                f"Field 'title' must be 10-200 characters. Got {len(issue['title'])}"
            )

        if len(issue["description"]) < 20:
            raise IssueValidationError(
                f"Field 'description' must be at least 20 characters. "
                f"Got {len(issue['description'])}"
            )

        if len(issue["repro"]) < 10:
            raise IssueValidationError(
                f"Field 'repro' must be at least 10 characters. "
                f"Got {len(issue['repro'])}"
            )

        if len(issue["root_cause_guess"]) < 10:
            raise IssueValidationError(
                f"Field 'root_cause_guess' must be at least 10 characters. "
                f"Got {len(issue['root_cause_guess'])}"
            )

        # Validate integer constraints
        if issue["attempts"] < 0:
            raise IssueValidationError(
                f"Field 'attempts' must be >= 0. Got: {issue['attempts']}"
            )

        # Validate array contents (must be valid UUIDs)
        for uuid_str in issue["blocked_by"]:
            if not self._is_valid_uuid4(uuid_str):
                raise IssueValidationError(
                    f"Field 'blocked_by' contains invalid UUID4: {uuid_str}"
                )

        for uuid_str in issue["depends_on"]:
            if not self._is_valid_uuid4(uuid_str):
                raise IssueValidationError(
                    f"Field 'depends_on' contains invalid UUID4: {uuid_str}"
                )

        # Check for duplicate issue_id in existing log
        if self.log_path.exists():
            try:
                with open(self.log_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            try:
                                entry = json.loads(line)
                                if entry.get("issue_id") == issue["issue_id"]:
                                    raise IssueValidationError(
                                        f"Issue ID already exists in log: {issue['issue_id']}. "
                                        f"Use unique issue_id or create status update entry."
                                    )
                            except json.JSONDecodeError:
                                pass  # Skip malformed lines
            except Exception as e:
                if isinstance(e, IssueValidationError):
                    raise
                # If we can't read the file, warn but continue
                print(f"Warning: Could not validate uniqueness: {e}")

    def append_issue(self, issue: Dict[str, Any]) -> None:
        """
        Validate and append an issue to the JSONL log.

        Args:
            issue: Dictionary representing an issue.

        Raises:
            IssueValidationError: If validation fails.
        """
        # Validate before appending
        self.validate_issue(issue)

        # Ensure log file exists with header
        if not self.log_path.exists():
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_path, "w", encoding="utf-8") as f:
                f.write(ISSUES_LOG_HEADER)

        # Append the issue as a JSON line
        with open(self.log_path, "a", encoding="utf-8") as f:
            json.dump(issue, f, separators=(",", ":"))
            f.write("\n")

    def check_new_issues(self) -> List[Dict[str, Any]]:
        """
        Retrieve all issues with status='NEW'.

        Returns:
            List of issue dictionaries with status NEW.
        """
        new_issues = []

        if not self.log_path.exists():
            return new_issues

        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    try:
                        entry = json.loads(line)
                        if entry.get("status") == "NEW":
                            new_issues.append(entry)
                    except json.JSONDecodeError:
                        pass

        return new_issues

    def get_issue_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of all issues in the log.

        Returns:
            Dictionary with summary statistics.
        """
        summary = {
            "total_issues": 0,
            "by_status": {},
            "by_severity": {},
            "by_repo": {},
            "by_type": {},
            "new_count": 0,
        }

        if not self.log_path.exists():
            return summary

        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    try:
                        entry = json.loads(line)

                        # Count total
                        summary["total_issues"] += 1

                        # Count by status
                        status = entry.get("status", "UNKNOWN")
                        summary["by_status"][status] = summary["by_status"].get(status, 0) + 1
                        if status == "NEW":
                            summary["new_count"] += 1

                        # Count by severity
                        severity = entry.get("severity", "UNKNOWN")
                        summary["by_severity"][severity] = (
                            summary["by_severity"].get(severity, 0) + 1
                        )

                        # Count by repo
                        repo = entry.get("repo", "UNKNOWN")
                        summary["by_repo"][repo] = summary["by_repo"].get(repo, 0) + 1

                        # Count by type
                        issue_type = entry.get("type", "UNKNOWN")
                        summary["by_type"][issue_type] = summary["by_type"].get(issue_type, 0) + 1

                    except json.JSONDecodeError:
                        pass

        return summary

    @staticmethod
    def _is_valid_uuid4(value: str) -> bool:
        """Check if value is a valid UUID4 format."""
        try:
            parsed = uuid.UUID(value, version=4)
            return str(parsed) == value
        except (ValueError, AttributeError):
            return False

    @staticmethod
    def _is_valid_timestamp(value: str) -> bool:
        """Check if value is a valid ISO 8601 UTC timestamp."""
        try:
            if not value.endswith("Z"):
                return False
            # Try parsing (will raise if invalid)
            datetime.datetime.fromisoformat(value[:-1])
            return True
        except (ValueError, AttributeError):
            return False


def append_issue(issue: Dict[str, Any], log_path: Optional[str] = None) -> None:
    """
    Convenience function to append a single issue.

    Args:
        issue: Dictionary representing an issue.
        log_path: Optional path to custom log file.

    Raises:
        IssueValidationError: If validation fails.
    """
    appender = IssueAppender(log_path)
    appender.append_issue(issue)


def create_issue(
    repo: str,
    agent: str,
    severity: str,
    issue_type: str,
    title: str,
    description: str,
    repro: str,
    root_cause_guess: str,
    blocked_by: Optional[List[str]] = None,
    depends_on: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Helper function to create a properly-formatted issue dictionary.

    Args:
        repo: Repository name (see VALID_REPOS)
        agent: Agent identifier
        severity: Severity level (CRITICAL|HIGH|MEDIUM|LOW)
        issue_type: Issue type (bug|enhancement|tech_debt|security|documentation|performance|compliance)
        title: One-line summary (10-200 chars)
        description: Detailed description (20+ chars)
        repro: Reproduction steps (10+ chars)
        root_cause_guess: Suspected root cause (10+ chars)
        blocked_by: Optional list of blocking issue UUIDs
        depends_on: Optional list of dependency issue UUIDs

    Returns:
        Dictionary ready for append_issue()
    """
    return {
        "issue_id": str(uuid.uuid4()),
        "timestamp_utc": datetime.datetime.utcnow().isoformat() + "Z",
        "repo": repo,
        "agent": agent,
        "severity": severity,
        "type": issue_type,
        "status": "NEW",
        "title": title,
        "description": description,
        "repro": repro,
        "root_cause_guess": root_cause_guess,
        "blocked_by": blocked_by or [],
        "depends_on": depends_on or [],
        "attempts": 0,
        "fix_summary": "",
    }


if __name__ == "__main__":
    """
    Example usage and testing.
    Run: python agent_issue_wrapper.py
    """
    import sys

    # Example: Create and append an issue
    example_issue = create_issue(
        repo="credentialmate-app",
        agent="claude-code-audit-v1",
        severity="HIGH",
        issue_type="bug",
        title="Missing input validation in auth endpoint",
        description="POST /auth/login does not validate email format before database query",
        repro="Send invalid email to POST /auth/login",
        root_cause_guess="Validation middleware missing from auth routes",
    )

    appender = IssueAppender()

    # Check for command-line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--check-new":
        # List new issues
        new_issues = appender.check_new_issues()
        if new_issues:
            print(f"Found {len(new_issues)} NEW issue(s):\n")
            for issue in new_issues:
                print(f"  [{issue['severity']}] {issue['title']}")
                print(f"    Issue ID: {issue['issue_id']}")
                print(f"    Repo: {issue['repo']}")
                print()
        else:
            print("No NEW issues found.")

    elif len(sys.argv) > 1 and sys.argv[1] == "--summary":
        # Print summary
        summary = appender.get_issue_summary()
        print("Issue Summary")
        print("=============")
        print(f"Total issues: {summary['total_issues']}")
        print(f"NEW issues: {summary['new_count']}")
        print(f"\nBy Status: {summary['by_status']}")
        print(f"By Severity: {summary['by_severity']}")
        print(f"By Repository: {summary['by_repo']}")
        print(f"By Type: {summary['by_type']}")

    else:
        # Default: show example (don't actually append)
        print("Agent Issue Wrapper - Example")
        print("=============================\n")
        print("Example issue to be logged:")
        print(json.dumps(example_issue, indent=2))
        print("\nTo append this issue:")
        print("  from agent_issue_wrapper import append_issue")
        print("  append_issue(example_issue)")
        print("\nTo check for NEW issues:")
        print("  python agent_issue_wrapper.py --check-new")
        print("\nTo get summary:")
        print("  python agent_issue_wrapper.py --summary")
