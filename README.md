# PHYNIX OS

> A self-evolving NixOS distribution with an integrated AI Copilot — built for power users who want their system to understand itself.

[![Release](https://github.com/ichnixkann/phynixOS/actions/workflows/build.yml/badge.svg)](https://github.com/ichnixkann/phynixOS/actions/workflows/build.yml)
[![PR Checks](https://github.com/ichnixkann/phynixOS/actions/workflows/pr-check.yml/badge.svg)](https://github.com/ichnixkann/phynixOS/actions/workflows/pr-check.yml)
[![Built by Garnix](https://img.shields.io/badge/built%20by-garnix.io-blue)](https://garnix.io)

> Canonical FOSS mirror: [codeberg.org/phynix-os/phynix-os](https://codeberg.org/phynix-os/phynix-os)

---

## What is PHYNIX OS?

PHYNIX OS is a NixOS-based Linux distribution that ships with a self-modifying AI agent (the *Copilot*) capable of reading your system configuration, proposing changes, and applying them — with your explicit approval. It is designed around the philosophy that an operating system should be able to explain and improve itself.

**Key traits:**

- **GPU-free** — LLM routing cascades: HuggingFace Inference API → Ollama (local) → offline RAG-only mode
- **Declarative** — everything is a Nix expression; the Copilot writes Nix, not shell scripts
- **Safe writes** — every change goes through a diff-and-confirm gate before touching disk
- **Self-evolving** — the Copilot can hot-reload its own modules without restarting the service
- **Hyprland desktop** — minimal, keyboard-driven Wayland compositor
- **Fish shell** — user-facing, with auto-generated Copilot completions

---

## Quick Start

### Install from ISO

1. Download the latest ISO from [Releases](https://github.com/ichnixkann/phynixOS/releases)
2. Verify the checksum:
   ```bash
   sha256sum -c phynix-os-*.iso.sha256
   ```
3. Write to USB:
   ```bash
   dd if=phynix-os-*.iso of=/dev/sdX bs=4M status=progress
   ```
4. Boot from USB and follow the TUI installer.

### Binary Cache

All flake outputs are built by [Garnix](https://garnix.io) and published to
the public `cache.garnix.io` binary cache — no Cachix, no proprietary
infrastructure. Add it to `configuration.nix` to avoid rebuilding:

```nix
nix.settings = {
  substituters = [ "https://cache.garnix.io" ];
  trusted-public-keys = [
    "cache.garnix.io:CTFPyKSLcx5RMJKfLo5EEPUObbA78b0YQ2DTCJXqr9g="
  ];
};
```

---

## Copilot CLI

```bash
# Interactive session
pcopilot

# One-shot query
pcopilot "search nixpkgs for ripgrep"

# Textual TUI
pcopilot --tui

# Show which LLM backend is active
pcopilot --backend

# Rebuild the RAG knowledge index
pcopilot --reindex

# View pending write proposals
pcopilot --pending

# Rollback all unapplied changes
pcopilot --rollback
```

### Write Operations

The Copilot can propose changes to your Home Manager config and NixOS modules:

```bash
pcopilot "install vim via home-manager"
# → shows diff → asks for confirmation → applies or discards
```

**Safe (auto-approved in daemon mode):** packages, shell aliases, functions  
**Unsafe (always require confirmation):** systemd units, security settings, rebuild switch

---

## Desktop & Tools

| Tool | Role |
|------|------|
| **Hyprland** | Wayland compositor |
| **Waybar** | Status bar |
| **tuigreet** | Login manager |
| **Fish + Tide** | User shell + prompt |
| **claurst** | Claude Rust CLI |
| **crush** | charmbracelet TUI selector |
| **Omo Ultimate** | OpenCode AI assistant |
| **pcopilot** | PHYNIX AI Copilot |

---

## Building from Source

Requirements: Nix with flakes enabled.

```bash
git clone https://github.com/ichnixkann/phynixOS
cd phynixOS/phynix-os

# Validate the flake
nix flake check --no-build

# Build the Copilot package
nix build .#phynix-copilot

# Build the installer ISO (requires nixos-generators)
nixos-generate --format iso --flake .#installer-iso --out-link result-iso
```

---

## Project Structure

```
phynix-os/
├── flake.nix                    # Flake inputs + package outputs
├── modules/
│   ├── core/                    # Boot, networking, audio, shell, cachix
│   ├── desktop/hyprland/        # Hyprland + Waybar + Mako + Wofi
│   ├── copilot/                 # systemd user service
│   ├── dev/                     # Rust + Python toolchains
│   └── branding/                # Plymouth boot theme + GRUB dark theme
├── hosts/
│   ├── installer/               # ISO profile (nixos-generators)
│   └── workstation/             # Reference workstation config
├── home/                        # Home Manager (user packages, Fish config)
├── installer/tui/               # Textual-based TUI installer wizard
├── overlays/rust-tools.nix      # claurst, crush, omo-ultimate derivations
├── pkgs/phynix-copilot/         # Copilot agent source
│   ├── agent.py                 # Core agent + LLM routing
│   ├── rag.py                   # ChromaDB RAG index
│   ├── write_tools.py           # WriteGate + Flake/HM/Rebuild tools
│   ├── write_agent.py           # Write-mode agent
│   ├── evolution.py             # Self-evolution + hot-reload
│   ├── tui.py                   # Textual TUI interface
│   ├── completions.py           # Auto-generated shell completions
│   └── cli.py                   # CLI entry point
└── assets/branding/             # Plymouth script + logo
```

---

## CI/CD

Nix builds run on **[Garnix](https://garnix.io)** — a Nix-native CI that's
free for public open-source repos and publishes results to the public
`cache.garnix.io` binary cache. The set of flake outputs Garnix builds is
declared in [`garnix.yaml`](./garnix.yaml).

GitHub Actions is used only for things Garnix doesn't cover:

| Workflow | Trigger | Description |
|----------|---------|-------------|
| Garnix (per output) | PRs + push | Flake check, package + NixOS + ISO builds, cache push |
| `build.yml` → `build-iso` | main/tags | Build installer ISO for release artifact |
| `build.yml` → `release` | `v*` tags | GitHub Release with ISO + sha256 |
| `build.yml` → `python-tests` | PRs + push | Python syntax, imports, RAG, routing |
| `pr-check.yml` → `syntax` | PRs | Fast Python feedback on PRs |
| `mirror.yml` | main/tags | Mirror repository to Codeberg |

Required secret: `CODEBERG_SSH_KEY` (Codeberg deploy key for the mirror).

---

## License

MIT
