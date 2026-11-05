# Tests: Checkpoint 6 retrieval pieces. Offline: fake embedder, fake reranker, no LLM.

import json

import pytest

from app import llm
from app.evals.metrics import score
from app.rag import router
from app.rag.bm25 import BM25, rrf, tokenize
from app.rag.children import split_sentences
from app.rag.strategies import STRATEGIES, run


def test_identifiers_survive_tokenizing():
    tokens = tokenize("What fixed INC-2024-017 and ticket IT-4112?")
    assert "inc-2024-017" in tokens and "it-4112" in tokens and "4112" in tokens
    assert "what" not in tokens  # stopword


def test_bm25_ranks_the_exact_identifier_first():
    texts = ["ticket IT-4120 monitor flickers", "ticket IT-4112 single sign-on token cleared", "VPN profile switched"]
    scores = BM25(texts).scores("how was IT-4112 resolved")
    assert scores.index(max(scores)) == 1


def test_rrf_rewards_items_both_rankings_like():
    fused = [item for item, _ in rrf([["a", "b", "c"], ["b", "c", "a"]])]
    assert fused[0] == "b"


def test_router_sends_list_questions_to_the_lookup():
    rows = [{"text": "Team Directory > X\nname: A; role: Dev; department: Engineering; office: San Francisco"},
            {"text": "Team Directory > Y\nname: B; role: QA; department: Engineering; office: Remote"},
            {"text": "Team Directory > Z\nname: C; role: PM; department: Product; office: San Francisco"}]
    shape, wanted = router.classify("Who works in our San Francisco office?", rows)
    assert shape == "aggregation" and wanted == {"office": ["San Francisco"]}
    assert len(router.lookup(rows, wanted)) == 2
    assert router.classify("Who works remotely?", rows)[1] == {"office": ["Remote"]}
    assert router.classify("Who do I call if I'm locked out?", rows)[0] == "pointwise"


def test_children_are_sentence_sized():
    text = "Code review. Every change needs one reviewer. Billing changes need two reviewers.\nDeploys are automated."
    pieces = split_sentences(text, 60)
    # whole sentences, packed up to the limit, never cut mid-sentence
    assert pieces == ["Code review. Every change needs one reviewer.",
                      "Billing changes need two reviewers. Deploys are automated."]


def test_metrics_count_records_for_list_questions():
    q = {"expect_docs": ["DIR"], "expect_chunks": ["DIR::0", "DIR::1", "DIR::2"]}
    got = [{"id": "DIR::1", "doc_id": "DIR"}, {"id": "X", "doc_id": "X"}, {"id": "DIR::2", "doc_id": "DIR"}]
    s = score(q, got)
    assert s["hit"] and s["rank"] == 1 and s["recall"] == pytest.approx(2 / 3)


@pytest.mark.parametrize("strategy", [s for s in STRATEGIES if s not in ("hyde", "multi_query")])
def test_every_strategy_respects_permissions(friday, events, strategy):
    from app.ingest.sync import run_sync
    run_sync(apply=True)
    friday.apply_event(events[4])  # salary bands: HR and managers only
    run_sync(apply=True)
    result = run(strategy, "salary range for a senior developer", user="intern", k=5)
    assert all(c.get("doc_id") != "HR-SALARY-BANDS-2026" for c in result.chunks)
    assert result.trace


def test_routed_returns_every_matching_record(friday):
    from app.ingest.sync import run_sync
    run_sync(apply=True)
    result = run("routed", "Who works in our San Francisco office?", user="eng-manager", k=5)
    assert len(result.chunks) == 6  # more than k: a list question is not top-k


def test_llm_calls_are_cached_on_disk(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(llm, "LLM_CACHE_FILE", tmp_path / "cache.json")
    monkeypatch.setattr(llm, "_cache", None)
    monkeypatch.setattr(llm, "call_llm", lambda user, system="": calls.append(user) or f"answer to {user}")
    assert llm.cached_call_llm("q1") == "answer to q1"
    assert llm.cached_call_llm("q1") == "answer to q1"
    assert calls == ["q1"]
    assert "answer" in next(iter(json.loads((tmp_path / "cache.json").read_text()).values()))
