#!/bin/bash
# Run all install method tests in Docker
# Usage: ./run_all_tests.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TESTS=(
    "test_curl_install"
    "test_pip_install"
    "test_uv_install"
    "test_npm_install"
    "test_apt_install"
)

FAILED_TESTS=()

echo "========================================"
echo "Kimigas Install Method Tests"
echo "========================================"
echo

for test in "${TESTS[@]}"; do
    echo "Running $test..."
    if docker build -f "${SCRIPT_DIR}/${test}.dockerfile" -t "kimigas-${test}" "${SCRIPT_DIR}/.." 2>&1 | tee "${SCRIPT_DIR}/${test}.log"; then
        echo "✅ $test PASSED"
        # Cleanup successful test image
        docker rmi "kimigas-${test}" >/dev/null 2>&1 || true
    else
        echo "❌ $test FAILED"
        FAILED_TESTS+=("$test")
    fi
    echo
done

echo "========================================"
if [ ${#FAILED_TESTS[@]} -eq 0 ]; then
    echo "All tests passed!"
    # Clean up all dangling images
    docker system prune -f >/dev/null 2>&1 || true
    exit 0
else
    echo "Failed tests:"
    for test in "${FAILED_TESTS[@]}"; do
        echo "  - $test"
        echo "    Log: ${SCRIPT_DIR}/${test}.log"
    done
    exit 1
fi
