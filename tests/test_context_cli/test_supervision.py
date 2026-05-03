"""Tests for the static supervision dashboard."""

import json

from context_cli import adr
from context_cli.indexer import index_doc
from context_cli.supervision import build_snapshot, render_html, write_dashboard


def _patch_runtime(tmp_path, monkeypatch):
    import context_cli.cli as cli_mod

    docs_dir = tmp_path / ".king-context" / "docs"
    research_dir = tmp_path / ".king-context" / "research"
    decisions_dir = tmp_path / ".king-context" / "decisions"

    monkeypatch.setattr(cli_mod, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(cli_mod, "STORE_DIR", docs_dir)
    monkeypatch.setattr(cli_mod, "RESEARCH_STORE_DIR", research_dir)
    monkeypatch.setattr(cli_mod, "DECISIONS_STORE_DIR", decisions_dir)

    return docs_dir, research_dir, decisions_dir


def _write_adr(adr_dir):
    adr_dir.mkdir(parents=True, exist_ok=True)
    path = adr_dir / "0001-adopt-cli-first-architecture.md"
    path.write_text(
        adr.render_adr_markdown(
            adr_id="ADR-0001",
            title="Adopt CLI-first architecture for agent retrieval",
            status="accepted",
            adr_date="2026-05-02",
            areas=["cli", "retrieval", "agents"],
            supersedes=[],
            superseded_by=[],
            related=[],
            supersession_reason="",
            keywords=["cli-first", "authentication", "retrieval"],
            tags=["architecture", "product"],
            context="Agents need explicit, composable retrieval primitives.",
            decision="Use CLI primitives as the primary surface.",
            alternatives="MCP-first workflows.",
            consequences="Docs and decisions should remain inspectable locally.",
        )
    )
    return path


def test_build_snapshot_collects_docs_research_and_decisions(tmp_path, monkeypatch):
    docs_dir, research_dir, _ = _patch_runtime(tmp_path, monkeypatch)

    docs_source = {
        "name": "test-api",
        "display_name": "Test API",
        "version": "v1",
        "base_url": "https://example.com",
        "sections": [
            {
                "title": "Authentication",
                "path": "authentication",
                "url": "https://example.com/auth",
                "keywords": ["authentication", "api-key"],
                "use_cases": ["How to authenticate requests"],
                "tags": ["security", "guide"],
                "priority": 9,
                "content": "Use an API key header for every request.",
            }
        ],
    }
    docs_file = tmp_path / "docs.json"
    docs_file.write_text(json.dumps(docs_source))
    index_doc(docs_file, docs_dir)

    research_source = {
        "name": "agent-memory",
        "display_name": "Agent Memory",
        "version": "v1",
        "base_url": "",
        "sections": [
            {
                "title": "Progressive Retrieval",
                "path": "progressive-retrieval",
                "url": "https://example.com/research/progressive",
                "keywords": ["retrieval", "memory"],
                "use_cases": ["Understand progressive retrieval"],
                "tags": ["architecture", "research"],
                "priority": 7,
                "content": "Research supports progressive retrieval for agents.",
                "source_type": "research",
            }
        ],
    }
    research_file = tmp_path / "research.json"
    research_file.write_text(json.dumps(research_source))
    index_doc(research_file, research_dir)

    _write_adr(tmp_path / ".king-context" / "adr")
    adr.rebuild_index()

    snapshot = build_snapshot()

    assert snapshot["overview"]["doc_corpora"] == 1
    assert snapshot["overview"]["research_corpora"] == 1
    assert snapshot["overview"]["decision_count"] == 1
    assert snapshot["overview"]["section_count"] == 2
    assert snapshot["stores"]["docs"]["corpora"][0]["name"] == "test-api"
    assert snapshot["stores"]["research"]["corpora"][0]["name"] == "agent-memory"
    assert snapshot["decisions"][0]["id"] == "ADR-0001"
    assert any(item["source"] == "decisions" for item in snapshot["search_items"])
    assert snapshot["stores"]["docs"]["corpora"][0]["top_domains"][0]["name"] == "authentication"


def test_build_snapshot_creates_decision_to_corpus_edges(tmp_path, monkeypatch):
    docs_dir, _, _ = _patch_runtime(tmp_path, monkeypatch)

    docs_source = {
        "name": "test-api",
        "display_name": "Test API",
        "version": "v1",
        "base_url": "https://example.com",
        "sections": [
            {
                "title": "Authentication",
                "path": "authentication",
                "url": "https://example.com/auth",
                "keywords": ["authentication", "api-key"],
                "use_cases": ["How to authenticate requests"],
                "tags": ["guide"],
                "priority": 9,
                "content": "Use an API key header for every request.",
            }
        ],
    }
    docs_file = tmp_path / "docs.json"
    docs_file.write_text(json.dumps(docs_source))
    index_doc(docs_file, docs_dir)

    _write_adr(tmp_path / ".king-context" / "adr")
    adr.rebuild_index()

    snapshot = build_snapshot()

    edge_kinds = [edge["kind"] for edge in snapshot["graph"]["edges"]]
    assert "informs" in edge_kinds


def test_render_html_embeds_dashboard_content(tmp_path, monkeypatch):
    _patch_runtime(tmp_path, monkeypatch)
    _write_adr(tmp_path / ".king-context" / "adr")
    adr.rebuild_index()

    html = render_html(build_snapshot())

    assert "King Context Supervision" in html
    assert "Search Inspector" in html
    assert "Decision View" in html
    assert "ADR-0001" in html


def test_snapshot_reads_nested_section_files(tmp_path, monkeypatch):
    docs_dir, _, _ = _patch_runtime(tmp_path, monkeypatch)
    doc_dir = docs_dir / "nested-doc"
    (doc_dir / "sections" / "auth" / "setup").mkdir(parents=True, exist_ok=True)
    (doc_dir / "index.json").write_text(
        json.dumps(
            {
                "name": "nested-doc",
                "display_name": "Nested Doc",
                "version": "v1",
                "base_url": "https://example.com",
                "section_count": 1,
            }
        )
    )
    (doc_dir / "tags.json").write_text(json.dumps({"security": ["auth/setup/login"]}))
    (doc_dir / "keywords.json").write_text(json.dumps({"authentication": ["auth/setup/login"]}))
    (doc_dir / "use_cases.json").write_text(json.dumps({"How to log in": ["auth/setup/login"]}))
    (doc_dir / "sections" / "auth" / "setup" / "login.json").write_text(
        json.dumps(
            {
                "title": "Login Setup",
                "path": "auth/setup/login",
                "url": "https://example.com/login",
                "keywords": ["authentication"],
                "use_cases": ["How to log in"],
                "tags": ["security"],
                "priority": 8,
                "content": "Nested section content for login setup.",
                "token_estimate": 8,
            }
        )
    )

    snapshot = build_snapshot()
    corpus = snapshot["stores"]["docs"]["corpora"][0]
    assert corpus["top_sections"][0]["path"] == "auth/setup/login"
    assert corpus["top_domains"][0]["name"] == "auth"


def test_write_dashboard_writes_html_file(tmp_path, monkeypatch):
    _patch_runtime(tmp_path, monkeypatch)
    _write_adr(tmp_path / ".king-context" / "adr")
    adr.rebuild_index()

    output = tmp_path / "dashboard" / "index.html"
    written = write_dashboard(output)

    assert written == output
    assert output.exists()
    assert "King Context Supervision" in output.read_text(encoding="utf-8")
