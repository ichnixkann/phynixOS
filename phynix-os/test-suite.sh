#!/usr/bin/env bash
# PHYNIX OS Test Suite
# Validates all phases and components

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
test_section() {
    echo -e "\n${YELLOW}[TEST]${NC} $1"
}

test_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((TESTS_PASSED++))
}

test_fail() {
    echo -e "${RED}✗${NC} $1"
    ((TESTS_FAILED++))
}

# Phase 0: Flake validation
test_section "Phase 0: Flake Structure"

if [ -f "phynix-os/flake.nix" ]; then
    test_pass "flake.nix exists"
else
    test_fail "flake.nix not found"
fi

if grep -q "nixpkgs" "phynix-os/flake.nix" && \
   grep -q "home-manager" "phynix-os/flake.nix" && \
   grep -q "hyprland" "phynix-os/flake.nix"; then
    test_pass "All required inputs present"
else
    test_fail "Missing inputs in flake.nix"
fi

# Phase 0: Module structure
test_section "Phase 0: Module Structure"

REQUIRED_MODULES=(
    "phynix-os/modules/core/default.nix"
    "phynix-os/modules/core/boot.nix"
    "phynix-os/modules/core/networking.nix"
    "phynix-os/modules/core/audio.nix"
    "phynix-os/modules/core/shell.nix"
    "phynix-os/modules/desktop/hyprland/default.nix"
    "phynix-os/modules/copilot/default.nix"
)

for module in "${REQUIRED_MODULES[@]}"; do
    if [ -f "$module" ]; then
        test_pass "Module exists: $module"
    else
        test_fail "Module missing: $module"
    fi
done

# Phase 1: Agent files
test_section "Phase 1: Agent Implementation"

AGENT_FILES=(
    "phynix-os/pkgs/phynix-copilot/agent.py"
    "phynix-os/pkgs/phynix-copilot/tools.py"
    "phynix-os/pkgs/phynix-copilot/cli.py"
    "phynix-os/pkgs/phynix-copilot/rag.py"
)

for file in "${AGENT_FILES[@]}"; do
    if [ -f "$file" ]; then
        test_pass "File exists: $(basename $file)"
    else
        test_fail "File missing: $(basename $file)"
    fi
done

# Validate Python syntax
test_section "Phase 1: Python Syntax"

for file in "${AGENT_FILES[@]}"; do
    if python3 -m py_compile "$file" 2>/dev/null; then
        test_pass "Valid Python: $(basename $file)"
    else
        test_fail "Invalid Python: $(basename $file)"
    fi
done

# Phase 2: Evolution and TUI
test_section "Phase 2: Self-Evolution & TUI"

PHASE2_FILES=(
    "phynix-os/pkgs/phynix-copilot/evolution.py"
    "phynix-os/pkgs/phynix-copilot/completions.py"
    "phynix-os/pkgs/phynix-copilot/tui.py"
)

for file in "${PHASE2_FILES[@]}"; do
    if [ -f "$file" ]; then
        test_pass "File exists: $(basename $file)"
    else
        test_fail "File missing: $(basename $file)"
    fi
done

# Phase 3: Write tools
test_section "Phase 3: Write-Mode Tools"

PHASE3_FILES=(
    "phynix-os/pkgs/phynix-copilot/write_tools.py"
    "phynix-os/pkgs/phynix-copilot/write_agent.py"
)

for file in "${PHASE3_FILES[@]}"; do
    if [ -f "$file" ]; then
        test_pass "File exists: $(basename $file)"
    else
        test_fail "File missing: $(basename $file)"
    fi
done

# Tools integration
test_section "Tools Integration: Rust"

if [ -f "phynix-os/overlays/rust-tools.nix" ]; then
    test_pass "Rust tools overlay exists"
else
    test_fail "Rust tools overlay missing"
fi

if [ -f "phynix-os/modules/dev/default.nix" ] && \
   [ -f "phynix-os/modules/dev/rust.nix" ]; then
    test_pass "Development modules exist"
else
    test_fail "Development modules missing"
fi

if [ -f "phynix-os/home/default.nix" ]; then
    test_pass "Home Manager config exists"
else
    test_fail "Home Manager config missing"
fi

# Documentation
test_section "Documentation"

DOCS=(
    "phynix-os/README.md"
    "phynix-os/PHASE_1.md"
    "phynix-os/PHASE_2.md"
    "phynix-os/PHASE_3.md"
    "phynix-os/TOOLS_INTEGRATION.md"
)

for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        test_pass "Doc exists: $(basename $doc)"
    else
        test_fail "Doc missing: $(basename $doc)"
    fi
done

# Import tests (Python)
test_section "Python Module Imports"

python3 << 'PYTHON_TEST'
import sys
sys.path.insert(0, "phynix-os/pkgs/phynix-copilot")

try:
    import tools
    print("✓ tools module imports")
except Exception as e:
    print(f"✗ tools module failed: {e}")

try:
    import rag
    print("✓ rag module imports")
except Exception as e:
    print(f"✗ rag module failed: {e}")

try:
    import evolution
    print("✓ evolution module imports")
except Exception as e:
    print(f"✗ evolution module failed: {e}")

try:
    import completions
    print("✓ completions module imports")
except Exception as e:
    print(f"✗ completions module failed: {e}")

try:
    import write_tools
    print("✓ write_tools module imports")
except Exception as e:
    print(f"✗ write_tools module failed: {e}")

try:
    import write_agent
    print("✓ write_agent module imports")
except Exception as e:
    print(f"✗ write_agent module failed: {e}")
PYTHON_TEST

# Summary
test_section "Test Summary"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}All tests passed! ✓${NC}"
    exit 0
else
    echo -e "\n${RED}Some tests failed.${NC}"
    exit 1
fi
