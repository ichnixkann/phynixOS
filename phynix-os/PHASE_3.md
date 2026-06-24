# Phase 3: Write-Mode Tools & Home Manager Autonomy

## 🎯 Objectives Achieved

- [x] Write-mode tools with confirmation gates
- [x] Change proposal system with diffs
- [x] Rollback capability for all mutations
- [x] Home Manager autonomous apply (sandbox-safe scope)
- [x] NixOS rebuild tools (dry, test, switch)
- [x] Flake manipulation tools
- [x] WriteAgent for autonomous decision-making

## 🔓 WriteGate System (write_tools.py)

### Change Proposal Flow

```
Proposed Change → Format Diff → User Confirmation → Apply → Log
                                     ↓ (rejected)
                            Discard (no mutation)
```

### Change Dataclass

```python
@dataclass
class Change:
    file: str                  # Path to file
    operation: str             # "modify", "create", "delete"
    before: Optional[str]      # Original content
    after: Optional[str]       # New content
    reason: str                # Why this change
    confirmed: bool = False    # User approval status
```

### WriteGate Methods

```python
gate = WriteGate(callback=interactive_confirm)

# Propose and confirm
change = Change(...)
confirmed = gate.propose_change(change)  # Shows diff, awaits approval

# Rollback all
gate.rollback_all()  # Restore all files to before state
```

## 🛠️ Tool Categories

### FlakeTools

**add_package(name, nix_expr, reason)**
- Propose adding package to flake.nix
- Requires confirmation
- Validates Nix syntax (placeholder)

**update_module(module_path, config, reason)**
- Modify NixOS module
- Propose before apply
- Full rollback capability

### HomeManagerTools

**propose_hm_config(snippet, reason)**
- Suggest Home Manager configuration
- User approval before apply
- Integrates with write_gate

**apply_hm_auto(config)**
- Auto-apply within sandbox scope
- Safe keys: packages, aliases, functions
- Unsafe keys require manual approval
  - systemd, services, security

### NixosRebuildTools

**dry_activate()**
- Preview changes without activation
- No user confirmation needed
- Shows what would change

**propose_rebuild_test(reason)**
- Test rebuild (active until reboot)
- Requires explicit user approval
- Safer than switch

**propose_rebuild_switch(reason)**
- Permanent system rebuild
- ⚠️ High-risk operation
- Double confirmation prompt

## 🤖 WriteAgent (write_agent.py)

### Interactive vs. Auto Modes

**Interactive (Default)**
```python
agent = WriteAgent(interactive=True)
# Every change awaits user confirmation
# Full control, slower
```

**Autonomous (Daemon)**
```python
agent = WriteAgent(interactive=False)
# Auto-approve safe operations only
# Fast, sandboxed to known-safe scope
```

### Sandbox Scope

**Safe (Auto-approvable)**
- Home Manager package installs
- Shell aliases and functions
- Environment variables
- Program configurations

**Unsafe (Requires Manual Approval)**
- System rebuild switch (permanent)
- Security-sensitive changes
- Systemd unit modifications
- Boot configuration

### Query Routing

```python
agent.handle_query("install vim hm")
# → Home Manager package installation

agent.handle_query("rebuild test")
# → NixOS rebuild preview + test

agent.handle_query("rebuild switch")
# → Permanent system change (requires approval)
```

### Session Management

```python
# Check sandbox status
agent.get_sandbox_status()

# Rollback all changes in session
agent.rollback_pending()

# Finalize session
agent.commit_session()
```

## 📊 Change Tracking

### Per-Session

```python
write_gate.pending_changes: list[Change]
# All proposed + applied changes in session
```

### Persistent

Updates to agent audit log:
```jsonl
{
    "timestamp": "2024-01-15T10:30:45",
    "action": "write_tool_applied",
    "status": "success",
    "details": {
        "tool": "hm_package_install",
        "package": "ripgrep",
        "confirmed": true
    }
}
```

## 🔄 Rollback Mechanism

### Manual Rollback

```python
agent.rollback_pending()
# Restores all files touched in session
# Runs `home-manager switch` with previous config
```

### Automatic Rollback

On exception:
1. WriteGate catches error
2. Iterates pending_changes in reverse
3. Calls _apply_rollback for each
4. Restores system to before-session state
5. Logs rollback event

## 🚀 Integration with Copilot

### Enhanced CLI

```bash
# Interactive mode (confirmed each step)
pcopilot --interactive

# Daemon mode (sandbox-auto)
pcopilot --daemon

# View pending changes
pcopilot --pending

# Rollback session
pcopilot --rollback

# Commit session
pcopilot --commit
```

### Agent Decision Flow

```
User Query
    ↓
Route to Tool (read-only or write)
    ↓
Write Tool?
    ├─ Yes → Create Change object
    │        ↓
    │        Show Diff (interactive)
    │        ↓
    │        User Approves?
    │        ├─ Yes → Apply Change
    │        │        Log to audit.jsonl
    │        └─ No → Discard
    │
    └─ No → Execute read-only tool
            Return results
```

## 🔐 Safety Guarantees

1. **No unexpected mutations** — All writes require explicit approval
2. **Reversible** — Every change is backed up and can be rolled back
3. **Auditable** — Full log of who (agent) did what (write_tool) and why (reason)
4. **Sandboxed** — Autonomous mode limited to known-safe operations
5. **Transparent** — Diffs shown before each change

## 📝 Example Workflows

### Install Package via Home Manager (Interactive)

```bash
$ pcopilot "install ripgrep hm"

=== PROPOSED CHANGE ===
home.packages with ripgrep
Reason: User requested installation
=== END ===

Approve? (yes/no): yes
✓ ripgrep added to Home Manager
```

### System Rebuild (With Safety)

```bash
$ pcopilot "rebuild test"

Dry-activate: OK
Changes preview: [... list of changes ...]

=== PROPOSED: Test Rebuild ===
Changes will be active until reboot.
Approve? (yes/no): yes

Building...
✓ Rebuild successful
System updated (test mode — revert on restart)
```

### Auto-Install Package (Daemon)

```bash
# Running as daemon with --daemon flag
$ pcopilot --daemon

[Agent detects] Missing development tool
[Proposes] Home Manager install
[Sandbox Check] ✓ Packages are safe
[Auto-Approve] ✓ Applying...
✓ Tool installed

# No user intervention needed for safe operations
```

## 🎯 Next Steps (Phase 4)

- [ ] Actual ChromaDB ingestion with NixOS/HM docs
- [ ] LLM-driven write proposals (agent suggests changes)
- [ ] Installer TUI with write-mode integration
- [ ] Advanced rollback (git-based, per-change)
- [ ] Approval workflows (whitelist, blacklist)

---

**Phase 3 Status:** Write-mode tools with safety gates complete. Agent can now propose and apply system changes with full rollback.
