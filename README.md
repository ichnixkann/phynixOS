# PHYNIX OS

> A self-evolving NixOS distribution with an integrated AI Copilot — built for power users who want their system to understand itself.

[![Release](https://github.com/ichnixkann/phynixOS/actions/workflows/build.yml/badge.svg)](https://github.com/ichnixkann/phynixOS/actions/workflows/build.yml)
[![Hercules CI](https://img.shields.io/badge/CI-Hercules-yellow)](https://hercules-ci.com)

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

All flake outputs are built by [Hercules CI](https://hercules-ci.com) and
published to a self-hosted [Attic](https://github.com/zhaofengli/attic)
cache. No Cachix, no proprietary SaaS in the build path. Add the cache
to `configuration.nix` to avoid rebuilding:

```nix
nix.settings = {
  substituters = [ "https://cache.phynix-os.example/phynix" ];
  trusted-public-keys = [ "phynix:PLACEHOLDER_ATTIC_PUBLIC_KEY=" ];
};
```

(Replace the placeholder host + key with the values printed by
`atticadm cache info phynix` when the cache is provisioned —
see [`docs/infra/attic-deploy.md`](./docs/infra/attic-deploy.md).)

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

Nix builds and **live, sandboxed VM tests** run on
**[Hercules CI](https://hercules-ci.com)** — a Nix-native CI that's free
for public OSS, with a fully open-source agent (`hercules-ci-agent`).
Hercules picks up every flake output declared in
[`hercules-ci.nix`](./hercules-ci.nix) and posts a status check per
output on each PR.

The flake `checks.x86_64-linux.*` set includes:

| Check | What it covers |
|-------|----------------|
| `boot-workstation`   | Boots a VM with the phynix modules; asserts multi-user.target + copilot service registered |
| `copilot-service`    | Minimal VM; asserts `pcopilot --backend` exits 0 with no LLM |
| `installer-iso-boot` | Boots the installer ISO; asserts the TUI installer is on PATH |
| `python-unit`        | pytest suite under `phynix-os/pkgs/phynix-copilot/tests/` |

GitHub Actions is used only for things Hercules doesn't cover:

| Workflow | Trigger | Description |
|----------|---------|-------------|
| `build.yml` → `build-iso` | main + tags | Build installer ISO + push to Attic cache |
| `build.yml` → `release`   | `v*` tags    | GitHub Release with ISO + sha256 |
| `mirror.yml`              | main + tags  | Mirror repository to Codeberg |

Required secrets:
- `ATTIC_TOKEN` — write token for the Attic cache (used by Hercules and by the ISO job)
- `CODEBERG_SSH_KEY` — Codeberg deploy key for the mirror

See [`docs/infra/attic-deploy.md`](./docs/infra/attic-deploy.md) for the
cache deployment recipe.

---

## License

MIT
