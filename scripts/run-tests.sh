#!/bin/bash
#
# Quick test runner for Xen ARM64 ports
# Compiles and runs test suite without full Xen build
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${SCRIPT_DIR}/.."

echo "🧪 Xen ARM64 Port Test Runner"
echo "=============================="

# Check for cross-compiler (macOS needs it)
if [[ "$(uname -m)" != "aarch64" ]]; then
    echo "⚠️  Not on ARM64 - checking for cross-compiler..."
    if ! command -v aarch64-linux-gnu-gcc &> /dev/null; then
        echo "❌ aarch64-linux-gnu-gcc not found"
        echo "Install with: brew install aarch64-elf-gcc (macOS)"
        echo "           or: sudo apt install gcc-aarch64-linux-gnu (Linux)"
        exit 1
    fi
    CC="aarch64-linux-gnu-gcc"
    AS="aarch64-linux-gnu-as"
    LD="aarch64-linux-gnu-ld"
else
    CC="gcc"
    AS="as"
    LD="ld"
fi

# Compile C test
echo "📝 Compiling qemu-trap-test.c..."
$CC -o "${ROOT_DIR}/tests/qemu-trap-test" \
    "${ROOT_DIR}/tests/qemu-trap-test.c" \
    -static -O2 || {
    echo "❌ C compilation failed"
    exit 1
}
echo "✅ qemu-trap-test compiled"

# Compile ASM test
echo "📝 Compiling trap-trigger-arm64.S..."
$AS "${ROOT_DIR}/tests/trap-trigger-arm64.S" \
    -o "${ROOT_DIR}/tests/trap-trigger.o" || {
    echo "❌ ASM compilation failed"
    exit 1
}

$LD -o "${ROOT_DIR}/tests/trap-trigger" \
    "${ROOT_DIR}/tests/trap-trigger.o" || {
    echo "❌ Linking failed"
    exit 1
}
echo "✅ trap-trigger compiled"

# Summary
echo ""
echo "✅ All tests compiled successfully!"
echo ""
echo "📦 Test binaries ready:"
echo "  - tests/qemu-trap-test (C user-space)"
echo "  - tests/trap-trigger (ASM low-level)"
echo ""
echo "🚀 Next steps:"
echo "  1. Build Xen: ./scripts/build-xen-arm64.sh"
echo "  2. Or run standalone: qemu-system-aarch64 -M virt -kernel tests/qemu-trap-test"
echo "  3. Check logs for PASS/FAIL"
