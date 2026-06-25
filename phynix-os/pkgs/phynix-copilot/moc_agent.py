"""
PHYNIX Copilot — Master of the Ceremony (MoC) reasoning agent.

This module wires the read-only PHYNIX tools and RAG retrieval into a real
smolagents agent driven by the MoC persona (moc_instructions.MOC_INSTRUCTIONS).

Design notes
------------
* smolagents is imported lazily inside `build_moc_agent` (not at module import
  time) so that environments without smolagents — or with it installed
  --no-deps, as in CI — can still import `agent.py` for the keyword router.
* Tools are thin smolagents `@tool` wrappers around the existing read-only
  NixTools / HyprlandTools / SystemTools and the RAG index. They return JSON
  strings so the agent gets clean, parseable observations.
* The persona is supplied via the `instructions=` parameter, which smolagents
  appends to its built-in system prompt (it does not replace the code/tool
  scaffolding). See moc_instructions.py.
* Small local models (e.g. phi-4-mini over Ollama) get a ToolCallingAgent
  (JSON tool calls) which is more robust for them than CodeAgent's code blobs.
"""

import json
import os
from typing import Any, Optional

from moc_instructions import MOC_INSTRUCTIONS


# ---------------------------------------------------------------------------
# Shared, lazily-initialised RAG index for the doc-search tool
# ---------------------------------------------------------------------------

_RAG = None


def _get_rag():
    global _RAG
    if _RAG is None:
        from rag import RAGIndex
        _RAG = RAGIndex()
    return _RAG


def set_rag_index(rag) -> None:
    """Allow the caller (PhynixCopilot) to share its existing RAG instance."""
    global _RAG
    _RAG = rag


# ---------------------------------------------------------------------------
# Tool factory — built only when smolagents is available
# ---------------------------------------------------------------------------

def _build_tools():
    """Create the smolagents @tool functions. Imports smolagents lazily."""
    from smolagents import tool
    from tools import NixTools, HyprlandTools, SystemTools

    @tool
    def nix_search(query: str) -> str:
        """Search nixpkgs for packages matching a query.

        Args:
            query: Package name or keyword to search for in nixpkgs.
        """
        return json.dumps(NixTools.nix_search(query))

    @tool
    def nix_eval(expr: str) -> str:
        """Evaluate a Nix expression in a pure, read-only way (no imports).

        Args:
            expr: The Nix expression to evaluate, e.g. "1 + 1".
        """
        return json.dumps(NixTools.nix_eval(expr))

    @tool
    def nix_flake_check() -> str:
        """Check the current flake for evaluation errors (read-only)."""
        return json.dumps(NixTools.nix_flake_check())

    @tool
    def nix_store_info(path: Optional[str] = None) -> str:
        """Get Nix store info, or path-info for a specific store path.

        Args:
            path: Optional store path to inspect. If omitted, returns store info.
        """
        return json.dumps(NixTools.nix_store_info(path))

    @tool
    def read_file(path: str) -> str:
        """Read a text file under the user's home directory (max 1MB).

        Args:
            path: Absolute path to the file. Must be inside the home directory.
        """
        return json.dumps(NixTools.read_file(path))

    @tool
    def hyprctl(command: str) -> str:
        """Query Hyprland state via hyprctl (clients, workspaces, monitors, binds).

        Args:
            command: One of "clients", "workspaces", "monitors", "binds".
        """
        return json.dumps(HyprlandTools.hyprctl_command(command))

    @tool
    def systemctl_status(unit: str) -> str:
        """Get the status of a user systemd unit.

        Args:
            unit: The systemd --user unit name, e.g. "phynix-copilot".
        """
        return json.dumps(SystemTools.systemctl_status(unit))

    @tool
    def journalctl_tail(unit: str, lines: int = 20) -> str:
        """Tail recent journal logs for a user systemd unit.

        Args:
            unit: The systemd --user unit name.
            lines: Number of trailing log lines to return (default 20).
        """
        return json.dumps(SystemTools.journalctl_tail(unit, lines))

    @tool
    def search_docs(query: str) -> str:
        """Search the local NixOS / Home Manager / Hyprland documentation index.

        Args:
            query: Natural-language query describing what you need to know.
        """
        results = _get_rag().search(query, top_k=4)
        return json.dumps(results)

    return [
        nix_search,
        nix_eval,
        nix_flake_check,
        nix_store_info,
        read_file,
        hyprctl,
        systemctl_status,
        journalctl_tail,
        search_docs,
    ]


# ---------------------------------------------------------------------------
# Model factory — maps PhynixCopilot's backend string to a smolagents model
# ---------------------------------------------------------------------------

def build_model(backend: str):
    """Return a smolagents model for the detected backend, or None if offline.

    Recognised backends (see PhynixCopilot._detect_lm_backend):
      * hf_inference     -> InferenceClientModel (HF Inference API, HF_TOKEN)
      * ollama_qwen3     -> LiteLLMModel (ollama/qwen3-coder-next)
      * ollama_phi4_mini -> LiteLLMModel (ollama/phi4-mini)
      * offline_mode     -> None
    """
    if backend == "hf_inference":
        from smolagents import InferenceClientModel
        return InferenceClientModel(
            model_id=os.getenv("PHYNIX_HF_MODEL", "Qwen/Qwen2.5-Coder-32B-Instruct"),
            token=os.getenv("HF_TOKEN"),
        )

    if backend in ("ollama_qwen3", "ollama_phi4_mini"):
        from smolagents import LiteLLMModel
        model_name = "qwen3-coder-next" if backend == "ollama_qwen3" else "phi4-mini"
        return LiteLLMModel(
            model_id=f"ollama_chat/{model_name}",
            api_base=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        )

    return None


# ---------------------------------------------------------------------------
# Agent factory
# ---------------------------------------------------------------------------

def build_moc_agent(backend: str):
    """Build the MoC smolagents agent for the given backend.

    Returns a configured agent, or None if the backend is offline or smolagents
    is unavailable. Small models get a ToolCallingAgent; capable models get a
    CodeAgent.
    """
    model = build_model(backend)
    if model is None:
        return None

    from smolagents import CodeAgent, ToolCallingAgent

    tools = _build_tools()

    # Small local models are more reliable with JSON tool calls than code blobs.
    if backend == "ollama_phi4_mini":
        return ToolCallingAgent(
            tools=tools,
            model=model,
            instructions=MOC_INSTRUCTIONS,
            max_steps=8,
        )

    return CodeAgent(
        tools=tools,
        model=model,
        instructions=MOC_INSTRUCTIONS,
        planning_interval=3,
        additional_authorized_imports=["json", "re"],
        max_steps=12,
    )


class MoCAgent:
    """Lazy wrapper so PhynixCopilot can hold a handle without eager imports."""

    def __init__(self, backend: str):
        self.backend = backend
        self._agent = None
        self._unavailable = False

    @property
    def available(self) -> bool:
        return self._ensure() is not None

    def _ensure(self):
        if self._agent is None and not self._unavailable:
            try:
                self._agent = build_moc_agent(self.backend)
            except Exception:
                self._agent = None
            if self._agent is None:
                self._unavailable = True
        return self._agent

    def run(self, query: str, rag_context: str = "") -> dict[str, Any]:
        """Run the agent on a query, optionally seeded with RAG context."""
        agent = self._ensure()
        if agent is None:
            return {
                "available": False,
                "note": f"MoC agent unavailable for backend '{self.backend}'",
            }

        task = query
        if rag_context:
            task = f"{query}\n\n{rag_context}"

        try:
            answer = agent.run(task)
            return {"available": True, "answer": str(answer)}
        except Exception as e:  # never let agent failure crash the CLI
            return {"available": True, "error": str(e)}
