# Phase 2: Self-Evolution, TUI, and Shell Integration

## 🎯 Objectives Achieved

- [x] Self-evolution framework with hot-reload
- [x] Textual TUI interface
- [x] Shell integration (Bash backbone, Fish user standard)
- [x] Auto-completion generation (Bash + Fish)
- [x] Evolution history tracking

## 🔄 Self-Evolution Framework (evolution.py)

### EvolutionManager

**Performance Analysis**
```python
metrics = evolution.analyze_performance(audit_log_path, window=100)
# Returns: total_queries, success_rate, tool_usage, error_patterns
```

**Improvement Proposals**
```python
proposals = evolution.propose_improvements(metrics)
# Suggests: error_handling, optimization, feature_improvements
```

**Hot-Reload**
```python
result = evolution.hot_reload_module("tools")
# Reloads module without stopping service (importlib.reload)
```

**Backup & Rollback**
```python
backup = evolution.create_backup(file_path)
evolution.rollback_to_backup(backup)
# Full version history in ~/.evolution/backups/
```

### Self-Improvement Loop

1. Agent monitors its audit log every N queries
2. Analyzes success rate, tool usage, error patterns
3. Proposes improvements to `tools.py`, `agent.py`, `rag.py`
4. Creates backup before modification
5. Applies improvement and hot-reloads module
6. Logs change to `.evolution/versions.jsonl`
7. On failure: automatically rolls back to last stable version

### Version Tracking

```jsonl
{"timestamp": "2024-01-15T10:30:45", "file": "tools.py", "description": "Add retry logic", "status": "applied"}
```

## 🖥️ Textual TUI (tui.py)

Interactive terminal UI with:

**Components**
- Status Bar: Shows LLM backend, agent state
- Query Panel: Input field with placeholder suggestions
- Output Panel: Formatted query results with RAG context
- Audit Log: Live display of recent operations

**Key Bindings**
| Key | Action |
|-----|--------|
| `Ctrl+C` | Quit |
| `Ctrl+L` | Clear output |
| `Tab` | Next focus |
| `Shift+Tab` | Previous focus |
| `Enter` | Submit query |

**Launch**
```bash
pcopilot --tui
```

## 🐚 Shell Integration

### Bash (Backbone)

**Auto-generated Completions**
```bash
source ~/.local/share/phynix/completions/pcopilot.bash
pcopilot search [TAB]  # Autocomplete
```

**Features**
- Dynamic option completion (--json, --backend, --audit-log)
- Command suggestions (search, eval, check, status)

### Fish (User Standard)

**Interactive Functions**
```fish
# User-friendly wrapper
pcopilot search ripgrep

# Helper functions
pcopilot_audit                  # View audit log
pcopilot_backend               # Show LLM backend
pcopilot --help
```

**Completions & Suggestions**
```bash
set fish_complete_path ~/.local/share/fish/completions $fish_complete_path
```

**NixOS Module**
```nix
# modules/core/shell.nix provides:
# - Fish shell as default user shell
# - Completions for pcopilot
# - Aliases (ll, vi, nix-build, nix-check)
# - Functions (mkcd)
```

## 📋 Auto-Completion Generation (completions.py)

**CompletionGenerator**

Generates shell completions automatically from tool registry:

```bash
pcopilot --generate-completions ~/.config/fish/completions
# Creates:
# ~/.config/fish/completions/pcopilot.fish
# ~/.config/bash/completions/pcopilot.bash
```

**Tool Registry**

Introspectable tool definitions allow dynamic completion generation:

```python
{
    "nix_search": {
        "description": "Search nixpkgs for packages",
        "args": [{"name": "query", "type": "string"}]
    },
    ...
}
```

## 🔧 CLI Enhancements

```bash
# Original features
pcopilot "search git"              # Single query
pcopilot                           # Interactive mode
pcopilot --json "query"            # JSON output
pcopilot --backend                 # Show LLM backend
pcopilot --audit-log               # View audit log

# Phase 2 additions
pcopilot --tui                     # Textual UI
pcopilot --generate-completions DIR  # Generate shell completions
pcopilot --evolution-status        # Show improvement history
```

## 📊 Architecture Updates

### Flake Outputs

```nix
flake.nix includes:
- phynix-copilot package with Textual + Rich dependencies
- Development shell with Fish + completion tools
```

### Dependencies Added

```
textual>=0.40.0      # TUI framework
rich>=13.0.0         # Terminal formatting
```

### Module Structure

```
pkgs/phynix-copilot/
├── agent.py          # Core logic
├── cli.py            # CLI with TUI/completion support
├── tools.py          # Read-only tool definitions
├── rag.py            # RAG index skeleton
├── evolution.py      # Self-evolution framework (NEW)
├── completions.py    # Shell completion generator (NEW)
├── tui.py            # Textual UI (NEW)
└── requirements.txt
```

## 🚀 Deployment & Usage

### Installation

```bash
# Via NixOS
nix build .#phynix-copilot
nix-shell

# Or directly
pip install -r requirements.txt
```

### Generate Completions

```bash
pcopilot --generate-completions ~/.config/fish/completions

# Add to ~/.config/fish/config.fish
source ~/.config/fish/completions/pcopilot.fish
```

### Monitor Evolution

```bash
# Check agent improvement history
pcopilot --evolution-status

# View detailed audit log
pcopilot --audit-log | tail -20
```

## 🔄 Self-Improvement Loop

**Triggers**
- After every 50 successful queries (configurable)
- On error pattern detection (>10% failure rate)
- Manual trigger: `pcopilot --analyze-and-improve`

**Process**
1. Read audit log
2. Calculate metrics
3. Generate proposals
4. Backup current version
5. Apply improvement
6. Hot-reload module
7. Log change
8. On failure: rollback

**Safety**
- All changes are reversible (backed up)
- Rollback on exception
- Audit trail of all modifications
- Version pinning capability

## 📝 Integration Points

### NixOS Module Integration

- Fish as default shell
- Auto-generated completions
- Service auto-starts on user login
- State directories managed

### Systemd Service

```ini
[Service]
Type=simple
ExecStart=pcopilot
Environment=PHYNIX_DAEMON=1
Restart=on-failure
```

## 🎯 Next Steps (Phase 3)

- [ ] Actual ChromaDB indexing with document ingestion
- [ ] Write-mode tools with confirmation gates
- [ ] Home Manager autonomous apply (within sandbox)
- [ ] TUI enhancements (keybind preview, diff viewer)
- [ ] LLM-based improvement proposals (using agent itself)
- [ ] Installer TUI (nixos-installer replacement)

---

**Phase 2 Status:** Self-evolution + TUI + Shell integration complete. Foundation ready for write-mode autonomy.
