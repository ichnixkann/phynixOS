# PHYNIX OS

A NixOS-based distribution with an integrated AI Copilot for system configuration assistance.

## 📋 Project Structure

```
phynix-os/
├── flake.nix                    # Entry point, pinned inputs
├── modules/
│   ├── core/                    # Boot, Kernel, Audio, Network
│   ├── desktop/hyprland/        # Hyprland + Waybar + Mako
│   ├── copilot/                 # Agent systemd service
│   ├── dev/                     # Shells, Toolchains (TODO)
│   └── branding/                # Plymouth, GRUB, Themes (TODO)
├── hosts/
│   ├── installer/               # ISO profile
│   ├── workstation/             # Reference host
│   └── laptop/                  # Minimal profile (TODO)
├── home/                        # Home Manager modules (TODO)
├── pkgs/phynix-copilot/        # Agent service + CLI
└── overlays/                    # Custom package overlays (TODO)
```

## 🚀 Phase 0: Foundation

- [x] Flake skeleton with nixpkgs, home-manager, hyprland inputs
- [x] Core modules (boot, networking, audio)
- [x] Hyprland desktop with greetd+tuigreet
- [x] Copilot systemd-user-service stub
- [x] LLM backend detection (CPU-optimized routing)
- [ ] Test flake evaluation
- [ ] Document build instructions

## 🤖 Copilot Backend Strategy

**CPU-Only Systems (Primary)**
1. HuggingFace Inference API (remote, requires HF_TOKEN)
2. Ollama (local, requires setup) → qwen3-coder-next-moe
3. Fallback → phi-4-mini via Ollama (~2GB RAM)

## 🤖 Copilot CLI

```bash
# Interactive mode
pcopilot

# Single query
pcopilot "search nixpkgs for git"

# Textual TUI
pcopilot --tui

# Show audit log
pcopilot --audit-log

# Show LLM backend
pcopilot --backend

# Generate shell completions
pcopilot --generate-completions ~/.config/fish/completions

# View evolution history
pcopilot --evolution-status
```

## 🐚 Shell Integration

**Fish** is the default user shell with:
- Auto-generated completions for pcopilot
- Helper functions: `pcopilot_audit`, `pcopilot_backend`
- Smart aliases and productivity functions

**Bash** is the backbone shell for scripts with:
- Full completion support
- Compatibility with system tools

## 🔧 Building

```bash
cd phynix-os
nix flake check                          # Validate flake
nix build .#nixosConfigurations.workstation
nix build .#phynix-copilot              # Build agent standalone
```

## 📝 Configuration

- **Locale:** de_DE (Deutsch)
- **Display Manager:** greetd + tuigreet
- **Desktop:** Hyprland
- **Audio:** PipeWire
- **Network:** NetworkManager

## 📋 Phases

| Phase | Content | Status |
|-------|---------|--------|
| 0 | Flake skeleton, core modules, Hyprland | ✅ Complete |
| 1 | Read-only tools, RAG index, CLI | ✅ Complete |
| 2 | Self-evolution, TUI, Shell integration | ✅ Complete |
| 3 | Write-mode tools, Home Manager autonomy | ✅ Complete |
| 4 | ChromaDB ingestion, Installer TUI | ⏳ Pending |
| 5 | Branding, Cachix, Public launch | ⏳ Pending |

See [PHASE_1.md](PHASE_1.md), [PHASE_2.md](PHASE_2.md), and [PHASE_3.md](PHASE_3.md) for architecture.

## 🔐 Write-Mode Operations

Agent can now propose and apply system changes with confirmation gates:

```bash
# Interactive mode (confirm each change)
pcopilot "install ripgrep hm"

# Daemon mode (auto-approve safe operations)
pcopilot --daemon

# View pending changes
pcopilot --pending

# Rollback all changes
pcopilot --rollback
```

**Safe Operations** (auto-approvable):
- Home Manager package installs
- Shell aliases and functions
- Environment variables

**Unsafe Operations** (require approval):
- System rebuild switch
- Security-sensitive changes
- Systemd unit modifications

---

**Status:** Phase 3 complete. Write-mode tools with safety gates ready. Next: Phase 4 (ChromaDB + Installer TUI).
