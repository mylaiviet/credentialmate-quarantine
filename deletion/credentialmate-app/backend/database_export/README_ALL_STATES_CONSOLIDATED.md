# TIMESTAMP: 2025-11-20T20:39:15Z
# CLASSIFICATION: SOC2 Type II - User Documentation
# COMPLIANCE: HIPAA, SOC2
# ORIGIN: credentialmate-app
# PURPOSE: Repository documentation and quick start guide

# Consolidated State CME Requirements Export - All 50 States + Territories

**Generated:** 2025-11-19
**Source:** FSMB CME Requirements by State (October 2025)
**Script:** `backend/app/scripts/export_state_requirements_md_do_consolidated.py`

## Overview

This CSV file contains **all state-level CME requirements for MD and DO providers** across all 50 states and U.S. territories, consolidated into a single denormalized view with 39 columns.

## File

**`state_requirements_ALL_STATES_CONSOLIDATED.csv`**

- **Total Rows:** 67 requirements (1 header + 67 data rows)
- **Total Columns:** 39 comprehensive data columns
- **States Covered:** 55 unique states/territories
- **Provider Types:** MD-specific, DO-specific, or Both (BOTH)

## Coverage Breakdown

### State/Territory Distribution

- **States with separate MD/DO boards:** 12 states
  - Arizona, California, Florida, Maine, Michigan, Nevada, Oklahoma, Pennsylvania, Tennessee, Vermont, West Virginia, New Jersey
  - Each has 2 separate requirements (one for MD board, one for DO board)

- **States with combined MD/DO requirements:** 43 states + territories
  - Single board governing both MD and DO providers
  - Requirements apply to BOTH provider types

### Requirement Types

- **MD-specific requirements:** 12 (separate MD boards)
- **DO-specific requirements:** 12 (separate DO boards)
- **Combined MD/DO requirements:** 43 (applies to BOTH)
- **Total requirements:** 67

## Data Structure

### Core Columns (39 total)

#### 1. Base Requirement Identifiers (5 columns)
- `base_requirement_id` - UUID of the requirement
- `state_code` - State/territory code (e.g., "CA-M", "CA-O", "AK")
- `state_name` - Full state/territory name
- `board_type` - MEDICAL, OSTEOPATHIC, or COMBINED
- `provider_type` - MD, DO, or BOTH

#### 2. CME Hour Requirements (5 columns)
- `substantial_cme_required` - Boolean: whether state requires substantial CME
- `cme_equivalent_accepted` - Boolean: whether MOC or other equivalents accepted
- `total_hours_required` - Total CME hours per renewal cycle
- `renewal_period_months` - Renewal cycle in months (12, 24, 36, or 48)
- `hours_per_year_equivalent` - Calculated annual hour requirement

#### 3. Category Requirements (3 columns)
- `min_category1_hours` - Minimum Category 1/1A hours required
- `category1_percentage` - Percentage of total that must be Category 1
- `max_category2_hours` - Maximum Category 2 hours allowed

#### 4. Rollover Policy (2 columns)
- `rollover_allowed` - Boolean: whether excess hours can roll over
- `max_rollover_hours` - Maximum hours that can be rolled over

#### 5. Accreditation (1 column)
- `accreditation_required` - Required accreditation bodies (AMA, AOA, etc.)

#### 6. Legal References (5 columns)
- `base_effective_date` - When requirement became effective
- `base_last_updated` - Last update to requirement
- `base_statute_citation` - Legal reference (statute, regulation, etc.)
- `board_guidance_url` - URL to official board guidance
- `base_notes` - Additional context, exemptions, edge cases

#### 7. State Board Contact (7 columns)
- `board_name` - Official board name
- `board_abbreviation` - Board acronym
- `board_website_url` - Main board website
- `board_cme_guidance_url` - CME-specific guidance page
- `board_contact_email` - Contact email
- `board_phone` - Contact phone number
- `board_last_verified` - Last verification date

#### 8. Content-Specific Requirements - AGGREGATED (3 columns)
- `content_specific_count` - Number of content-specific requirements
- `content_topics` - Semicolon-separated list of topics
- `content_requirements_summary` - Pipe-separated summaries of each requirement

**Content Topics Include:**
- Opioid prescribing
- Pain management
- Professional boundaries
- Ethics
- Cultural competency

#### 9. Exemptions - AGGREGATED (3 columns)
- `exemptions_count` - Number of exemptions available
- `exemption_types` - Semicolon-separated list of exemption types
- `exemptions_summary` - Pipe-separated summaries of each exemption

**Exemption Types Include:**
- Board certification (ABMS, AOA)
- Maintenance of Certification (MOC)
- Other equivalents

#### 10. Special Population Requirements - AGGREGATED (3 columns)
- `special_population_count` - Number of special population requirements
- `special_population_topics` - Semicolon-separated list of topics
- `special_population_summary` - Pipe-separated summaries

**Special Population Topics:**
- Geriatric medicine
- Pediatric care
- Other specialty-specific requirements

#### 11. Timestamps (2 columns)
- `base_created_at` - Record creation timestamp
- `base_updated_at` - Last update timestamp

## Key Statistics

### Content-Specific Requirements
- **States with content-specific requirements:** 8
- **Most common topics:**
  - Opioid prescribing: 6 states
  - Pain management: 2 states
  - Professional boundaries: 1 state

### Exemptions
- **States offering exemptions:** 3
- **All exemption types:** Board certification-related (ABMS, AOA, RCPSC)

### Rollover Policies
- **States allowing rollover:** 4
- **Most states:** Do not allow hour rollover

### Renewal Periods
- **Annual (12 months):** Most common
- **Biennial (24 months):** Second most common
- **Triennial (36 months):** Some states
- **Quadrennial (48 months):** Rare

## Data Quality Notes

- All data extracted from official FSMB CME Requirements by State document (October 2025)
- State-level regulatory requirements, NOT provider-specific compliance data
- Dates in ISO format (YYYY-MM-DD)
- Decimal values (hours, percentages) as floats
- Empty/NULL values appear as blank cells
- Multi-line content and special characters preserved
- Aggregated fields use delimiters:
  - Semicolon (`;`) for lists
  - Pipe (`|`) for detailed summaries

## Usage

### Regenerate Export

```bash
# Run seeding script first (if needed)
docker exec credentialmate-backend python -m app.scripts.seed_all_50_states_cme

# Run export script
docker exec credentialmate-backend python -m app.scripts.export_state_requirements_md_do_consolidated

# Copy from Docker container
docker cp credentialmate-backend:/tmp/state_requirements_md_do_CONSOLIDATED.csv backend/database_export/state_requirements_ALL_STATES_CONSOLIDATED.csv
```

### Example Queries

**Find states requiring opioid CME:**
```bash
grep -i "opioid" state_requirements_ALL_STATES_CONSOLIDATED.csv
```

**Find states allowing rollover:**
```bash
grep ",True," state_requirements_ALL_STATES_CONSOLIDATED.csv | grep "rollover_allowed"
```

**Count MD-only vs DO-only vs BOTH:**
```bash
cut -d',' -f5 state_requirements_ALL_STATES_CONSOLIDATED.csv | sort | uniq -c
```

## Important Notes

1. **State Requirements vs Provider Compliance**
   - This data represents STATE REGULATORY REQUIREMENTS
   - Not individual provider compliance tracking
   - Use this for understanding what states require, not what providers have completed

2. **MD/DO Split States**
   - 12 states have separate medical and osteopathic boards
   - These states have 2 rows each (one for MD, one for DO)
   - State codes use suffixes: "-M" for MD board, "-O" for DO board
   - Example: "CA-M" (California Medical Board), "CA-O" (California Osteopathic Board)

3. **Aggregated Data**
   - Content-specific, exemptions, and special population data are AGGREGATED
   - Full details available in separate normalized tables in database
   - Summaries provide quick overview without joining multiple tables

4. **Conditional Requirements**
   - Many content-specific requirements are conditional
   - Example: Opioid CME only required if provider has DEA registration
   - Check `content_requirements_summary` for conditional details

## Database Schema

This export draws from 5 database tables:

1. `state_cme_base_requirements` - Core hour requirements
2. `content_specific_cme` - Topic-specific CME (opioid, ethics, etc.)
3. `exemptions_equivalents` - Board certification and MOC exemptions
4. `special_population_requirements` - Specialty/population-based requirements
5. `state_board_contacts` - Board contact information

All tables joined and denormalized into single CSV for easy analysis.

---

**For questions or to report data discrepancies, contact the CredentialMate development team.**
