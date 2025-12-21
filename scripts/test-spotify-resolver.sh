#!/bin/bash
#
# Test script for Spotify Album Resolver
#
# This script runs comprehensive tests to verify the resolver is working correctly.
#
# Version: 1.0.0
# Author: cursor
# Created: December 23rd, 2025

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Script path
RESOLVER_SCRIPT="${HOME}/.config/tools/spotify-resolver/src/spotify-album-resolver.py"

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

log_info() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((TESTS_PASSED++))
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((TESTS_FAILED++))
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Check if script exists
if [ ! -f "${RESOLVER_SCRIPT}" ]; then
    log_fail "Resolver script not found: ${RESOLVER_SCRIPT}"
    exit 1
fi

# Check if script is executable
if [ ! -x "${RESOLVER_SCRIPT}" ]; then
    log_warning "Script is not executable, fixing..."
    chmod +x "${RESOLVER_SCRIPT}"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Spotify Album Resolver - Test Suite"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# Test 1: Help message
log_info "Test 1: Help message"
if python3 "${RESOLVER_SCRIPT}" --help &>/dev/null; then
    log_success "Help message works"
else
    log_fail "Help message failed"
fi

# Test 2: Known album (The Beatles - Abbey Road)
log_info "Test 2: Known album - The Beatles - Abbey Road"
if python3 "${RESOLVER_SCRIPT}" --band "The Beatles" --album "Abbey Road" --no-clipboard 2>/dev/null | grep -q "https://open.spotify.com/album/"; then
    log_success "Found The Beatles - Abbey Road"
else
    log_fail "Could not find The Beatles - Abbey Road"
fi

# Test 3: Known album (Metallica - Master of Puppets)
log_info "Test 3: Known album - Metallica - Master of Puppets"
if python3 "${RESOLVER_SCRIPT}" --band "Metallica" --album "Master of Puppets" --no-clipboard 2>/dev/null | grep -q "https://open.spotify.com/album/"; then
    log_success "Found Metallica - Master of Puppets"
else
    log_fail "Could not find Metallica - Master of Puppets"
fi

# Test 4: Query format
log_info "Test 4: Query format"
if python3 "${RESOLVER_SCRIPT}" --query "artist:Pink Floyd album:The Dark Side of the Moon" --no-clipboard 2>/dev/null | grep -q "https://open.spotify.com/album/"; then
    log_success "Query format works"
else
    log_fail "Query format failed"
fi

# Test 5: Non-existent album (should fail)
log_info "Test 5: Non-existent album (should fail gracefully)"
if python3 "${RESOLVER_SCRIPT}" --band "Nonexistent Band XYZ123" --album "Fake Album 456" 2>/dev/null; then
    log_fail "Should have failed for non-existent album"
else
    log_success "Correctly failed for non-existent album"
fi

# Test 6: Special characters
log_info "Test 6: Special characters - AC/DC"
if python3 "${RESOLVER_SCRIPT}" --band "AC/DC" --album "Highway to Hell" --no-clipboard 2>/dev/null | grep -q "https://open.spotify.com/album/"; then
    log_success "Handled special characters correctly"
else
    log_fail "Failed with special characters"
fi

# Test 7: Verbose mode
log_info "Test 7: Verbose mode"
if python3 "${RESOLVER_SCRIPT}" --band "The Beatles" --album "Abbey Road" --verbose --no-clipboard 2>&1 | grep -q "Searching Spotify"; then
    log_success "Verbose mode works"
else
    log_fail "Verbose mode failed"
fi

# Test 8: Clipboard functionality (if available)
log_info "Test 8: Clipboard functionality"
CLIPBOARD_TEST=$(python3 "${RESOLVER_SCRIPT}" --band "The Beatles" --album "Abbey Road" 2>/dev/null && pbpaste 2>/dev/null || echo "")
if echo "${CLIPBOARD_TEST}" | grep -q "https://open.spotify.com/album/"; then
    log_success "Clipboard functionality works"
else
    log_warning "Clipboard test skipped (may require manual verification)"
fi

# Test 9: Piped input
log_info "Test 9: Piped input"
PIPED_RESULT=$(echo "Metallica - Master of Puppets" | python3 "${RESOLVER_SCRIPT}" --no-clipboard 2>/dev/null || echo "")
if echo "${PIPED_RESULT}" | grep -q "https://open.spotify.com/album/"; then
    log_success "Piped input works"
else
    log_fail "Piped input failed"
fi

# Summary
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Test Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "Tests Passed: ${GREEN}${TESTS_PASSED}${NC}"
echo -e "Tests Failed: ${RED}${TESTS_FAILED}${NC}"
echo

if [ ${TESTS_FAILED} -eq 0 ]; then
    echo -e "${GREEN}All tests passed! ✓${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. Please review the output above.${NC}"
    exit 1
fi
