#!/usr/bin/env bash
# Run all gastown smoke tests locally.
#
# Usage:
#   bash tests_gastown/run_all.sh
#   # or from repo root:
#   make test-gastown
set -euo pipefail

cd "$(dirname "$0")/.."

TESTS=(
    tests_gastown/test_wire_smoke.py
    tests_gastown/test_print_smoke.py
    tests_gastown/test_queue_smoke.py
    tests_gastown/test_skills_smoke.py
)

TOTAL=0
PASSED=0
FAILED=0

for test in "${TESTS[@]}"; do
    echo ""
    echo "━━━ Running: $test ━━━"
    if python3 "$test"; then
        PASSED=$((PASSED + 1))
    else
        FAILED=$((FAILED + 1))
    fi
    TOTAL=$((TOTAL + 1))
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "GASTOWN TEST SUITE: $PASSED/$TOTAL passed, $FAILED failed"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

exit $FAILED
