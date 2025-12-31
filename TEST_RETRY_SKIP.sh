#!/bin/bash
# Test retry-skip logic with direct commands

echo "============================================================"
echo "TEST: Retry-Skip Logic Verification"
echo "============================================================"
echo ""
echo "Test 1: Direct fetch command (lb - currently down)"
echo "------------------------------------------------------------"
./capcat fetch lb --count 5
echo ""
echo "============================================================"
echo "Test completed!"
echo "You should have seen:"
echo "  - Timeout accessing https://lobste.rs (attempt 1/2)"
echo "  - Timeout accessing https://lobste.rs (attempt 2/2)"
echo "  - Skipping source 'lb' after 2 failed attempts"
echo "============================================================"
