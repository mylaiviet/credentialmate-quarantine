#!/usr/bin/env python3
"""
Audit High-Accuracy Documents for Hidden GT Issues
Analyzes TD-001, TD-003, TD-004, TD-005, TD-006, TD-021, TD-022 for potential improvements
"""

import json
from pathlib import Path

# High-accuracy documents from SESSION-1-4-FIELD-EXTRACTION-RESULTS.json
HIGH_ACCURACY_DOCS = {
    "TD-001": {
        "accuracy": 100.0,
        "issues": [],  # Perfect! Use as gold standard
    },
    "TD-003": {
        "accuracy": 80.0,
        "issues": [
            {
                "field": "credential_details.title",
                "expected": "UpToDate",
                "actual": None,
                "fix": "GT expects 'UpToDate', model says null - need to verify which is correct"
            },
            {
                "field": "credential_details.date_range",
                "expected": "May 29, 2024 - May 29, 2024",
                "actual": None,
                "fix": "GT expects date range, model says null - need to verify"
            }
        ]
    },
    "TD-004": {
        "accuracy": 63.6,
        "issues": [
            {
                "field": "professional_designation",
                "expected": "MD",
                "actual": "MEDICAL DOCTOR",
                "fix": "Normalization issue - both are correct, need fuzzy match"
            },
            {
                "field": "issue_date",
                "expected": "2025-10-28",
                "actual": None,
                "fix": "GT has date, model didn't extract - verify if visible on document"
            },
            {
                "field": "jurisdiction",
                "expected": "Missouri",
                "actual": "MO",
                "fix": "Normalization issue - both are correct, need to normalize to 2-letter code"
            },
            {
                "field": "issuing_authority",
                "expected": "Missouri Department of Health and Senior Services - Bureau of Narcotics and Dangerous Drugs",
                "actual": "Bureau of Narcotics and Dangerous Drugs, Missouri Department of Health and Senior Services",
                "fix": "Word order difference - same authority, need fuzzy match"
            }
        ]
    },
}

POTENTIAL_GT_FIXES = {
    "TD-003": {
        # These might be wrong in GT - need to verify against actual document
        # "credential_details.title": None,  # If model is right, GT should be null not "UpToDate"
        # "credential_details.date_range": None,  # If model is right, GT should be null
    },
    "TD-004": {
        # These are normalization issues, not GT errors
        # Should update test harness to handle these cases
    }
}

NORMALIZATION_IMPROVEMENTS = {
    "professional_designation": {
        "aliases": ["MD", "MEDICAL DOCTOR", "Doctor of Medicine"],
        "canonical": "MD"
    },
    "jurisdiction": {
        "aliases": ["Missouri", "MO"],
        "canonical": "MO"  # Use 2-letter state code
    },
}

def main():
    print("="*80)
    print("HIGH-ACCURACY DOCUMENT AUDIT")
    print("="*80)
    print()

    print("SUMMARY:")
    print(f"  TD-001: 100% accuracy - PERFECT (gold standard)")
    print(f"  TD-003: 80% accuracy - 2 potential issues (title, date_range)")
    print(f"  TD-004: 63.6% accuracy - 4 normalization issues")
    print()

    print("="*80)
    print("FINDINGS")
    print("="*80)
    print()

    print("1. TD-001 is PERFECT - use as reference for GT validation")
    print()

    print("2. TD-003 has 2 mismatches:")
    print("   - title: GT says 'UpToDate', model says null")
    print("   - date_range: GT says 'May 29, 2024 - May 29, 2024', model says null")
    print("   ACTION: Verify these fields on actual document")
    print()

    print("3. TD-004 has 4 normalization issues (not GT errors):")
    print("   - 'MD' vs 'MEDICAL DOCTOR' - need fuzzy match")
    print("   - 'Missouri' vs 'MO' - need state code normalization")
    print("   - issue_date missing - need to check document")
    print("   - issuing_authority word order - need fuzzy match")
    print("   ACTION: Improve normalization, not GT")
    print()

    print("="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    print()

    print("Option 1: QUICK WINS (30 min)")
    print("  - Fix TD-003 if model is right (2 fields)")
    print("  - Add TD-004 issue_date if visible (1 field)")
    print("  - Expected gain: +1-2 pp")
    print()

    print("Option 2: NORMALIZATION IMPROVEMENTS (2-3 hours)")
    print("  - Add professional_designation aliases (MD, MEDICAL DOCTOR, etc.)")
    print("  - Improve jurisdiction matching (state name <-> code)")
    print("  - Improve issuing_authority fuzzy matching")
    print("  - Expected gain: +3-5 pp")
    print()

    print("Option 3: COMPREHENSIVE AUDIT (4-6 hours)")
    print("  - Manually review ALL remaining docs against source PDFs")
    print("  - Fix any hidden GT errors")
    print("  - Improve all normalization rules")
    print("  - Expected gain: +5-8 pp")
    print()

    print("="*80)
    print("RECOMMENDED NEXT STEP")
    print("="*80)
    print()
    print("Since we're targeting 72-75% (need +5-8 pp from current 67-70%):")
    print()
    print("Best approach: Option 2 (Normalization Improvements)")
    print("  - Fastest path to 72-75%")
    print("  - Improves system quality overall")
    print("  - Doesn't require manual document review")
    print()
    print("Implementation:")
    print("  1. Add fuzzy matching for professional_designation")
    print("  2. Add state code normalization for jurisdiction")
    print("  3. Improve issuing_authority matching")
    print("  4. Test and measure improvement")
    print()

if __name__ == "__main__":
    main()
