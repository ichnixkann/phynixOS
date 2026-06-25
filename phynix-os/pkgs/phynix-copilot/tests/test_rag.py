"""End-to-end test that the RAG index builds and serves results.

This replaces the inline RAG smoke test from `.github/workflows/pr-check.yml`.
"""


def test_index_all_produces_chunks(tmp_rag):
    from rag import RAGIndex

    rag = RAGIndex(tmp_rag)
    result = rag.index_all()

    assert result["total_chunks"] > 0
    assert result["nixos_options"]["count"] > 0


def test_search_returns_hits(tmp_rag):
    from rag import RAGIndex

    rag = RAGIndex(tmp_rag)
    rag.index_all()

    hits = rag.search("pipewire audio", top_k=2)
    assert hits, "search returned nothing"
    top = hits[0]
    assert "title" in top
    assert "relevance" in top
