#!/usr/bin/env bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
info() { echo -e "${BLUE}ℹ${NC} $*"; }
success() { echo -e "${GREEN}✓${NC} $*"; }
warn() { echo -e "${YELLOW}⚠${NC} $*"; }
error() { echo -e "${RED}✗${NC} $*"; exit 1; }

info "PHYNIX OS ISO Test Launcher"
echo

# Check for QEMU
if ! command -v qemu-system-x86_64 &> /dev/null; then
    error "QEMU is not installed. Install it with: nix-shell -p qemu"
fi
success "QEMU found: $(qemu-system-x86_64 --version | head -1)"

# Look for ISO
ISO_PATH=""
if [ -n "$1" ]; then
    ISO_PATH="$1"
elif [ -f "result-installer-iso/iso/phynix-installer-*.iso" ]; then
    ISO_PATH="result-installer-iso/iso/phynix-installer-*.iso"
    ISO_PATH=$(ls -1 $ISO_PATH 2>/dev/null | head -1)
else
    # Try to build if not found
    warn "ISO not found. Building installer-iso..."
    nix build .#nixosConfigurations.installer-iso.config.system.build.isoImage -o result-installer-iso
    ISO_PATH="result-installer-iso/iso/phynix-installer-*.iso"
    ISO_PATH=$(ls -1 $ISO_PATH 2>/dev/null | head -1)
fi

if [ -z "$ISO_PATH" ] || [ ! -f "$ISO_PATH" ]; then
    error "Could not find or build ISO. Specify path as: $0 /path/to/iso"
fi

success "ISO found: $ISO_PATH"
success "ISO size: $(du -h "$ISO_PATH" | cut -f1)"
echo

# Detect KVM support
KVM_ARGS="-enable-kvm"
if ! [ -r /dev/kvm ] 2>/dev/null; then
    warn "KVM not available, using software emulation (slower)"
    KVM_ARGS=""
fi

# Setup networking
info "Configuring network..."
NETWORK_ARGS="-nic user,model=virtio,hostfwd=tcp:127.0.0.1:2222-:22"
success "SSH will be available at: ssh -p 2222 root@127.0.0.1"
echo

# QEMU configuration
MEMORY="${PHYNIX_MEMORY:-4096}"
CPUS="${PHYNIX_CPUS:-4}"
DISK_SIZE="${PHYNIX_DISK_SIZE:-20G}"

info "Launch Configuration:"
echo "  Memory: $MEMORY MB"
echo "  CPUs: $CPUS"
echo "  Disk: $DISK_SIZE"
echo

info "Starting QEMU with PHYNIX OS ISO..."
echo "  TIP: Use Ctrl+Alt+G to release mouse, Ctrl+C to stop QEMU"
echo

qemu-system-x86_64 \
    $KVM_ARGS \
    -m $MEMORY \
    -smp $CPUS \
    -cdrom "$ISO_PATH" \
    -drive file=/tmp/phynix-test-disk.qcow2,format=qcow2,if=virtio,cache=writeback \
    -bios /usr/share/ovmf/OVMF.fd \
    $NETWORK_ARGS \
    -display gtk,zoom-to-fit=off \
    -machine q35 \
    -device qemu-xhci,id=xhci \
    -device usb-kbd \
    -device usb-mouse \
    -rtc base=utc
