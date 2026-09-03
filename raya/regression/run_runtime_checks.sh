#!/bin/bash
# run_runtime_checks.sh — every RUNTIME (behaviour) detector in one command.
#
# These read real Raya call transcripts, so they need raya/.env and CANNOT run in the
# zero-secrets GitHub Actions daily job. That is exactly why a behaviour regression
# (e.g. the 2026-09-01 location-reconfirm and already-applied misses) never appeared in
# the daily email: the daily suite is STATIC only. Run this after any behaviour change,
# and see README "Runtime checks are not in the daily digest yet" for the standing gap.
#
# Usage: raya/regression/run_runtime_checks.sh [--since YYYY-MM-DD] [--agent <id>]
set -uo pipefail
cd "$(dirname "$0")/../.."
ARGS=("$@")
FAIL=0
for chk in consent_before_apply location_chain location_reconfirm apply_result_integrity apply_failure_wording location_integrity apply_outcomes; do
  echo ""
  echo "================================================================ $chk"
  python3 "raya/regression/$chk.py" "${ARGS[@]}" || FAIL=1
done
echo ""
if [ "$FAIL" -eq 0 ]; then echo "ALL RUNTIME CHECKS CLEAN"; else echo "RUNTIME FINDINGS PRESENT (exit 1)"; fi
exit "$FAIL"
