"""Smoke tests for the copilot's query router.

Same cases that were previously inline in the GitHub Actions YAML, now
in a real pytest suite that runs identically locally, in `nix flake
check`, and on Hercules CI.
"""

import pytest


@pytest.mark.parametrize(
    "query, expected_tool",
    [
        ("search ripgrep", "nix_search"),
        ("check flake", "nix_flake_check"),
        ("install vim hm", "write_agent"),
    ],
)
def test_route_query(tmp_rag, query, expected_tool):
    from agent import PhynixCopilot

    copilot = PhynixCopilot(interactive=True)
    got = copilot._route_query(query)["tool"]
    assert got == expected_tool, f"{query!r}: expected {expected_tool}, got {got}"


def test_backend_detection_returns_string(tmp_rag):
    from agent import PhynixCopilot

    copilot = PhynixCopilot(interactive=True)
    assert isinstance(copilot.llm_backend, str) and copilot.llm_backend
