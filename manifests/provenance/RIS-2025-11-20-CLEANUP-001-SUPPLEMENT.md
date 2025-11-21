# TIMESTAMP: 2025-11-20T00:00:00Z
# ORIGIN: credentialmate-ai
# UPDATED_FOR: credentialmate-ai
# PURPOSE: Supplemental cleanup plan for missing needs-review files
# VERSION: v1.0
# PLAN_ID: RIS-2025-11-20-CLEANUP-001-SUPPLEMENT
# PARENT_PLAN: RIS-2025-11-20-CLEANUP-001

# SUPPLEMENTAL NEEDS-REVIEW CLEANUP PLAN
Generated: 2025-11-20
Mode: PLAN-ONLY (no execution)
Compliance: SOC2 CC8.1, CC6.6 | HIPAA 164.308(a)(1)

## EXECUTIVE SUMMARY

This supplemental plan addresses the remaining needs-review files that were not included in the initial execution of RIS-2025-11-20-CLEANUP-001.

**Parent Plan Execution Summary:**
- Total files moved: 1,352
  - Deletion bucket: 1,294 files
  - Archive bucket: 28 files
  - Needs-review bucket: 30 files

**Original Requirement:**
- Needs-review files required: 130
- Needs-review files moved: 30
- **Missing needs-review files: 100 (estimated)**

**Actual Discovery:**
Upon re-scanning the 7 CredentialMate repositories using the original needs-review patterns, significantly more files were identified than originally estimated.

---

## DISCREPANCY ANALYSIS

The original plan estimated 130 needs-review files based on:
- credentialmate-docs: 2
- credentialmate-app: 95
- credentialmate-notification: 2
- credentialmate-schemas: 12
- credentialmate-ai: 16
- credentialmate-infra: 3

**Pattern-matched files discovered:**

| Repository | Pattern | Original Est. | Actual Found |
|------------|---------|---------------|--------------|
| credentialmate-app | diag_*.md | 21 | 51 |
| credentialmate-app | api_*.md | 7 | 6 |
| credentialmate-app | design_*.md | 11 | 36 |
| credentialmate-app | ops_*.md | 3 | 128 |
| credentialmate-app | spec_*.md | 2 | 21 |
| credentialmate-ai | *.csv governance | 16 | 15 (remaining) |

**Note:** The significant increase in ops_*.md files (3 estimated vs 128 found) suggests either additional documentation was created after the original plan, or the original estimate was incomplete.

---

## SUPPLEMENTAL NEEDS-REVIEW FILES

### credentialmate-app (242 files)

These files match the diagnostic, API, design, operations, and specification patterns defined in the original plan:

#### Diagnostic Reports (diag_*.md) - 51 files
- backend/tests/diag_baseline_accuracy_report_v1.0.md
- backend/tests/diag_bug_fix_cme_misclassification_v1.0.md
- backend/tests/diag_edge_case_analysis_v1.0.md
- backend/tests/diag_haiku_vs_sonnet_analysis_v1.0.md
- backend/tests/diag_phase3_step4_validation_report_v1.0.md
- backend/tests/diag_tesseract_findings_summary_v1.0.md
- diag_authentication_500_error_fixes_v1.0.md
- diag_authentication_500_error_root_cause_analysis_v1.0.md
- diag_aws_bedrock_throttling_analysis_v1.0.md
- diag_branch_protection_report_v1.0.md
- diag_critical_fixes_applied_v1.0.md
- diag_docker_diagnostic_report_v1.0.md
- diag_login_error_investigation_v1.0.md
- diag_m2_t3_completion_report_v1.0.md
- diag_m2_t4_final_tdd_status_report_v1.0.md
- diag_m2_t4_phase1_completion_report_v1.0.md
- diag_m2_t4_red_phase_readiness_report_v1.0.md
- diag_milestone_1_completion_report_v1.0.md
- diag_new_phase_1_orchestration_report_v1.0.md
- diag_phase_8_completion_report_v1.0.md
- diag_phase2_completion_report_v1.0.md
- diag_phase3_completion_report_v1.0.md
- diag_phase3_end_to_end_test_report_v1.0.md
- diag_phase7_progress_report_v1.0.md
- diag_reassessment_current_state_v1.0.md
- diag_ris_phase5_completion_report_v1.0.md
- diag_ris_phase9_10_completion_report_v1.0.md
- diag_session_closure_report_v1.0.md
- docs/data-model-build/diag_phase1_tests_passing_report_v1.0.md
- docs/governance/diag_cost_analysis_and_optimization_v1.0.md
- docs/governance/diag_ris_docker_configuration_fix_v1.0.md
- docs/governance/diag_tech_stack_e2e_analysis_v1.0.md
- docs/governance/diag_test_errors_fixed_v1.0.md
- docs/governance/diag_workspace_assessment_ris_20251118v2_v1.0.md
- docs/governance/diag_workspace_assessment_v1.0.md
- docs/ux-ui/outputs/diag_alternative_bedrock_models_analysis_v1.0.md
- docs/ux-ui/outputs/diag_model_upgrade_impact_analysis_v1.0.md
- docs/ux-ui/outputs/diag_session_1_10_comprehensive_analysis_v1.0.md
- docs/ux-ui/outputs/diag_session_1_11_extraction_comparison_analysis_v1.0.md
- docs/ux-ui/outputs/diag_session_1_12_systematic_gt_fix_plan_v1.0.md
- docs/ux-ui/outputs/diag_session_1_2_deliverables_report_v1.0.md
- docs/ux-ui/outputs/diag_session_1_3_accuracy_report_v1.0.md
- docs/ux-ui/outputs/diag_session_1_3_deliverables_report_v1.0.md
- docs/ux-ui/outputs/diag_session_1_4_field_extraction_report_v1.0.md
- docs/ux-ui/outputs/diag_session_1_5_field_extraction_improvement_report_v1.0.md
- docs/ux-ui/outputs/diag_session_1_7_findings_v1.0.md
- docs/ux-ui/outputs/diag_session_1_8_title_fix_summary_v1.0.md
- docs/ux-ui/outputs/diag_session_1_9_regression_analysis_v1.0.md
- docs/ux-ui/outputs/diag_session_2_1_calibration_analysis_v1.0.md
- docs/ux-ui/outputs/diag_session_2_2_discrepancy_analysis_report_v1.0.md
- docs/ux-ui/outputs/diag_session_2_3_1_validation_report_v1.0.md

#### API Documentation (api_*.md) - 6 files
- api_api_testing_report_v1.0.md
- api_database_api_usage_guide_v1.0.md
- api_m2_t3_endpoint_wiring_complete_v1.0.md
- api_m2_t4_phase2_admin_endpoints_fix_v1.0.md
- api_wiring_quick_reference_v1.0.md
- backend/app/routers/v2/API_ENDPOINT_INVENTORY.md

#### Design Documentation (design_*.md) - 36 files
- backend/tests/design_quick_start_v1.0.md
- design_docker_quick_commands_v1.0.md
- design_final_pre_rebuild_assessment_v1.0.md
- design_m2_t4_quick_reference_v1.0.md
- design_phase_1_project_management_framework_v1.0.md
- design_phase2_quick_reference_v1.0.md
- design_pre_rebuild_checklist_v1.0.md
- design_pre_rebuild_status_v1.0.md
- design_quick_fix_guide_v1.0.md
- design_quick_start_v1.0.md
- design_quickstart_v1.0.md
- design_session_continuity_m2_t4_v1.0.md
- docs/data-model-build/design_agent_context_session_guide_v1.0.md
- docs/data-model-build/design_architecture_quick_start_v1.0.md
- docs/data-model-build/design_data_architecture_executive_summary_v1.0.md
- docs/data-model-build/design_event_driven_implementation_guide_v1.0.md
- docs/data-model-build/design_extensible_data_architecture_design_v1.0.md
- docs/data-model-build/design_extensible_data_architecture_tdd_plan_v1.0.md
- docs/data-model-build/design_phase6_dashboards_completion_v1.0.md
- docs/data-model-build/design_phase6_quick_reference_v1.0.md
- docs/data-model-build/design_pm_quick_reference_v1.0.md
- docs/governance/design_issue_login_failure_relationship_ambiguity_2025111_v1.0.md
- docs/governance/design_pulse_check_dashboard_v1.0.md
- docs/RIS/design_admin_guide_v1.0.md
- docs/RIS/design_ai_query_guide_v1.0.md
- docs/RIS/design_automation_setup_guide_v1.0.md
- docs/RIS/design_dashboards_v1.0.md
- docs/RIS/design_performance_guide_v1.0.md
- docs/RIS/design_phase10_operations_guide_v1.0.md
- docs/RIS/design_phase9_10_implementation_guide_v1.0.md
- docs/RIS/design_ris_phase_execution_guide_v1.0.md
- docs/RIS/design_ris_phase1_testing_guide_v1.0.md
- docs/RIS/design_training_quick_reference_v1.0.md
- docs/ux-ui/outputs/design_pricing_page_screenshot_guide_v1.0.md
- docs/ux-ui/outputs/design_session_1_11_continuity_prompt_v1.0.md
- docs/ux-ui/outputs/design_ui_ux_0_1_addendum_corrections_v1.0.md

#### Operations Documentation (ops_*.md) - 128 files
(Full list in CSV manifest)

Key categories:
- Session summaries and completion reports
- Implementation plans and execution guides
- Deployment checklists and validation reports
- Project management and tracking documents
- Phase completion reports

#### Specification Documentation (spec_*.md) - 21 files
- .github/spec_audit_log_guide_v1.0.md
- .github/spec_change_control_policy_v1.0.md
- docs/data-model-build/spec_tracker_requirements_addendum_v1.0.md
- docs/governance/spec_security_audit_v1.0.md
- docs/RIS/spec_data_table_schema_v1.0.md
- docs/RIS/spec_phase5_security_scanning_v1.0.md
- docs/RIS/spec_ris_documentation_standards_v1.0.md
- docs/RIS/spec_schema_documentation_v1.0.md
- docs/RIS/spec_security_audit_v1.0.md
- docs/ux-ui/outputs/spec_ground_truth_audit_summary_v1.0.md
- docs/ux-ui/outputs/spec_session_1_12_ground_truth_audit_results_v1.0.md
- docs/ux-ui/outputs/spec_session_1_6_schema_harmonization_report_v1.0.md
- spec_app_security_v1.0.md
- spec_compensating_controls_checklist_v1.0.md
- spec_comprehensive_codebase_audit_v1.0.md
- spec_github_security_setup_v1.0.md
- spec_hipaa_gap_analysis_v1.0.md
- spec_metadata_compliance_report_v1.0.md
- spec_schema_import_fixes_v1.0.md
- spec_security_audit_report_v1.0.md
- spec_security_blockers_resolution_v1.0.md

### credentialmate-ai (15 files)

Governance orchestration files requiring review:
- governance/orchestration/AUTOMATION_LOG.csv
- governance/orchestration/CHANGES_LOG.csv
- governance/orchestration/CHANGE_LOG.csv
- governance/orchestration/CHAT_LOG.csv
- governance/orchestration/INITIATIVE_NOTIF_001_EMAIL_INFRASTRUCTURE.csv
- governance/orchestration/ISSUES_LOG.csv
- governance/orchestration/KNOWLEDGE_BASE.csv
- governance/orchestration/KNOWLEDGE_HTTPONLY_COOKIES_20251112.csv
- governance/orchestration/PROJECT_PLAN.csv
- governance/orchestration/RISK_REGISTER.csv
- governance/orchestration/SESSIONS.csv
- governance/orchestration/TASK_LOG.csv
- governance/orchestration/TESTING_RESULTS.csv
- governance/orchestration/TESTING_RESULTS_UPLOAD_AUTH.csv
- governance/orchestration/TRACKERS.csv

---

## SUMMARY

| Repository | Files |
|------------|-------|
| credentialmate-app | 242 |
| credentialmate-ai | 15 |
| **TOTAL** | **257** |

---

## RATIONALE

All files in this supplemental plan are flagged as **needs-review** because they:
1. Match the patterns specified in the original RIS-2025-11-20-CLEANUP-001 plan
2. Were not included in the initial execution manifest
3. Require human decision on whether to retain, archive, or delete
4. May contain valuable project history, technical documentation, or governance records

---

## SAFETY VALIDATION

- Runtime-critical files: NOT INCLUDED
- Active migrations: NOT INCLUDED
- Seed files: NOT INCLUDED
- Infrastructure state files: NOT INCLUDED
- Build system files: NOT INCLUDED

Result: **Safe to execute**

---

## RIS PLAN LOG

ID: **RIS-2025-11-20-CLEANUP-001-SUPPLEMENT**
Parent Plan: RIS-2025-11-20-CLEANUP-001
Operation: Supplemental needs-review file identification
Status: PLAN_GENERATED
Files identified: 257
Risk: low (documentation files only)
Execution: blocked pending user approval

---

## ACTION REQUIRED

No files will be moved until explicit user approval is provided.

This supplemental plan should be reviewed to determine:
1. Whether all 257 files should be moved to needs-review
2. If some files should be reclassified to deletion or archive
3. If any files should be excluded entirely

---

## PROVENANCE

- Plan ID: RIS-2025-11-20-CLEANUP-001-SUPPLEMENT
- Parent Plan: RIS-2025-11-20-CLEANUP-001
- Created: 2025-11-20
- Rationale: missing_from_initial_plan_execution
- Compliance: SOC2 CC8.1, CC6.6