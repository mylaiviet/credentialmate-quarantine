import json
import csv
from datetime import datetime, timedelta
from collections import defaultdict
import os
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load the auto_issues_log.jsonl
log_file = r"c:\CREDENTIALMATE-REBUILD\credentialmate\credentialmate-app\credentialmate-docs\issues\auto_issues_log.jsonl"
issues = []

with open(log_file, 'r') as f:
    for line in f:
        if line.strip():
            issues.append(json.loads(line))

# Get current time and 4 hours ago
now = datetime.fromisoformat("2025-11-16T23:59:00Z")
four_hours_ago = now - timedelta(hours=4)

# Filter issues from last 4 hours
recent_issues = [i for i in issues if datetime.fromisoformat(i['created_at']) >= four_hours_ago]

# Categorize by status
new_issues = [i for i in recent_issues if i['status'] == 'NEW']
fixed_issues = [i for i in issues if i['status'] == 'FIXED' and datetime.fromisoformat(i['updated_at']) >= four_hours_ago]
active_issues = [i for i in recent_issues if i['status'] in ['NEW', 'TRIAGED']]
regression_issues = [i for i in issues if i['status'] == 'REGRESSION']
in_progress_issues = [i for i in issues if i['status'] == 'IN_PROGRESS']

# Filter for HIGH/CRITICAL only
critical_new = [i for i in new_issues if i['severity'] in ['HIGH', 'CRITICAL']]
critical_fixed = [i for i in fixed_issues if i['severity'] in ['HIGH', 'CRITICAL']]
critical_active = [i for i in active_issues if i['severity'] in ['HIGH', 'CRITICAL']]

# Analyze patterns
patterns = defaultdict(int)
for issue in issues:
    if 'pattern_id' in issue:
        patterns[issue['pattern_id']] += 1

print("=" * 90)
print("AUTO-ISSUES ENGINE DASHBOARD REPORT")
print("=" * 90)
print(f"Report Generated: {now.isoformat()}Z")
print(f"Analysis Period: Last 4 hours ({four_hours_ago.isoformat()}Z to {now.isoformat()}Z)")
print()

# SUMMARY TABLE
print("EXECUTIVE SUMMARY")
print("-" * 90)
print(f"Total NEW Issues (CRITICAL/HIGH):        {len(critical_new):>3}")
print(f"Total FIXED Issues (CRITICAL/HIGH):      {len(critical_fixed):>3}")
print(f"Active CRITICAL Issues (NEW/TRIAGED):    {len([i for i in critical_active if i['severity']=='CRITICAL']):>3}")
print(f"Regression Detectors Triggered:          {len(regression_issues):>3}")
print(f"In-Progress Issues:                      {len(in_progress_issues):>3}")
print(f"Total Issues in Log:                     {len(issues):>3}")
print()

# NEW ISSUES TABLE
if critical_new:
    print("NEW CRITICAL/HIGH SEVERITY ISSUES")
    print("-" * 90)
    print(f"{'ID':<10} {'Severity':<10} {'Component':<30} {'Issue Title':<40}")
    print("-" * 90)
    for i, issue in enumerate(critical_new[:8]):
        severity = issue['severity'][:10]
        comp = issue['component'][:29]
        title = issue['title'][:39]
        print(f"{issue['issue_id']:<10} {severity:<10} {comp:<30} {title:<40}")
    print()

# FIXED ISSUES TABLE
if critical_fixed:
    print("FIXED CRITICAL/HIGH SEVERITY ISSUES (Last 4hrs)")
    print("-" * 90)
    print(f"{'ID':<10} {'Component':<30} {'Fix Time':<12} {'Commit':<20}")
    print("-" * 90)
    for issue in critical_fixed[:6]:
        comp = issue['component'][:29]
        fix_time = str(issue.get('fix_time_minutes', 'N/A'))[:11]
        commit = issue.get('fix_commit', 'N/A')[:19]
        print(f"{issue['issue_id']:<10} {comp:<30} {fix_time:<12} {commit:<20}")
    print()

# REGRESSION ISSUES
if regression_issues:
    print("REGRESSION DETECTORS TRIGGERED")
    print("-" * 90)
    print(f"{'ID':<10} {'Original':<15} {'Component':<25} {'Score':<7} {'Status':<15}")
    print("-" * 90)
    for issue in regression_issues:
        orig = issue.get('original_issue_id', 'N/A')[:14]
        comp = issue['component'][:24]
        score = str(issue.get('regression_score', 'N/A'))[:6]
        status = issue['status'][:14]
        print(f"{issue['issue_id']:<10} {orig:<15} {comp:<25} {score:<7} {status:<15}")
    print()

# PATTERN ANALYSIS
if patterns:
    print("DETECTED PATTERNS & ISSUE CLUSTERS")
    print("-" * 90)
    print(f"{'Pattern ID':<35} {'Count':<8} {'Severity':<15} {'Impact':<15}")
    print("-" * 90)
    pattern_list = sorted(patterns.items(), key=lambda x: x[1], reverse=True)
    for pattern_id, count in pattern_list[:6]:
        pattern_issues = [i for i in issues if i.get('pattern_id') == pattern_id]
        severity = pattern_issues[0]['severity'] if pattern_issues else 'N/A'
        impact = "Critical" if severity == "CRITICAL" else "High" if severity == "HIGH" else "Medium"
        print(f"{pattern_id:<35} {count:<8} {severity:<15} {impact:<15}")
    print()

# COMPONENT VULNERABILITY HEAT MAP
print("COMPONENT VULNERABILITY HEAT MAP")
print("-" * 90)
component_issues = defaultdict(lambda: {"critical": 0, "high": 0})
for issue in issues:
    comp = issue['component']
    if issue['severity'] == 'CRITICAL':
        component_issues[comp]['critical'] += 1
    elif issue['severity'] == 'HIGH':
        component_issues[comp]['high'] += 1

print(f"{'Component':<35} {'CRITICAL':<10} {'HIGH':<6} {'Risk Level':<18}")
print("-" * 90)
for comp in sorted(component_issues.keys()):
    crit = component_issues[comp]['critical']
    high = component_issues[comp]['high']
    risk = "[CRITICAL]" if crit > 0 else "[HIGH]" if high > 0 else "[MEDIUM]"
    comp_str = comp[:34]
    print(f"{comp_str:<35} {crit:<10} {high:<6} {risk:<18}")
print()

print("=" * 90)
print("DETAILED ISSUE BREAKDOWN")
print("=" * 90)
print()

# Detailed listing
all_statuses = ["NEW", "TRIAGED", "IN_PROGRESS", "FIXED", "REGRESSION"]
for status in all_statuses:
    status_issues = [i for i in issues if i['status'] == status]
    if status_issues and status in ["NEW", "FIXED", "REGRESSION"]:
        print(f"\n[{status}] - {len(status_issues)} issue(s)")
        print("-" * 90)
        for issue in status_issues:
            print(f"  ID: {issue['issue_id']} | {issue['severity']:8} | {issue['title']}")
            print(f"     Component: {issue['component']}")
            print(f"     Pattern: {issue.get('pattern_id', 'N/A')} | Created: {issue['created_at']}")
            if issue['status'] == 'FIXED':
                print(f"     Fixed in: {issue.get('fix_time_minutes', 'N/A')} minutes | Commit: {issue.get('fix_commit', 'N/A')}")
            print()

print("=" * 90)
print("STATISTICS & METRICS")
print("=" * 90)
print()
print(f"Total Issues Analyzed:              {len(issues)}")
print(f"New Issues (Last 4 hours):          {len(critical_new)}")
print(f"Fixed Issues (Last 4 hours):        {len(critical_fixed)}")
print(f"Active Critical Issues:             {len([i for i in critical_active if i['severity']=='CRITICAL'])}")
print(f"Regressions Detected:               {len(regression_issues)}")
if critical_fixed:
    avg_fix_time = sum([i.get('fix_time_minutes', 0) for i in critical_fixed]) / len(critical_fixed)
    print(f"Average Fix Time:                   {avg_fix_time:.1f} minutes")
print(f"Total Unique Patterns:              {len(patterns)}")
if pattern_list:
    print(f"Most Common Pattern:                {pattern_list[0][0]} ({pattern_list[0][1]} issues)")
print()

# Generate CSV exports
print("=" * 90)
print("CSV EXPORTS GENERATED")
print("=" * 90)

csv_dir = r"c:\CREDENTIALMATE-REBUILD\credentialmate\credentialmate-app\credentialmate-docs\issues"

# All issues CSV
csv_file = os.path.join(csv_dir, "auto_issues_export.csv")
with open(csv_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Issue ID', 'Type', 'Severity', 'Status', 'Title', 'Component', 'Pattern ID', 'Created At', 'Updated At', 'Detected By', 'Tags'])
    for issue in issues:
        writer.writerow([
            issue['issue_id'],
            issue['type'],
            issue['severity'],
            issue['status'],
            issue['title'],
            issue['component'],
            issue.get('pattern_id', ''),
            issue['created_at'],
            issue['updated_at'],
            issue['detected_by'],
            ', '.join(issue.get('tags', []))
        ])
print(f"✓ Generated: auto_issues_export.csv ({len(issues)} records)")

# NEW issues only CSV
csv_file_new = os.path.join(csv_dir, "auto_issues_new.csv")
with open(csv_file_new, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Issue ID', 'Severity', 'Title', 'Component', 'Pattern ID', 'Created At', 'Detected By'])
    for issue in critical_new:
        writer.writerow([
            issue['issue_id'],
            issue['severity'],
            issue['title'],
            issue['component'],
            issue.get('pattern_id', ''),
            issue['created_at'],
            issue['detected_by']
        ])
print(f"✓ Generated: auto_issues_new.csv ({len(critical_new)} records)")

# FIXED issues CSV
csv_file_fixed = os.path.join(csv_dir, "auto_issues_fixed.csv")
with open(csv_file_fixed, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Issue ID', 'Severity', 'Title', 'Component', 'Fix Time (min)', 'Commit', 'Fixed At'])
    for issue in critical_fixed:
        writer.writerow([
            issue['issue_id'],
            issue['severity'],
            issue['title'],
            issue['component'],
            issue.get('fix_time_minutes', ''),
            issue.get('fix_commit', ''),
            issue['updated_at']
        ])
print(f"✓ Generated: auto_issues_fixed.csv ({len(critical_fixed)} records)")

# Regressions CSV
csv_file_regr = os.path.join(csv_dir, "auto_issues_regressions.csv")
with open(csv_file_regr, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Issue ID', 'Severity', 'Title', 'Component', 'Original Issue', 'Regression Score', 'Detected At'])
    for issue in regression_issues:
        writer.writerow([
            issue['issue_id'],
            issue['severity'],
            issue['title'],
            issue['component'],
            issue.get('original_issue_id', ''),
            issue.get('regression_score', ''),
            issue['created_at']
        ])
print(f"✓ Generated: auto_issues_regressions.csv ({len(regression_issues)} records)")

print()
print("=" * 90)
print("REPORT COMPLETE")
print("=" * 90)
