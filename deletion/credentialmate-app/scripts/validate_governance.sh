#!/bin/bash
# TIMESTAMP: 2025-11-16T06:04:50Z
# ORIGIN: credentialmate-app
# UPDATED_FOR: governance initialization

echo "Running AI Governance Validation..."

echo "Checking SOC2 metadata..."
grep -RIL "# TIMESTAMP:" backend/app frontend | while read -r file; do
  echo "❌ Missing SOC2 metadata: $file"
done

echo "Checking for parser modifications (forbidden)..."
if git diff HEAD backend/app/services/document_parser.py; then
  echo "❌ Parser modified — forbidden in ShipFastV1."
fi

echo "Checking for cross-repo import leakage..."
grep -R "credentialmate-" backend/app | grep -v credentialmate-app

echo "Validation complete."
