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
def tmp_rag(monkeypatch):
    """Point RAGIndex at a throwaway directory so tests never touch
    the user's real index."""
    import rag as rag_mod

    with tempfile.TemporaryDirectory() as tmp:
        orig_init = rag_mod.RAGIndex.__init__
        monkeypatch.setattr(
            rag_mod.RAGIndex,
            "__init__",
            lambda self, db=None: orig_init(self, tmp),
        )
        yield tmp
