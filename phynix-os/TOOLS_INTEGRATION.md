# PHYNIX Tools Integration

## 🦀 Rust Tools

### claurst — Claude Rust CLI

**Purpose:** CLI tool for Claude Code written in Rust

**Integration:**
- User-space application (not system-wide)
- Available via `claurst` command
- Nix package in `overlays/rust-tools.nix`
- Home Manager integration via `home/default.nix`

**Usage:**
```bash
claurst --help                    # View help
pcopilot-claurst                 # Alias for claurst
```

**Where it fits:**
- Companion to Claude Code desktop app
- Can be used alongside PHYNIX Copilot
- Provides alternative interface for Claude interactions

### crush — charmbracelet TUI

**Purpose:** Modern TUI tool from charmbracelet

**Integration:**
- User-space application
- Available via `crush` command
- Nix package in `overlays/rust-tools.nix`
- Home Manager integration

**Usage:**
```bash
crush --help                      # View help
crush-menu                        # Fish function launcher
```

**Where it fits:**
- Terminal UI companion
- Can be used for interactive selections
- Integrates with PHYNIX TUI ecosystem

### Omo Ultimate — OpenCode Assistant

**Purpose:** Advanced code assistant for OpenCode

**Integration:**
- User-space application
- Available via `omo-ultimate` command
- Nix package in `overlays/rust-tools.nix`
- Home Manager integration
- Fish shell functions

**Usage:**
```bash
omo-ultimate --help               # View help
omo-ultimate code "your query"    # Ask about code
omo-ultimate init                 # Initialize project
code-review                       # Review current directory
ask-omo "explain this function"   # Fish function
```

**Where it fits:**
- Companion to claurst for Claude queries
- OpenCode-native code assistant
- Integrated with PHYNIX development workflow
- Can be combined with PHYNIX Copilot for full stack assistance

## 🔧 Development Environment

### modules/dev/default.nix

**Includes:**
- Git and version control
- Build tools (make, cmake, pkg-config)
- Interpreters (Python, Node.js)
- Text editors (vim, nano)
- Rust toolchain (via rust.nix)

**Enabled Features:**
- Nix flakes support
- Development shells (`nix develop`)
- Build commands (`nix build`)

### modules/dev/rust.nix

**Provides:**
- Rust compiler and toolchain
- Cargo package manager
- Custom Rust tools (claurst, crush)

**Aliases:**
```bash
dev                     # Enter nix develop shell
build                   # Build with nix build
rebuild                 # nixos-rebuild with flake
```

## 📦 Package Integration

### Overlay System (overlays/rust-tools.nix)

Custom package definitions for:
- **claurst** from `Kuberwastaken/claurst`
- **crush** from `charmbracelet/crush`

Both use `rustPlatform.buildRustPackage` for Nix compilation.

**Note:** SHA256 hashes use fakeSha256 as placeholders. First build will compute real hashes.

### Home Manager (home/default.nix)

**User packages:**
- claurst
- crush
- Plus standard utilities (bat, exa, fd, ripgrep, fzf)

**Shell functions:**
- Fish: `claurst-claude`, `crush-menu`
- Bash: aliases for quick access

## 🎯 Usage Patterns

### Integration with PHYNIX Copilot

**Option 1: Companion Tool**
```bash
# Use claurst independently
claurst query "what's the weather?"

# Use crush for menu-driven selections
crush select-package-to-install

# Use pcopilot for system config
pcopilot "install ripgrep hm"
```

**Option 2: Agent Integration (Future)**
Could integrate claurst as a read-only tool:
```python
# tools.py could call claurst for Claude queries
def claude_query(query: str) -> str:
    result = subprocess.run(["claurst", query])
    return result.stdout
```

**Option 3: TUI Integration (Future)**
crush could be used in pcopilot --tui for menu selections:
```bash
pcopilot --tui
# Uses crush for interactive package selection
```

## 🚀 Installation

Users will have these available automatically:

```bash
# After building PHYNIX
claurst --version
crush --version

# Via Home Manager
home-manager switch
# Activates both tools in user environment

# Via system rebuild
sudo nixos-rebuild switch --flake .
# Installs system-wide (if enabled in configuration)
```

## 📝 Development

### Building from Source

```bash
# Enter dev shell with Rust
nix develop

# Build claurst locally
cargo build --release

# Build crush locally
cargo build --release
```

### Updating Packages

When updating claurst or crush, modify:
1. `overlays/rust-tools.nix` - SHA256 hashes
2. Version strings in package definitions
3. Commit to track updates

---

**Status:** claurst and crush integrated as user-space tools with Nix packages and Home Manager support.
