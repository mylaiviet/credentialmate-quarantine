#!/usr/bin/env python3
"""
Log the Login "Failed to Fetch" Bug Fix to Auto-Issues Engine

TIMESTAMP: 2025-11-16T00:00:00Z
ORIGIN: credentialmate-docs/issues
UPDATED_FOR: Phase 6 – BugFix / UAT
STATUS: Issue Logged
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from agent_issue_wrapper import create_issue, append_issue

def main():
    """Log the login bug fix issue."""

    # Create issue dictionary
    issue = create_issue(
        repo="credentialmate-app",
        agent="claude-code-bugfix-v1",
        severity="CRITICAL",
        issue_type="bug",
        title="Login throws 'Failed to Fetch' due to CSP blocking localhost:8000",
        description=(
            "Frontend login endpoint POST /api/auth/login was blocked by overly "
            "restrictive Content-Security-Policy (CSP) header. The CSP directive "
            "'connect-src 'self'' only allows connections to the same origin "
            "(localhost:3000), preventing API calls to backend at localhost:8000. "
            "This causes login to fail with 'Failed to Fetch' error in browser console."
        ),
        repro=(
            "1. Start frontend dev server (localhost:3000)\n"
            "2. Start backend dev server (localhost:8000)\n"
            "3. Navigate to login page\n"
            "4. Attempt login with valid credentials\n"
            "5. Observe 'Failed to Fetch' error in console\n"
            "6. Check browser console for CSP violation warning"
        ),
        root_cause_guess=(
            "CSP header in frontend/next.config.js line 27 restricts "
            "connect-src to 'self' only. When frontend (port 3000) tries to "
            "call backend API (port 8000), the browser blocks the request "
            "as a CSP violation. This is a security misconfiguration that "
            "prevents same-machine dev connectivity."
        ),
        blocked_by=[],
        depends_on=[],
    )

    # Append the issue
    log_path = Path(__file__).parent / "auto_issues_log.jsonl"
    append_issue(issue, str(log_path))

    print(f"✓ Issue logged to {log_path}")
    print(f"  Issue ID: {issue['issue_id']}")
    print(f"  Status: {issue['status']}")
    print(f"  Severity: {issue['severity']}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
