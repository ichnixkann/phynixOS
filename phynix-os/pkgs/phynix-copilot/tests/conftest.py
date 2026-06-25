import sys
import tempfile
from pathlib import Path

import pytest

# The copilot package isn't installed as a wheel; tests run against the
# source tree directly. Prepend the parent directory so the test imports
# match what cli.py does at runtime.
_PKG_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PKG_ROOT))


@pytest.fixture
def tmp_rag(monkeypatch, tmp_path):
    """Isolate the copilot from the user's $HOME and point RAGIndex
    at a throwaway directory so tests never touch the real index.

    Under the Nix build sandbox HOME=/homeless-shelter, which is
    unwritable; PhynixCopilot.__init__ calls Path.home() to create
    its state dir, so we have to redirect HOME before any test imports
    or instantiates the agent.
    """
    import rag as rag_mod

    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))

    with tempfile.TemporaryDirectory() as tmp:
        orig_init = rag_mod.RAGIndex.__init__
        monkeypatch.setattr(
            rag_mod.RAGIndex,
            "__init__",
            lambda self, db=None: orig_init(self, tmp),
        )
        yield tmp
