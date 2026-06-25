# PHYNIX OS

> A self-evolving NixOS distribution with an integrated AI Copilot — built for power users who want their system to understand itself.

[![Checks](https://github.com/ichnixkann/phynixOS/actions/workflows/checks.yml/badge.svg)](https://github.com/ichnixkann/phynixOS/actions/workflows/checks.yml)
[![Release](https://github.com/ichnixkann/phynixOS/actions/workflows/build.yml/badge.svg)](https://github.com/ichnixkann/phynixOS/actions/workflows/build.yml)

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

There is no project-owned cache yet (open follow-up). For now, every
build pulls from `cache.nixos.org`.

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

Everything runs on GitHub Actions free runners. No third-party signups,
no paid services. The runners expose `/dev/kvm`, so the NixOS VM tests
boot real virtual machines at native speed.

### `checks.yml` — live sandbox tests on every PR

Runs every flake `checks.x86_64-linux.*` output:

| Check | What it covers |
|-------|----------------|
| `boot-workstation`   | Boots a VM with the phynix modules; asserts `multi-user.target` + copilot user-service registered |
| `copilot-service`    | Minimal VM; asserts `pcopilot --backend` exits 0 with no LLM available |
| `installer-iso-build` | Realises the installer ISO image end-to-end |
| `python-unit`        | pytest suite under [`phynix-os/pkgs/phynix-copilot/tests/`](./phynix-os/pkgs/phynix-copilot/tests/) |

Plus a second job that builds `packages.phynix-copilot` so package
regressions are caught even when tests pass. The Nix store is cached
across runs via [`nix-community/cache-nix-action`](https://github.com/nix-community/cache-nix-action)
(GitHub Actions cache, free, OSS).

### Other workflows

| Workflow | Trigger | Description |
|----------|---------|-------------|
| `build.yml` → `build-iso` | main + tags | Build installer ISO |
| `build.yml` → `release`   | `v*` tags   | GitHub Release with ISO + sha256 |
| `mirror.yml`              | main + tags | Mirror repository to Codeberg |

Required secrets:
- `CODEBERG_SSH_KEY` — Codeberg deploy key for the mirror

See [`phynix-os/tests/README.md`](./phynix-os/tests/README.md) for how
to run the VM tests locally and drive them interactively.

---

## License

LGPL-3.0-or-later. See [`LICENSE`](./LICENSE) (LGPLv3 — the additional
permissions) and [`COPYING`](./COPYING) (GPLv3, on top of which LGPLv3
adds those permissions).
