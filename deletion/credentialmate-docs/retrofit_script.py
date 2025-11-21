#!/usr/bin/env python3
"""
FNSP v1.0 Retrofit Script for credentialmate-docs
- Add SOC2 headers to all Markdown, JSON, YAML, and text files
- Rename files to FNSP v1.0 format: <category>_<topic>_v<version>.md
- Update internal links to reflect renamed files
"""

import os
import re
from datetime import datetime
from pathlib import Path

# Constants
BASE_DIR = "/home/user/credentialmate-docs"
TIMESTAMP = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

# Approved categories
CATEGORIES = {
    'spec': 'Specification',
    'design': 'Design/Architecture',
    'guide': 'Guide/How-to',
    'ops': 'Operations/Runbook',
    'pm': 'Project Management',
    'diag': 'Diagnostics/Troubleshooting'
}

# Directory to category mapping
DIR_TO_CATEGORY = {
    'specifications': 'spec',
    'architecture': 'design',
    'guides': 'guide',
    'runbooks': 'ops',
    'tracking': 'pm',
    'governance': 'pm',
    'compliance': 'spec',
    'api': 'spec',
    'adr': 'design',
    'issues': 'diag',
    'qa': 'guide',
    '.github': 'ops',
    'docs': 'guide',
}

# SOC2 Header Templates
def get_soc2_header_md(category, purpose):
    """Generate SOC2 header for Markdown files."""
    return f"""<!--
TIMESTAMP: {TIMESTAMP}
CLASSIFICATION: SOC2 Type II - {CATEGORIES.get(category, 'Documentation')}
COMPLIANCE: SOC2 CC1.1, CC1.2, CC2.1 - Documentation Controls
ORIGIN: credentialmate-docs
PURPOSE: {purpose}
VERSION: v1.0
-->

"""

def get_soc2_header_yaml(category, purpose):
    """Generate SOC2 header for YAML files."""
    return f"""# TIMESTAMP: {TIMESTAMP}
# CLASSIFICATION: SOC2 Type II - {CATEGORIES.get(category, 'Documentation')}
# COMPLIANCE: SOC2 CC1.1, CC1.2, CC2.1 - Documentation Controls
# ORIGIN: credentialmate-docs
# PURPOSE: {purpose}
# VERSION: v1.0

"""

def get_soc2_header_txt(category, purpose):
    """Generate SOC2 header for text files."""
    return f"""# TIMESTAMP: {TIMESTAMP}
# CLASSIFICATION: SOC2 Type II - {CATEGORIES.get(category, 'Documentation')}
# COMPLIANCE: SOC2 CC1.1, CC1.2, CC2.1 - Documentation Controls
# ORIGIN: credentialmate-docs
# PURPOSE: {purpose}
# VERSION: v1.0

"""

def convert_to_fnsp_name(filename, category):
    """Convert filename to FNSP v1.0 format: <category>_<topic>_v<version>.ext"""
    name, ext = os.path.splitext(filename)

    # Check if already versioned
    version_match = re.search(r'_v(\d+(?:\.\d+)?)$', name)
    if version_match:
        version = version_match.group(1)
        name = name[:version_match.start()]
    else:
        version = "1.0"

    # Step 1: Replace underscores with hyphens
    topic = name.replace('_', '-')

    # Step 2: Handle CamelCase by inserting hyphens at word boundaries
    # Insert hyphen before uppercase letter that follows lowercase letter
    topic = re.sub(r'([a-z])([A-Z])', r'\1-\2', topic)
    # Insert hyphen before lowercase letter that follows uppercase letters (except first)
    topic = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1-\2', topic)

    # Step 3: Convert to lowercase
    topic = topic.lower()

    # Step 4: Clean up multiple hyphens
    topic = re.sub(r'-+', '-', topic)

    # Step 5: Remove leading/trailing hyphens
    topic = topic.strip('-')

    # Build new filename
    new_name = f"{category}_{topic}_v{version}{ext}"

    return new_name

def remove_existing_header(content, file_ext):
    """Remove existing SOC2-style header from content."""
    if file_ext == '.md':
        # Remove HTML comment header at start
        match = re.match(r'^<!--[\s\S]*?-->\s*', content)
        if match and 'TIMESTAMP:' in match.group(0):
            return content[match.end():]
    elif file_ext in ['.yaml', '.yml', '.txt']:
        # Remove comment lines at start that look like header
        lines = content.split('\n')
        start_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('#') and any(k in line for k in ['TIMESTAMP:', 'ORIGIN:', 'CLASSIFICATION:', 'COMPLIANCE:', 'PURPOSE:', 'VERSION:', 'UPDATED_FOR:']):
                start_idx = i + 1
            elif line.strip() == '':
                continue
            else:
                break
        return '\n'.join(lines[start_idx:]).lstrip('\n')
    return content

def get_purpose_from_content(content, filename):
    """Extract purpose from content or generate from filename."""
    # Try to find first heading
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip('*').strip()

    # Fallback to filename-based purpose
    name = os.path.splitext(filename)[0]
    name = name.replace('_', ' ').replace('-', ' ')
    return name.title()

def process_files():
    """Main function to process all files."""
    renamed_files = []
    added_headers = []
    skipped_files = []
    conflicts = []
    link_updates = {}

    # Files to skip (system files, the script itself)
    skip_patterns = [
        'retrofit_script.py',
        '.git',
        'node_modules',
        '__pycache__',
        '.pyc'
    ]

    # Collect all target files
    target_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        # Skip hidden directories except .github
        dirs[:] = [d for d in dirs if not d.startswith('.') or d == '.github']

        for filename in files:
            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, BASE_DIR)

            # Skip certain files
            if any(skip in rel_path for skip in skip_patterns):
                continue

            # Only process target file types
            ext = os.path.splitext(filename)[1].lower()
            if ext in ['.md', '.json', '.yaml', '.yml', '.txt']:
                target_files.append((filepath, rel_path, ext))

    # First pass: create rename mapping
    rename_map = {}  # old_path -> new_path

    for filepath, rel_path, ext in target_files:
        dirname = os.path.dirname(rel_path)
        filename = os.path.basename(rel_path)

        # Determine category based on directory
        if dirname:
            top_dir = dirname.split('/')[0]
            category = DIR_TO_CATEGORY.get(top_dir, 'spec')
        else:
            # Root level files - determine by name
            name_lower = filename.lower()
            if 'security' in name_lower:
                category = 'ops'
            elif 'readme' in name_lower:
                category = 'guide'
            elif 'checklist' in name_lower:
                category = 'ops'
            elif 'dashboard' in name_lower:
                category = 'pm'
            elif 'phase' in name_lower:
                category = 'pm'
            elif 'manifest' in name_lower:
                category = 'pm'
            elif 'auditor' in name_lower or 'evidence' in name_lower:
                category = 'spec'
            else:
                category = 'spec'

        # Special cases for certain files
        if filename == 'README.md':
            # Keep README files as guide_readme
            new_filename = f"guide_readme_v1.0{ext}"
        elif filename in ['mkdocs.yml', 'requirements.txt', '.agent-rules.yaml']:
            # Skip renaming config files
            new_filename = filename
            skipped_files.append({
                'file': rel_path,
                'reason': 'Configuration file - kept as-is'
            })
        elif filename.startswith('.'):
            # Skip hidden files
            new_filename = filename
            skipped_files.append({
                'file': rel_path,
                'reason': 'Hidden file - kept as-is'
            })
        else:
            new_filename = convert_to_fnsp_name(filename, category)

        new_rel_path = os.path.join(dirname, new_filename) if dirname else new_filename
        new_filepath = os.path.join(BASE_DIR, new_rel_path)

        if new_filepath != filepath:
            rename_map[rel_path] = new_rel_path

    # Check for naming conflicts
    new_paths = list(rename_map.values())
    duplicates = set([x for x in new_paths if new_paths.count(x) > 1])

    if duplicates:
        for dup in duplicates:
            originals = [k for k, v in rename_map.items() if v == dup]
            conflicts.append({
                'new_name': dup,
                'conflicting_files': originals
            })
            # Add suffix to resolve conflicts
            for i, orig in enumerate(originals[1:], 2):
                base, ext = os.path.splitext(dup)
                version_match = re.search(r'_v(\d+(?:\.\d+)?)$', base)
                if version_match:
                    base_no_ver = base[:version_match.start()]
                    version = version_match.group(1)
                    rename_map[orig] = f"{base_no_ver}-{i}_v{version}{ext}"
                else:
                    rename_map[orig] = f"{base}-{i}{ext}"

    # Second pass: add headers
    for filepath, rel_path, ext in target_files:
        filename = os.path.basename(filepath)
        dirname = os.path.dirname(rel_path)

        # Skip config files for header addition but still track
        if filename in ['mkdocs.yml', 'requirements.txt']:
            pass  # These get headers
        elif filename.startswith('.') and filename != '.agent-rules.yaml':
            continue

        # Read file content
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            skipped_files.append({
                'file': rel_path,
                'reason': f'Read error: {str(e)}'
            })
            continue

        # Determine category
        if dirname:
            top_dir = dirname.split('/')[0]
            category = DIR_TO_CATEGORY.get(top_dir, 'spec')
        else:
            if 'security' in filename.lower():
                category = 'ops'
            elif 'readme' in filename.lower():
                category = 'guide'
            else:
                category = 'spec'

        # Get purpose
        purpose = get_purpose_from_content(content, filename)

        # Remove existing header if present
        content = remove_existing_header(content, ext)

        # Add new SOC2 header
        if ext == '.md':
            header = get_soc2_header_md(category, purpose)
        elif ext in ['.yaml', '.yml']:
            header = get_soc2_header_yaml(category, purpose)
        elif ext == '.txt':
            header = get_soc2_header_txt(category, purpose)
        elif ext == '.json':
            skipped_files.append({
                'file': rel_path,
                'reason': 'JSON file - header not applicable'
            })
            continue
        else:
            continue

        new_content = header + content

        # Write updated content
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            added_headers.append(rel_path)
        except Exception as e:
            skipped_files.append({
                'file': rel_path,
                'reason': f'Write error: {str(e)}'
            })
            continue

    # Third pass: rename files
    rename_items = sorted(rename_map.items(), key=lambda x: x[0].count('/'), reverse=True)

    for old_rel_path, new_rel_path in rename_items:
        old_filepath = os.path.join(BASE_DIR, old_rel_path)
        new_filepath = os.path.join(BASE_DIR, new_rel_path)

        if old_filepath == new_filepath:
            continue

        try:
            if os.path.exists(new_filepath):
                skipped_files.append({
                    'file': old_rel_path,
                    'reason': f'Target already exists: {new_rel_path}'
                })
                continue

            os.rename(old_filepath, new_filepath)
            renamed_files.append({
                'old': old_rel_path,
                'new': new_rel_path
            })
            link_updates[old_rel_path] = new_rel_path
        except Exception as e:
            skipped_files.append({
                'file': old_rel_path,
                'reason': f'Rename error: {str(e)}'
            })

    # Fourth pass: update internal links
    link_update_count = 0
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if not d.startswith('.') or d == '.github']

        for filename in files:
            if not filename.endswith('.md'):
                continue

            filepath = os.path.join(root, filename)

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                original_content = content

                for old_path, new_path in link_updates.items():
                    old_filename = os.path.basename(old_path)
                    new_filename = os.path.basename(new_path)

                    content = content.replace(f']({old_filename})', f']({new_filename})')
                    content = content.replace(f'](./{old_filename})', f'](./{new_filename})')
                    content = content.replace(f'](../{old_path})', f'](../{new_path})')
                    content = content.replace(f']({old_path})', f']({new_path})')

                if content != original_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    link_update_count += 1

            except Exception:
                pass

    summary = {
        'total_files_processed': len(target_files),
        'headers_added': len(added_headers),
        'files_renamed': len(renamed_files),
        'files_skipped': len(skipped_files),
        'conflicts_resolved': len(conflicts),
        'links_updated': link_update_count,
        'renamed_files': renamed_files,
        'skipped_files': skipped_files,
        'conflicts': conflicts
    }

    return summary

if __name__ == '__main__':
    print("Starting FNSP v1.0 Retrofit...")
    print("=" * 50)

    summary = process_files()

    print(f"\n{'='*50}")
    print("RETROFIT SUMMARY")
    print(f"{'='*50}")
    print(f"Total files processed: {summary['total_files_processed']}")
    print(f"SOC2 headers added: {summary['headers_added']}")
    print(f"Files renamed: {summary['files_renamed']}")
    print(f"Files skipped: {summary['files_skipped']}")
    print(f"Conflicts resolved: {summary['conflicts_resolved']}")
    print(f"Links updated: {summary['links_updated']}")

    print(f"\n{'='*50}")
    print("RENAMED FILES (sample)")
    print(f"{'='*50}")
    for item in summary['renamed_files'][:30]:
        print(f"  {item['old']}")
        print(f"    -> {item['new']}")
    if len(summary['renamed_files']) > 30:
        print(f"  ... and {len(summary['renamed_files']) - 30} more files")

    print(f"\n{'='*50}")
    print("SKIPPED FILES")
    print(f"{'='*50}")
    for item in summary['skipped_files']:
        print(f"  {item['file']}: {item['reason']}")

    if summary['conflicts']:
        print(f"\n{'='*50}")
        print("CONFLICTS RESOLVED")
        print(f"{'='*50}")
        for item in summary['conflicts']:
            print(f"  {item['new_name']}")
            for orig in item['conflicting_files']:
                print(f"    <- {orig}")

    # Save summary to file
    summary_path = os.path.join(BASE_DIR, 'pm_retrofit-summary_v1.0.md')
    with open(summary_path, 'w') as f:
        f.write(f"""<!--
TIMESTAMP: {TIMESTAMP}
CLASSIFICATION: SOC2 Type II - Project Management
COMPLIANCE: SOC2 CC1.1, CC1.2, CC2.1 - Documentation Controls
ORIGIN: credentialmate-docs
PURPOSE: FNSP v1.0 Retrofit Summary
VERSION: v1.0
-->

# FNSP v1.0 Retrofit Summary

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Repository:** credentialmate-docs

## Summary

| Metric | Count |
|--------|-------|
| Total files processed | {summary['total_files_processed']} |
| SOC2 headers added | {summary['headers_added']} |
| Files renamed | {summary['files_renamed']} |
| Files skipped | {summary['files_skipped']} |
| Conflicts resolved | {summary['conflicts_resolved']} |
| Links updated | {summary['links_updated']} |

## Renamed Files

""")
        for item in summary['renamed_files']:
            f.write(f"- `{item['old']}` -> `{item['new']}`\n")

        f.write("\n## Skipped Files\n\n")
        for item in summary['skipped_files']:
            f.write(f"- `{item['file']}`: {item['reason']}\n")

        if summary['conflicts']:
            f.write("\n## Conflicts Resolved\n\n")
            for item in summary['conflicts']:
                f.write(f"### {item['new_name']}\n")
                for orig in item['conflicting_files']:
                    f.write(f"- `{orig}`\n")

    print(f"\nSummary saved to: {summary_path}")
    print("\nRetrofit complete!")
