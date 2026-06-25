# Phase 1: Copilot Intelligence — Read-Only Tools & RAG

## Objectives

- [x] Smolagents framework setup
- [x] Read-only Nix tools (search, eval, flake-check)
- [x] System introspection tools (journalctl, systemctl)
- [x] Hyprland query tools (safe read-only subset)
- [x] RAG index skeleton (ChromaDB integration)
- [x] CLI interface (`pcopilot` command)
- [x] Audit logging framework
- [x] Package definition (Nix)

## Architecture

### Tools (tools.py)

**NixTools**
- `nix_search(query)` — Search nixpkgs
- `nix_eval(expr)` — Dry-run Nix evaluation
- `nix_flake_check()` — Check flake.nix
- `read_file(path)` — Safe file reading
- `nix_store_info(path)` — Nix store queries

**HyprlandTools**
- `hyprctl_command(cmd)` — Safe subset (clients, workspaces, monitors, binds)

**SystemTools**
- `systemctl_status(unit)` — Check systemd unit
- `journalctl_tail(unit, lines)` — View logs

### RAG (rag.py)

**RAGIndex**
- ChromaDB backend for document storage
- Placeholder indexers for:
  - NixOS options
  - Home Manager docs
  - Hyprland wiki
- `search(query, top_k)` — Vector similarity search
- `build_context(query)` — Format results for agent

### Agent (agent.py)

**PhynixCopilot**
- Query routing to appropriate tools
- LLM backend detection (HF Inference → Ollama → Offline)
- Audit logging (JSONL)
- Interactive mode and daemon mode

### CLI (cli.py)

```bash
# Single query
pcopilot "search git package"

# Interactive mode
pcopilot

# Show audit log
pcopilot --audit-log

# Show LLM backend
pcopilot --backend

# JSON output
pcopilot --json "what packages provide git?"
```

## LLM Backend Routing

1. **HuggingFace Inference API** (requires HF_TOKEN)
   - Remote, reliable, supports streaming
   - Best for production

2. **Ollama Local** (qwen3-coder-next or phi-4-mini)
   - CPU-optimized fallback
   - ~2-3GB RAM for phi-4-mini

3. **Offline Mode**
   - No external requests
   - Cached responses + tool results

## Audit Logging

All queries logged to `~/.local/state/phynix/audit.jsonl`:

```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "action": "query_received",
  "status": "processing",
  "details": { "query": "search ripgrep" }
}
```

## Integration Points

- **Systemd Service:** Runs as user unit, respects session lifetime
- **Package System:** Installable via NixOS module
- **Environment:** HF_TOKEN, PHYNIX_DAEMON env vars

## Next Steps (Phase 2)

- [ ] Implement actual ChromaDB indexing
- [x] Integrate smolagents CodeAgent with tool registration (MoC agent, see moc_agent.py)
- [ ] Add write-mode tools with confirmation gates
- [ ] Home Manager autonomous apply
- [ ] TUI interface (Textual)

## Testing

```bash
# Validate flake
nix flake check

# Build copilot package (if available)
nix build .#phynix-copilot

# Run CLI
python3 -m phynix_copilot.cli "search vim"
```

---

**Phase 1 Status:** Foundation complete. Ready for Phase 2 (write tools + HM autonomy).
