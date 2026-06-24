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

# Show audit log
pcopilot --audit-log

# Show LLM backend
pcopilot --backend
```

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
| 2 | Write tools, Home Manager autonomy | ⏳ Pending |
| 3 | TUI interface, Installer ISO | ⏳ Pending |
| 4 | Branding, Cachix, Plymouth | ⏳ Pending |
| 5 | Public launch | ⏳ Pending |

See [PHASE_1.md](PHASE_1.md) for detailed architecture and tool documentation.

---

**Status:** Phase 1 complete. Copilot read-only intelligence ready. Next: Phase 2 (write tools + autonomy).
