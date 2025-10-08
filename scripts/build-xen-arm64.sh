#!/bin/bash

# Automated build script for Xen on ARM64
# Assumes native build on ARM64 (aarch64) host, e.g., Ubuntu/Debian-based.
# Run as non-root; uses sudo for package installs.
# Usage: ./build-xen-arm64.sh [version]  (default: stable-4.17)

set -euo pipefail  # Exit on error, undefined vars, pipe failures

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
XEN_DIR="${SCRIPT_DIR}/../xen-ports/xen"  # Relative to scripts/ dir
XEN_VERSION="${1:-stable-4.17}"  # Default to latest stable

# Function for error handling and logging
log_error() {
    echo "ERROR: $1" >&2
    exit 1
}

log_info() {
    echo "INFO: $1"
}

# Check architecture
if [[ "$(uname -m)" != "aarch64" ]]; then
    log_error "This script is designed for native ARM64 (aarch64) builds. Current arch: $(uname -m)"
fi

log_info "Starting Xen ARM64 build for version: ${XEN_VERSION}"

# Step 1: Install dependencies (Ubuntu/Debian assumed; adjust for other distros)
log_info "Installing dependencies..."
if ! command -v apt-get &> /dev/null; then
    log_error "apt-get not found. This script assumes Debian/Ubuntu."
fi

sudo apt-get update || log_error "Failed to update package list"
sudo apt-get install -y \
    build-essential \
    git \
    bison \
    flex \
    libssl-dev \
    python3 \
    python3-dev \
    python3-setuptools \
    libncurses5-dev \
    uuid-dev \
    liblzma-dev \
    || log_error "Failed to install dependencies"

# Additional Xen-specific deps for ARM64
sudo apt-get install -y \
    gcc-aarch64-linux-gnu \
    libc6-dev-arm64-cross \
    || log_info "Cross-compiler deps skipped (native build assumed)"

# Step 2: Clone or update Xen source
if [[ -d "${XEN_DIR}" ]]; then
    log_info "Using existing Xen repo in ${XEN_DIR}"
    cd "${XEN_DIR}"
else
    log_error "Xen source not found at ${XEN_DIR}. Please clone first."
fi

# Step 3: Configure (Xen uses stubdom and tools; ARM64 detected automatically)
log_info "Configuring Xen for ARM64..."
./autogen.sh || log_error "Autogen failed"

# Configure with ARM64-specific flags (native build; for cross-compile, add --host=aarch64-linux-gnu)
./configure \
    --enable-guest-admin \
    --disable-qemu-traditional \
    --with-system-seabios=no \
    --with-system-ovmf=no \
    || log_error "Configuration failed"

# Step 4: Compile
log_info "Compiling Xen (using $(nproc) parallel jobs)..."
make -j"$(nproc)" dist-xen || log_error "Compilation failed"

# Step 5: Install (to /usr/local by default; use sudo)
log_info "Installing Xen..."
sudo make install || log_error "Installation failed"

# Step 6: Post-install verification
log_info "Verifying installation..."
if [[ -f "/usr/local/lib/xen/bin/xen" ]] || [[ -f "/usr/local/libexec/xen/bin/xen" ]]; then
    log_info "Xen hypervisor installed successfully!"
else
    log_error "Installation verification failed: xen binary not found"
fi

log_info "Xen ARM64 build complete! Check /usr/local for binaries."
log_info "To run Xen, ensure kernel and grub are configured for ARM64 hypervisor."
