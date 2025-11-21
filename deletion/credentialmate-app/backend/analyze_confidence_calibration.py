#!/usr/bin/env python3
"""
Confidence Calibration Analysis Script

Analyzes whether AI confidence scores are calibrated with actual accuracy.
Critical for Phase 2 Session 1 - Confidence Scoring & Field-Level Accuracy Tracking.

Expected Behavior:
- If AI says 90% confident → should be correct ~90% of the time
- If AI says 70% confident → should be correct ~70% of the time

Calibration Issues:
- Over-confident: High confidence but low accuracy (model thinks it's right but it's wrong)
- Under-confident: Low confidence but high accuracy (model uncertain but actually correct)

Author: Claude Code
Session: Phase 2, Session 1
"""

import sys
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from sqlalchemy import func, case

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal
from app.models.field_accuracy_log import FieldAccuracyLog


def analyze_calibration_overall() -> Dict:
    """
    Analyze overall confidence calibration across all fields.

    Returns:
        Dict with calibration metrics by confidence bucket
    """
    db = SessionLocal()

    try:
        # Query: Group by confidence bucket, calculate accuracy
        results = db.query(
            FieldAccuracyLog.confidence_bucket,
            func.count(FieldAccuracyLog.id).label('total_count'),
            func.sum(case((FieldAccuracyLog.is_correct == True, 1), else_=0)).label('correct_count'),
            func.avg(FieldAccuracyLog.confidence_score).label('avg_confidence')
        ).filter(
            FieldAccuracyLog.confidence_bucket.isnot(None)
        ).group_by(
            FieldAccuracyLog.confidence_bucket
        ).all()

        calibration_by_bucket = {}
        for row in results:
            bucket = row.confidence_bucket
            total = row.total_count
            correct = row.correct_count
            avg_conf = row.avg_confidence

            accuracy = (correct / total * 100) if total > 0 else 0

            calibration_by_bucket[bucket] = {
                'total_fields': total,
                'correct_fields': correct,
                'accuracy_pct': round(accuracy, 1),
                'avg_confidence': round(avg_conf, 3) if avg_conf else None,
                'calibration_gap': round(avg_conf * 100 - accuracy, 1) if avg_conf else None
            }

        return calibration_by_bucket

    finally:
        db.close()


def analyze_calibration_by_field() -> Dict:
    """
    Analyze confidence calibration per field type.

    Identifies which fields are well-calibrated vs poorly calibrated.

    Returns:
        Dict mapping field_name → calibration metrics by bucket
    """
    db = SessionLocal()

    try:
        results = db.query(
            FieldAccuracyLog.field_name,
            FieldAccuracyLog.confidence_bucket,
            func.count(FieldAccuracyLog.id).label('total_count'),
            func.sum(case((FieldAccuracyLog.is_correct == True, 1), else_=0)).label('correct_count'),
            func.avg(FieldAccuracyLog.confidence_score).label('avg_confidence')
        ).filter(
            FieldAccuracyLog.confidence_bucket.isnot(None)
        ).group_by(
            FieldAccuracyLog.field_name,
            FieldAccuracyLog.confidence_bucket
        ).order_by(
            FieldAccuracyLog.field_name,
            FieldAccuracyLog.confidence_bucket
        ).all()

        calibration_by_field = {}
        for row in results:
            field_name = row.field_name
            bucket = row.confidence_bucket
            total = row.total_count
            correct = row.correct_count
            avg_conf = row.avg_confidence

            accuracy = (correct / total * 100) if total > 0 else 0

            if field_name not in calibration_by_field:
                calibration_by_field[field_name] = {}

            calibration_by_field[field_name][bucket] = {
                'total': total,
                'correct': correct,
                'accuracy_pct': round(accuracy, 1),
                'avg_confidence': round(avg_conf, 3) if avg_conf else None,
                'calibration_gap': round(avg_conf * 100 - accuracy, 1) if avg_conf else None
            }

        return calibration_by_field

    finally:
        db.close()


def identify_problem_fields() -> List[Dict]:
    """
    Identify fields with poor calibration (over/under-confident).

    Returns:
        List of problem fields with recommendations
    """
    db = SessionLocal()

    try:
        # Query: Fields with high confidence but low accuracy (over-confident)
        over_confident = db.query(
            FieldAccuracyLog.field_name,
            func.count(FieldAccuracyLog.id).label('total_count'),
            func.sum(case((FieldAccuracyLog.is_correct == True, 1), else_=0)).label('correct_count'),
            func.avg(FieldAccuracyLog.confidence_score).label('avg_confidence')
        ).filter(
            FieldAccuracyLog.confidence_bucket == 'high'  # High confidence
        ).group_by(
            FieldAccuracyLog.field_name
        ).having(
            func.avg(FieldAccuracyLog.confidence_score) >= 0.85
        ).all()

        problems = []

        for row in over_confident:
            field_name = row.field_name
            total = row.total_count
            correct = row.correct_count
            avg_conf = row.avg_confidence

            accuracy = (correct / total * 100) if total > 0 else 0
            calibration_gap = (avg_conf * 100 - accuracy) if avg_conf else 0

            # Flag if calibration gap > 10% (e.g., 90% confident but only 75% accurate)
            if calibration_gap > 10:
                problems.append({
                    'field_name': field_name,
                    'issue': 'over-confident',
                    'avg_confidence': round(avg_conf, 3),
                    'actual_accuracy': round(accuracy, 1),
                    'calibration_gap': round(calibration_gap, 1),
                    'sample_size': total,
                    'recommendation': f'Lower confidence threshold or improve extraction for {field_name}'
                })

        return problems

    finally:
        db.close()


def generate_calibration_report() -> str:
    """
    Generate comprehensive calibration report in Markdown format.

    Returns:
        Markdown-formatted report
    """
    report_lines = [
        "# Confidence Calibration Analysis Report",
        "",
        f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
        "---",
        "",
        "## Overall Calibration by Confidence Bucket",
        ""
    ]

    # Overall calibration
    overall = analyze_calibration_overall()

    report_lines.append("| Confidence Bucket | Total Fields | Accuracy | Avg Confidence | Calibration Gap |")
    report_lines.append("|-------------------|--------------|----------|----------------|-----------------|")

    for bucket in ['high', 'medium', 'low']:
        if bucket in overall:
            data = overall[bucket]
            bucket_label = f"{bucket.capitalize()}"
            if bucket == 'high':
                bucket_label += " (≥0.85)"
            elif bucket == 'medium':
                bucket_label += " (0.70-0.84)"
            else:
                bucket_label += " (<0.70)"

            report_lines.append(
                f"| {bucket_label} | {data['total_fields']} | "
                f"{data['accuracy_pct']}% | {data['avg_confidence']} | "
                f"{data['calibration_gap']:+.1f}% |"
            )

    report_lines.extend([
        "",
        "**Calibration Gap Interpretation:**",
        "- **Positive gap** (e.g., +10%): Model is over-confident (says 90% but only 80% accurate)",
        "- **Negative gap** (e.g., -10%): Model is under-confident (says 70% but actually 80% accurate)",
        "- **Near zero** (±5%): Well-calibrated",
        "",
        "---",
        "",
        "## Calibration by Field Type",
        ""
    ])

    # Per-field calibration
    by_field = analyze_calibration_by_field()

    for field_name, buckets in sorted(by_field.items()):
        report_lines.append(f"### {field_name}")
        report_lines.append("")
        report_lines.append("| Bucket | Total | Accuracy | Avg Confidence | Calibration Gap |")
        report_lines.append("|--------|-------|----------|----------------|-----------------|")

        for bucket in ['high', 'medium', 'low']:
            if bucket in buckets:
                data = buckets[bucket]
                report_lines.append(
                    f"| {bucket} | {data['total']} | {data['accuracy_pct']}% | "
                    f"{data['avg_confidence']} | {data['calibration_gap']:+.1f}% |"
                )

        report_lines.append("")

    report_lines.extend([
        "---",
        "",
        "## Problem Fields (Poorly Calibrated)",
        ""
    ])

    # Problem fields
    problems = identify_problem_fields()

    if problems:
        report_lines.append("| Field | Issue | Avg Confidence | Actual Accuracy | Gap | Recommendation |")
        report_lines.append("|-------|-------|----------------|-----------------|-----|----------------|")

        for problem in problems:
            report_lines.append(
                f"| {problem['field_name']} | {problem['issue']} | "
                f"{problem['avg_confidence']} | {problem['actual_accuracy']}% | "
                f"{problem['calibration_gap']:+.1f}% | {problem['recommendation']} |"
            )
    else:
        report_lines.append("✅ No significant calibration issues detected!")

    report_lines.extend([
        "",
        "---",
        "",
        "## Production Recommendations",
        "",
        "Based on this calibration analysis:",
        ""
    ])

    # Generate recommendations based on calibration
    if overall.get('high', {}).get('accuracy_pct', 0) >= 90:
        report_lines.append("- ✅ **High-confidence fields (≥0.85)** can be auto-validated (>90% accurate)")
    else:
        report_lines.append("- ⚠️ **High-confidence fields** need review (accuracy below 90%)")

    if overall.get('medium', {}).get('accuracy_pct', 0) >= 75:
        report_lines.append("- ⚠️ **Medium-confidence fields (0.70-0.84)** should be flagged for user review")
    else:
        report_lines.append("- ❌ **Medium-confidence fields** require mandatory user validation")

    report_lines.append("- ❌ **Low-confidence fields (<0.70)** require mandatory user verification")

    return "\n".join(report_lines)


if __name__ == "__main__":
    print("Generating confidence calibration report...")
    print("=" * 60)

    try:
        report = generate_calibration_report()

        # Save to file - try multiple locations
        possible_dirs = [
            Path(__file__).parent.parent / "docs/ux-ui/outputs",
            Path("/app"),
        ]

        output_file = None
        for output_dir in possible_dirs:
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
                output_file = output_dir / "SESSION-2-1-CALIBRATION-ANALYSIS.md"
                with open(output_file, 'w') as f:
                    f.write(report)
                break
            except (PermissionError, FileNotFoundError):
                continue

        if output_file:
            print(f"✅ Report saved to {output_file}")
        else:
            print("⚠️ Could not save report to file, printing to console only")

        print("=" * 60)

        # Also print to console
        print("\n" + report)

    except Exception as e:
        print(f"❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
