# SOC2 COMPLIANCE AUDIT ARTIFACT
# Generated: 2025-11-21T04:43:50Z
# Task ID: APP-QUARANTINE-MOVE-2025-11
# Classification: INTERNAL
# Purpose: Relocation Manifest for credentialmate-app Quarantine Files

# App Quarantine Move Manifest

## Summary

- **Task ID**: APP-QUARANTINE-MOVE-2025-11
- **Generated**: 2025-11-21T04:43:50Z
- **Source Repository**: credentialmate-app
- **Destination**: credentialmate-quarantine/deletion/credentialmate-app/

## Statistics

| Metric | Count |
|--------|-------|
| Total Candidates | 239 |
| Successfully Moved | 239 |
| Not Found | 0 |
| Errors | 0 |

## Bucket Breakdown

### questionable_tests (238 files)

- `backend/.orchestration/KNOWLEDGE_BASE.csv`
- `backend/.orchestration/SESSIONS.csv`
- `backend/.orchestration/TASK_LOG.csv`
- `backend/analyze_cme_overlap.py`
- `backend/analyze_confidence_calibration.py`
- `backend/analyze_discrepancies.py`
- `backend/analyze_discrepancies_direct.py`
- `backend/analyze_ground_truth.py`
- `backend/audit_all_ground_truth.py`
- `backend/audit_ground_truth.py`
- `backend/audit_high_accuracy_docs.py`
- `backend/audit_title_ground_truth.py`
- `backend/batch_final_output.txt`
- `backend/batch_upload_with_checkpoints.py`
- `backend/capture_parsing_learnings.py`
- `backend/check_actual_seed_time.py`
- `backend/check_and_seed.py`
- `backend/check_seed_data.py`
- `backend/cme_state_overlap_analysis.csv`
- `backend/cme_state_overlap_analysis_20251119_035909.csv`
- `backend/compare_extraction_vs_gt.py`
- `backend/create_admin_users.py`
- `backend/create_demo_users.py`
- `backend/create_master_analysis.py`
- `backend/create_test_user.py`
- `backend/database_export/README_ALL_STATES_CONSOLIDATED.md`
- `backend/database_export/license_compliance_reports/20251119_002628/license_based_compliance.csv`
- `backend/database_export/license_compliance_reports/20251119_002645/license_based_compliance.csv`
- `backend/database_export/license_compliance_reports/20251119_002716/license_based_compliance.csv`
- `backend/database_export/license_compliance_reports/20251119_002726/license_based_compliance.csv`
- `backend/database_export/license_compliance_reports/20251119_003614/license_based_compliance.csv`
- `backend/database_export/license_compliance_reports/20251119_004026/license_based_compliance.csv`
- `backend/database_export/state_requirements_ALL_STATES_CONSOLIDATED.csv`
- `backend/database_export/state_requirements_ALL_STATES_CONSOLIDATED.xlsm`
- `backend/database_export/state_requirements_md_do/README.md`
- `backend/database_export/state_requirements_md_do/content_specific_cme_md_do.csv`
- `backend/database_export/state_requirements_md_do/exemptions_equivalents_md_do.csv`
- `backend/database_export/state_requirements_md_do/special_population_requirements_md_do.csv`
- `backend/database_export/state_requirements_md_do/state_board_contacts.csv`
- `backend/database_export/state_requirements_md_do/state_cme_base_requirements_md_do.csv`
- `backend/database_export/state_requirements_md_do_CONSOLIDATED.csv`
- `backend/discrepancy_taxonomy.py`
- `backend/export_provider_analysis.py`
- `backend/export_users.py`
- `backend/find_actual_seed.py`
- `backend/find_seed_timestamp.py`
- `backend/fix_all_ground_truth_final.py`
- `backend/fix_all_ground_truth_round2.py`
- `backend/fix_ground_truth_nulls.py`
- `backend/fix_ground_truth_option_a.py`
- `backend/fix_ground_truth_option_c.py`
- `backend/fix_ground_truth_schemas.py`
- `backend/gen_csv.py`
- `backend/link_admins_to_all_providers.py`
- `backend/provider_cme.csv`
- `backend/provider_documents.csv`
- `backend/provider_licenses.csv`
- `backend/provider_summary.csv`
- `backend/query_provider_data.py`
- `backend/query_seed_metadata.py`
- `backend/query_users.py`
- `backend/reset_db_simple.py`
- `backend/restore_and_validate_titles.py`
- `backend/run_accuracy_test.py`
- `backend/run_field_extraction_test.py`
- `backend/run_migrations.py`
- `backend/scripts/check_alembic_version.py`
- `backend/scripts/check_db_tables.py`
- `backend/scripts/fix_unicode_in_seeds.py`
- `backend/scripts/reset_database.py`
- `backend/scripts/reset_db.py`
- `backend/scripts/validate_schema_parity.py`
- `backend/seed_50_state_providers.py`
- `backend/start_mock_server.bat`
- `backend/tests/fixtures/ground_truth/TD-001_ground_truth.json`
- `backend/tests/fixtures/ground_truth/TD-002_ground_truth.json`
- `backend/tests/fixtures/ground_truth/TD-003_ground_truth.json`
- `backend/tests/fixtures/ground_truth/TD-004_ground_truth.json`
- `backend/tests/fixtures/ground_truth/TD-005_ground_truth.json`
- `backend/tests/fixtures/ground_truth/TD-006_ground_truth.json`
- `backend/tests/fixtures/ground_truth/TD-007_ground_truth.json`
- `backend/tests/fixtures/ground_truth/TD-008_ground_truth.json`
- `backend/tests/fixtures/ground_truth/TD-009_ground_truth.json`
- `backend/tests/fixtures/ground_truth/TD-010_ground_truth.json`
- `backend/tests/fixtures/ground_truth/TD-011_ground_truth.json`
- `backend/tests/fixtures/ground_truth/TD-012_ground_truth.json`
- `backend/tests/fixtures/ground_truth/TD-013_ground_truth.json`
- `backend/tests/fixtures/ground_truth/TD-014_ground_truth.json`
- `backend/tests/fixtures/ground_truth/TD-015_ground_truth.json`
- `backend/tests/fixtures/ground_truth/TD-016_ground_truth.json`
- `backend/tests/fixtures/ground_truth/TD-017_ground_truth.json`
- `backend/tests/fixtures/ground_truth/TD-018_ground_truth.json`
- `backend/tests/fixtures/ground_truth/TD-019_ground_truth.json`
- `backend/tests/fixtures/ground_truth/TD-020_ground_truth.json`
- `backend/tests/fixtures/ground_truth/TD-021_ground_truth.json`
- `backend/tests/fixtures/ground_truth/TD-022_ground_truth.json`
- `backend/tests/fixtures/ground_truth/TD-023_ground_truth.json`
- `backend/tests/qa_logs/AGGREGATE_SUMMARY.csv`
- `backend/tests/qa_logs/CLASSIFICATION_LOG.csv`
- `backend/tests/qa_logs/PARSING_LOG.csv`
- `backend/tests/requirements-qa.txt`
- `backend/tests/test_parse_document_hybrid_mock_mode.py`
- `backend/update_titles_from_parser.py`
- `backend/uploads/2025/11/20251109_924a7d6f_ABIM IM.png`
- `backend/uploads/2025/11/20251109_a0b4d06a_Medical School.png`
- `backend/uploads/2025/11/20251110_9d5158bb_BNDD.pdf`
- `backend/uploads/2025/11/20251110_fef4cffe_audit.pdf`
- `backend/uploads/2025/11/20251111_9f3c4096_CME 25hrs June 2025.pdf`
- `backend/uploads/2025/11/20251111_e47ddf8b_25 CMEs July 2023.pdf`
- `backend/uploads/2025/11/20251113_24b51784_25 CMEs July 2023.pdf`
- `backend/uploads/2025/11/20251113_35fc8cd6_NetCE(3).png`
- `backend/uploads/2025/11/20251113_42063a54_WillsEye Hospital(5).png`
- `backend/uploads/2025/11/20251113_9be2def0_certificate-1157731502 (1).pdf`
- `backend/uploads/2025/11/20251113_f6bdb11e_WillsEye Hospital.png`
- `backend/uploads/2025/11/20251117_37877de2_WillsEye Hospital(3).png`
- `backend/uploads/2025/11/20251117_4433bf00_NetCE(2).png`
- `backend/uploads/2025/11/20251117_5729c042_NetCE(6).png`
- `backend/uploads/2025/11/20251118_a6ec0a05_NetCE(6).png`
- `backend/uploads/2025/11/20251119_28a8bb2f_12642_732_1.pdf`
- `backend/uploads/2025/11/20251119_4d4478d3_12642_735_1.pdf`
- `backend/uploads/2025/11/20251119_4fcfde18_12642_734_1.pdf`
- `backend/uploads/2025/11/20251119_53406083_NetCE(2).png`
- `backend/uploads/2025/11/20251119_57c0fea6_Certificate_47174.pdf`
- `backend/uploads/2025/11/20251119_7235ad09_NetCE(6).png`
- `backend/uploads/2025/11/20251119_7b5eef4b_Certificate_95152 (1).pdf`
- `backend/uploads/2025/11/20251119_8437b4a5_NetCE(2).png`
- `backend/uploads/2025/11/20251119_88c23f97_Certificate_96342.pdf`
- `backend/uploads/2025/11/20251119_8d2aa3be_Certificate_94151.pdf`
- `backend/uploads/2025/11/20251119_fee8dc15_12642_736_1.pdf`
- `backend/uploads/2025/11/25 CMEs July 2023.pdf`
- `backend/uploads/2025/11/CME 25hrs June 2025.pdf`
- `backend/uploads/2025/11/FL - Presscribing contolled substances CME 2023.pdf`
- `backend/uploads/2025/11/Implicit bias CMW.pdf`
- `backend/uploads/2025/11/PA Child abuse CME 2022.pdf`
- `backend/uploads/2025/11/PA Requirements_Certificate_No_369708.pdf`
- `backend/uploads/2025/11/_FL CME Broker Instructions.pdf`
- `backend/uploads/2025/11/_NE-Physician-CE-2024-Nebraska-Medical-Licensure-Program-37318187-certificate.pdf`
- `backend/uploads/2025/11/certificate-1157737702.pdf`
- `backend/uploads/2025/11/nguyenD.pdf`
- `backend/uploads/2025/11/polaris-ht101-certificate-template.png`
- `backend/validate_compliance_grid.py`
- `backend/verify_and_create_users.py`
- `database_export/20251117_194253/_EXPORT_SUMMARY.txt`
- `database_export/20251117_194253/ai_actions.csv`
- `database_export/20251117_194253/alembic_version.csv`
- `database_export/20251117_194253/audit_logs.csv`
- `database_export/20251117_194253/change_events.csv`
- `database_export/20251117_194253/cme_activities.csv`
- `database_export/20251117_194253/content_specific_cme.csv`
- `database_export/20251117_194253/delegations.csv`
- `database_export/20251117_194253/developer_events.csv`
- `database_export/20251117_194253/documents.csv`
- `database_export/20251117_194253/events.csv`
- `database_export/20251117_194253/exemptions_equivalents.csv`
- `database_export/20251117_194253/file_dependencies.csv`
- `database_export/20251117_194253/file_history_events.csv`
- `database_export/20251117_194253/file_history_events_y2025m11.csv`
- `database_export/20251117_194253/file_history_events_y2025m12.csv`
- `database_export/20251117_194253/file_history_events_y2026m01.csv`
- `database_export/20251117_194253/file_history_events_y2026m02.csv`
- `database_export/20251117_194253/file_history_events_y2026m03.csv`
- `database_export/20251117_194253/file_history_events_y2026m04.csv`
- `database_export/20251117_194253/file_history_events_y2026m05.csv`
- `database_export/20251117_194253/file_history_events_y2026m06.csv`
- `database_export/20251117_194253/file_history_events_y2026m07.csv`
- `database_export/20251117_194253/file_history_events_y2026m08.csv`
- `database_export/20251117_194253/file_history_events_y2026m09.csv`
- `database_export/20251117_194253/file_history_events_y2026m10.csv`
- `database_export/20251117_194253/file_metadata.csv`
- `database_export/20251117_194253/file_registry.csv`
- `database_export/20251117_194253/file_security_metadata.csv`
- `database_export/20251117_194253/keystroke_logs.csv`
- `database_export/20251117_194253/licenses.csv`
- `database_export/20251117_194253/login_lockouts.csv`
- `database_export/20251117_194253/notification_queue.csv`
- `database_export/20251117_194253/notification_settings.csv`
- `database_export/20251117_194253/special_population_requirements.csv`
- `database_export/20251117_194253/state_board_contacts.csv`
- `database_export/20251117_194253/state_cme_base_requirements.csv`
- `database_export/20251117_194253/user_actions.csv`
- `database_export/20251117_194253/user_sessions.csv`
- `database_export/20251117_194253/users.csv`
- `database_export/license_based_compliance.csv`
- `database_export/license_based_compliance.xlsx`
- `database_export/license_based_compliance_FINAL.csv`
- `database_export/license_based_compliance_updated.csv`
- `database_export/provider_compliance_reports/20251117_200352/compliance_summary.txt`
- `database_export/provider_compliance_reports/20251117_200352/provider_compliance_detailed.csv`
- `database_export/provider_compliance_reports/20251118_175623/compliance_summary.txt`
- `database_export/provider_compliance_reports/20251118_175623/provider_compliance_detailed.csv`
- `database_export/provider_compliance_reports/20251118_184839/compliance_summary.txt`
- `database_export/provider_compliance_reports/20251118_184839/provider_compliance_detailed.csv`
- `frontend/demo/compliance-grid-demo.html`
- `frontend/demo/test-login.py`
- `generate_dashboard_report.py`
- `scripts/database_exports/README.md`
- `scripts/database_exports/export_compliance_audit.py`
- `scripts/database_exports/export_provider_compliance_detailed.py`
- `scripts/database_exports/export_ris_system.py`
- `scripts/database_exports/export_tracking_events.py`
- `scripts/database_exports/export_user_management.py`
- `scripts/ris/README.md`
- `scripts/ris/backup-db.sh`
- `scripts/ris/ris_daily_scan.sh`
- `scripts/ris/ris_health_check.sh`
- `scripts/ris/ris_monthly_maintenance.sh`
- `scripts/ris/ris_performance_check.sh`
- `scripts/ris/ris_weekly_report.py`
- `scripts/ris/setup_cron_linux.sh`
- `scripts/ris/setup_cron_windows.bat`
- `scripts/validate_governance.sh`
- `scripts/validate_tracker.py`
- `scripts/validate_ux_ui_session.py`
- `terraform/README.md`
- `terraform/alb-fix.tf`
- `terraform/alb.tf`
- `terraform/cloudwatch.tf`
- `terraform/ec2.tf`
- `terraform/outputs.tf`
- `terraform/providers.tf`
- `terraform/rds.tf`
- `terraform/route53.tf`
- `terraform/s3.tf`
- `terraform/security_groups.tf`
- `terraform/terraform.tfvars.example`
- `terraform/user_data.sh`
- `terraform/variables.tf`
- `terraform/vpc.tf`
- `uat/PHASE5_STEP4_COMPLETION_SUMMARY.md`
- `uat/QUICK_START_GUIDE.md`
- `uat/README.md`
- `uat/SHIPFASTV1_UAT_BUG_REPORT_TEMPLATE.md`
- `uat/SHIPFASTV1_UAT_ERROR_CLASSIFICATION_MATRIX.md`
- `uat/SHIPFASTV1_UAT_FEEDBACK_SUMMARY_TEMPLATE.md`
- `uat/SHIPFASTV1_UAT_ISSUE_TYPES.md`
- `uat/SHIPFASTV1_UAT_TRACEABILITY_SHEET.csv`
- `update_routers_for_tdd.py`
- `wire_endpoints.py`

### temp_or_dev (1 files)

- `backend/tests/debug_driver_license_ocr.py`

## RIS Logging

```json
{
    "task_id": "APP-QUARANTINE-MOVE-2025-11",
    "total_moved": 239,
    "total_not_found": 0,
    "total_errors": 0,
    "status": "success"
}
```

## Verification

To verify the relocation:

1. Check that source files no longer exist in credentialmate-app
2. Confirm files exist in credentialmate-quarantine/deletion/credentialmate-app/
3. Verify directory structure is preserved

## Next Steps

1. Review moved files for any that should be restored
2. Commit changes to both repositories
3. Update any references to these files if needed
