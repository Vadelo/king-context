"""Static supervision dashboard for indexed King Context stores."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

from context_cli import adr
from context_cli.store import list_docs

SECTION_PREVIEW_WORDS = 70
MAX_TOP_SECTIONS = 6
MAX_TOP_TAGS = 8
MAX_TOP_DOMAINS = 6
MAX_SEARCH_ITEMS_PER_CORPUS = 12


def _runtime_paths() -> tuple[Path, Path, Path, Path]:
    """Return project/store paths, preferring CLI monkeypatched values in tests."""
    import context_cli as base_mod
    import context_cli.cli as cli_mod

    project_root = getattr(cli_mod, "PROJECT_ROOT", base_mod.PROJECT_ROOT)
    docs_store = getattr(cli_mod, "STORE_DIR", base_mod.STORE_DIR)
    research_store = getattr(cli_mod, "RESEARCH_STORE_DIR", base_mod.RESEARCH_STORE_DIR)
    decisions_store = getattr(cli_mod, "DECISIONS_STORE_DIR", base_mod.DECISIONS_STORE_DIR)
    return project_root, docs_store, research_store, decisions_store


def _default_output_file() -> Path:
    project_root, _, _, _ = _runtime_paths()
    return project_root / ".king-context" / "supervision" / "index.html"


def _load_json(path: Path) -> dict[str, Any] | list[Any]:
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def _preview_text(text: str, *, words: int = SECTION_PREVIEW_WORDS) -> str:
    parts = text.split()
    if len(parts) <= words:
        return text
    return " ".join(parts[:words]) + " ..."


def _safe_stat_mtime(path: Path) -> str:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()
    except OSError:
        return ""


def _top_tags(doc_dir: Path) -> list[dict[str, Any]]:
    raw = _load_json(doc_dir / "tags.json")
    if not isinstance(raw, dict):
        return []

    tags = [
        {"tag": tag, "section_count": len(paths)}
        for tag, paths in raw.items()
        if isinstance(paths, list)
    ]
    tags.sort(key=lambda item: (-item["section_count"], item["tag"]))
    return tags[:MAX_TOP_TAGS]


def _top_sections(doc_name: str, doc_dir: Path, source: str) -> list[dict[str, Any]]:
    sections_dir = doc_dir / "sections"
    if not sections_dir.exists():
        return []

    candidates: list[dict[str, Any]] = []
    for section_file in sorted(sections_dir.rglob("*.json")):
        raw = _load_json(section_file)
        if not isinstance(raw, dict):
            continue
        candidates.append(
            {
                "title": raw.get("title", section_file.stem),
                "path": raw.get("path", section_file.stem),
                "priority": raw.get("priority", 0),
                "keywords": raw.get("keywords", []),
                "tags": raw.get("tags", []),
                "token_estimate": raw.get("token_estimate", 0),
                "preview": _preview_text(raw.get("content", "")),
                "source": source,
                "doc_name": doc_name,
            }
        )

    candidates.sort(key=lambda item: (-item["priority"], item["path"]))
    return candidates[:MAX_TOP_SECTIONS]


def _search_items_for_doc(doc_name: str, doc_dir: Path, source: str) -> list[dict[str, Any]]:
    sections_dir = doc_dir / "sections"
    if not sections_dir.exists():
        return []

    items: list[dict[str, Any]] = []
    for section_file in sorted(sections_dir.rglob("*.json")):
        raw = _load_json(section_file)
        if not isinstance(raw, dict):
            continue
        items.append(
            {
                "kind": "section",
                "source": source,
                "corpus": doc_name,
                "title": raw.get("title", section_file.stem),
                "path": raw.get("path", section_file.stem),
                "subtitle": f"{source}:{doc_name}",
                "keywords": raw.get("keywords", []),
                "tags": raw.get("tags", []),
                "use_cases": raw.get("use_cases", []),
                "preview": _preview_text(raw.get("content", "")),
                "priority": raw.get("priority", 0),
                "token_estimate": raw.get("token_estimate", 0),
            }
        )

    items.sort(key=lambda item: (-item["priority"], item["path"]))
    return items[:MAX_SEARCH_ITEMS_PER_CORPUS]


def _top_domains(doc_dir: Path) -> list[dict[str, Any]]:
    sections_dir = doc_dir / "sections"
    if not sections_dir.exists():
        return []

    domains: dict[str, dict[str, Any]] = {}
    for section_file in sorted(sections_dir.rglob("*.json")):
        raw = _load_json(section_file)
        if not isinstance(raw, dict):
            continue

        section_path = str(raw.get("path", section_file.stem))
        domain = section_path.split("/")[0] if "/" in section_path else section_path
        entry = domains.setdefault(
            domain,
            {
                "name": domain,
                "section_count": 0,
                "priority": 0,
                "keywords": set(),
                "tags": set(),
            },
        )
        entry["section_count"] += 1
        entry["priority"] = max(entry["priority"], int(raw.get("priority", 0)))
        entry["keywords"].update(str(value) for value in raw.get("keywords", []))
        entry["tags"].update(str(value) for value in raw.get("tags", []))

    packed = []
    for value in domains.values():
        packed.append(
            {
                "name": value["name"],
                "section_count": value["section_count"],
                "priority": value["priority"],
                "keywords": sorted(value["keywords"])[:8],
                "tags": sorted(value["tags"])[:8],
            }
        )

    packed.sort(key=lambda item: (-item["section_count"], -item["priority"], item["name"]))
    return packed[:MAX_TOP_DOMAINS]


def _collect_store(source: str, store_dir: Path) -> dict[str, Any]:
    corpora: list[dict[str, Any]] = []
    search_items: list[dict[str, Any]] = []

    for info in list_docs(store_dir):
        doc_dir = store_dir / info.name
        corpus = {
            "name": info.name,
            "display_name": info.display_name,
            "version": info.version,
            "base_url": info.base_url,
            "section_count": info.section_count,
            "source": source,
            "indexed_at": _safe_stat_mtime(doc_dir / "index.json"),
            "top_domains": _top_domains(doc_dir),
            "top_tags": _top_tags(doc_dir),
            "top_sections": _top_sections(info.name, doc_dir, source),
        }
        corpora.append(corpus)
        search_items.extend(_search_items_for_doc(info.name, doc_dir, source))

    return {
        "source": source,
        "count": len(corpora),
        "corpora": corpora,
        "search_items": search_items,
    }


def _decision_items() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    decisions = adr._load_indexed_decisions()  # noqa: SLF001 - internal reuse within package
    items: list[dict[str, Any]] = []
    search_items: list[dict[str, Any]] = []

    for decision in decisions:
        preview = _preview_text(decision.get("content", ""))
        entry = {
            "id": decision.get("id", ""),
            "title": decision.get("title", ""),
            "status": decision.get("status", ""),
            "active": bool(decision.get("active", False)),
            "date": decision.get("date", ""),
            "path": decision.get("path", ""),
            "areas": decision.get("areas", []),
            "tags": decision.get("tags", []),
            "keywords": decision.get("keywords", []),
            "supersedes": decision.get("supersedes", []),
            "superseded_by": decision.get("superseded_by", []),
            "related": decision.get("related", []),
            "preview": preview,
            "token_estimate": decision.get("token_estimate", 0),
        }
        items.append(entry)
        search_items.append(
            {
                "kind": "decision",
                "source": "decisions",
                "corpus": "project",
                "title": entry["title"],
                "path": entry["path"],
                "subtitle": f"{entry['id']} ({entry['status']})",
                "keywords": entry["keywords"],
                "tags": entry["tags"] + entry["areas"],
                "use_cases": [],
                "preview": preview,
                "priority": 10 if entry["active"] else 5,
                "token_estimate": entry["token_estimate"],
                "decision_id": entry["id"],
            }
        )

    items.sort(key=lambda item: (not item["active"], item["date"], item["id"]))
    return items, search_items


def _overlap_score(left: set[str], right: set[str]) -> int:
    return len(left & right)


def _architecture_graph(
    docs_store: dict[str, Any],
    research_store: dict[str, Any],
    decisions: list[dict[str, Any]],
) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    seen_nodes: set[str] = set()

    def add_node(node_id: str, *, label: str, kind: str, meta: dict[str, Any] | None = None) -> None:
        if node_id in seen_nodes:
            return
        seen_nodes.add(node_id)
        nodes.append({"id": node_id, "label": label, "kind": kind, "meta": meta or {}})

    for store in (docs_store, research_store):
        for corpus in store["corpora"]:
            corpus_id = f"{corpus['source']}::{corpus['name']}"
            add_node(
                corpus_id,
                label=corpus["display_name"],
                kind="corpus",
                meta={
                    "source": corpus["source"],
                    "section_count": corpus["section_count"],
                    "tags": [item["tag"] for item in corpus["top_tags"]],
                    "domains": [item["name"] for item in corpus.get("top_domains", [])],
                },
            )

            for domain in corpus.get("top_domains", []):
                domain_id = f"domain::{corpus['source']}::{corpus['name']}::{domain['name']}"
                add_node(
                    domain_id,
                    label=domain["name"],
                    kind="domain",
                    meta={
                        "source": corpus["source"],
                        "section_count": domain["section_count"],
                        "priority": domain["priority"],
                    },
                )
                edges.append(
                    {
                        "from": corpus_id,
                        "to": domain_id,
                        "kind": "contains",
                        "label": f"{domain['section_count']} sections",
                    }
                )

            for tag in corpus["top_tags"]:
                tag_id = f"tag::{corpus['source']}::{tag['tag']}"
                add_node(
                    tag_id,
                    label=tag["tag"],
                    kind="tag",
                    meta={"source": corpus["source"], "section_count": tag["section_count"]},
                )
                edges.append(
                    {
                        "from": corpus_id,
                        "to": tag_id,
                        "kind": "covers",
                        "label": f"{tag['section_count']} sections",
                    }
                )

    corpus_tag_sets: dict[str, set[str]] = {}
    for store in (docs_store, research_store):
        for corpus in store["corpora"]:
            corpus_id = f"{corpus['source']}::{corpus['name']}"
            tags = {item["tag"].lower() for item in corpus["top_tags"]}
            tags.update(item["name"].lower() for item in corpus.get("top_domains", []))
            for section in corpus["top_sections"]:
                tags.update(str(value).lower() for value in section.get("keywords", []))
                tags.update(str(value).lower() for value in section.get("tags", []))
            corpus_tag_sets[corpus_id] = tags

    for decision in decisions:
        decision_id = f"decision::{decision['id']}"
        add_node(
            decision_id,
            label=decision["id"],
            kind="decision",
            meta={
                "title": decision["title"],
                "status": decision["status"],
                "active": decision["active"],
            },
        )

        decision_terms = {
            str(value).lower()
            for value in decision["areas"] + decision["tags"] + decision["keywords"]
        }
        for corpus_id, corpus_terms in corpus_tag_sets.items():
            score = _overlap_score(decision_terms, corpus_terms)
            if score <= 0:
                continue
            edges.append(
                {
                    "from": decision_id,
                    "to": corpus_id,
                    "kind": "informs",
                    "label": f"{score} shared signals",
                }
            )

    return {"nodes": nodes, "edges": edges}


def build_snapshot() -> dict[str, Any]:
    """Build a consolidated dashboard snapshot from local stores."""
    project_root, docs_dir, research_dir, _ = _runtime_paths()
    docs_store = _collect_store("docs", docs_dir)
    research_store = _collect_store("research", research_dir)
    decisions, decision_search_items = _decision_items()

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_root": str(project_root),
        "overview": {
            "doc_corpora": docs_store["count"],
            "research_corpora": research_store["count"],
            "decision_count": len(decisions),
            "section_count": sum(c["section_count"] for c in docs_store["corpora"])
            + sum(c["section_count"] for c in research_store["corpora"]),
            "active_decision_count": sum(1 for decision in decisions if decision["active"]),
        },
        "stores": {
            "docs": {"count": docs_store["count"], "corpora": docs_store["corpora"]},
            "research": {
                "count": research_store["count"],
                "corpora": research_store["corpora"],
            },
        },
        "decisions": decisions,
        "graph": _architecture_graph(docs_store, research_store, decisions),
        "search_items": docs_store["search_items"]
        + research_store["search_items"]
        + decision_search_items,
    }


def render_html(snapshot: dict[str, Any]) -> str:
    """Render the static supervision dashboard HTML."""
    snapshot_json = escape(json.dumps(snapshot, ensure_ascii=True))
    generated_at = escape(snapshot["generated_at"])
    project_root = escape(snapshot["project_root"])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>King Context Supervision</title>
  <style>
    :root {{
      --bg: #f3efe7;
      --panel: rgba(255, 255, 255, 0.82);
      --line: rgba(49, 40, 28, 0.14);
      --ink: #251c13;
      --muted: #6b5b4a;
      --accent: #b45309;
      --shadow: 0 18px 50px rgba(77, 58, 29, 0.12);
      --radius: 18px;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Georgia, "Segoe UI", serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(246, 195, 108, 0.45), transparent 28%),
        linear-gradient(180deg, #f8f4ed 0%, var(--bg) 100%);
    }}
    .page {{
      display: grid;
      grid-template-columns: 320px 1fr;
      min-height: 100vh;
    }}
    .sidebar {{
      padding: 24px;
      border-right: 1px solid var(--line);
      background: rgba(255,255,255,0.42);
      backdrop-filter: blur(12px);
      position: sticky;
      top: 0;
      height: 100vh;
      overflow: auto;
    }}
    .brand {{
      margin-bottom: 20px;
      padding-bottom: 20px;
      border-bottom: 1px solid var(--line);
    }}
    .brand h1 {{
      margin: 0 0 8px;
      font-size: 1.75rem;
      line-height: 1;
    }}
    .brand p,
    .nav-item span,
    .meta,
    .footer,
    .panel-header p,
    .detail p {{
      color: var(--muted);
    }}
    .nav-section {{
      margin-top: 22px;
    }}
    .nav-section h2 {{
      margin: 0 0 10px;
      font-size: 0.9rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--muted);
    }}
    .nav-list,
    .decision-list,
    .section-list,
    .edge-list,
    .search-results {{
      display: grid;
      gap: 10px;
    }}
    .nav-item,
    .result,
    .corpus-card,
    .graph-card,
    .decision,
    .detail {{
      border: 1px solid var(--line);
      border-radius: 16px;
      background: rgba(255,255,255,0.82);
    }}
    .nav-item {{
      display: block;
      padding: 10px 12px;
      text-decoration: none;
    }}
    .nav-item strong {{
      display: block;
    }}
    .main {{
      padding: 28px;
      display: grid;
      gap: 24px;
    }}
    .panel {{
      border-radius: 22px;
      border: 1px solid var(--line);
      background: var(--panel);
      box-shadow: var(--shadow);
      overflow: hidden;
    }}
    .hero {{
      padding: 28px;
    }}
    .hero h2 {{
      margin: 0 0 10px;
      font-size: 2rem;
      max-width: 16ch;
      line-height: 1.05;
    }}
    .hero p {{
      margin: 0;
      max-width: 72ch;
      line-height: 1.6;
      color: var(--muted);
    }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 14px;
      margin-top: 22px;
    }}
    .stat {{
      border-radius: 18px;
      padding: 16px;
      background: rgba(37,28,19,0.03);
      border: 1px solid rgba(37,28,19,0.06);
    }}
    .label {{
      color: var(--muted);
      font-size: 0.83rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    .value {{
      margin-top: 8px;
      font-size: 1.9rem;
      font-weight: 700;
    }}
    .panel-header {{
      padding: 20px 22px 12px;
      border-bottom: 1px solid var(--line);
    }}
    .panel-header h3 {{
      margin: 0;
      font-size: 1.2rem;
    }}
    .panel-body {{
      padding: 20px 22px 24px;
    }}
    .search-layout {{
      display: grid;
      grid-template-columns: 1.1fr 0.9fr;
      gap: 18px;
    }}
    #search-input {{
      width: 100%;
      border-radius: 14px;
      border: 1px solid var(--line);
      padding: 14px 16px;
      font: inherit;
      background: rgba(255,255,255,0.9);
    }}
    .result,
    .graph-card,
    .decision,
    .corpus-card,
    .detail {{
      padding: 16px;
    }}
    .result {{
      cursor: pointer;
    }}
    .result small {{
      display: block;
      margin-bottom: 6px;
      color: var(--muted);
    }}
    .detail h4,
    .corpus-card h4,
    .graph-card h4,
    .decision h4 {{
      margin: 0 0 8px;
    }}
    .chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .chip {{
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      padding: 6px 10px;
      background: rgba(37, 28, 19, 0.06);
      font-size: 0.84rem;
    }}
    .corpus-grid,
    .graph-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(290px, 1fr));
      gap: 16px;
    }}
    .section-item {{
      border-left: 3px solid rgba(180, 83, 9, 0.3);
      padding-left: 12px;
    }}
    .submeta {{
      margin-top: 10px;
      margin-bottom: 12px;
      color: var(--muted);
      font-size: 0.92rem;
    }}
    .edge {{
      border: 1px dashed var(--line);
      border-radius: 12px;
      padding: 10px;
      background: rgba(255,255,255,0.7);
    }}
    .footer {{
      text-align: center;
      padding: 10px 0 18px;
      font-size: 0.9rem;
    }}
    @media (max-width: 1080px) {{
      .page {{ grid-template-columns: 1fr; }}
      .sidebar {{
        position: relative;
        height: auto;
        border-right: 0;
        border-bottom: 1px solid var(--line);
      }}
      .search-layout {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <aside class="sidebar">
      <div class="brand">
        <h1>King Context</h1>
        <p>Supervision dashboard for indexed context, corpus structure, and decision memory.</p>
      </div>
      <div class="nav-section">
        <h2>Sections</h2>
        <div class="nav-list">
          <a class="nav-item" href="#overview"><strong>Overview</strong><span>Health of the local knowledge stores</span></a>
          <a class="nav-item" href="#search"><strong>Search Inspector</strong><span>Inspect why a result exists and what it contains</span></a>
          <a class="nav-item" href="#corpora"><strong>Corpus Explorer</strong><span>Browse docs and research corpora</span></a>
          <a class="nav-item" href="#architecture"><strong>Architecture Map</strong><span>See how corpus signals connect to decisions</span></a>
          <a class="nav-item" href="#decisions"><strong>Decision View</strong><span>Read active and historical ADR signals</span></a>
        </div>
      </div>
      <div class="nav-section">
        <h2>Generated</h2>
        <div class="nav-list">
          <div class="nav-item"><strong>{generated_at}</strong><span>Snapshot timestamp (UTC)</span></div>
          <div class="nav-item"><strong>{project_root}</strong><span>Project root used for this dashboard</span></div>
        </div>
      </div>
    </aside>

    <main class="main">
      <section class="panel hero" id="overview">
        <h2>Context supervision for the whole project.</h2>
        <p>This view helps a human or agent understand what context is available, which sections matter most, and which architectural decisions inform the current corpus.</p>
        <div class="stats" id="stats"></div>
      </section>

      <section class="panel" id="search">
        <div class="panel-header">
          <h3>Search Inspector</h3>
          <p>Query the local snapshot and inspect preview, origin, tags, and ranking clues.</p>
        </div>
        <div class="panel-body search-layout">
          <div>
            <input id="search-input" type="search" placeholder="Try: authentication, cli first, prompt engineering, guide">
            <div class="search-results" id="search-results"></div>
          </div>
          <div class="detail" id="detail-panel">
            <h4>Select a result</h4>
            <p>The detail panel shows preview text, keywords, tags, and origin so you can supervise what the store knows before an agent consumes it.</p>
          </div>
        </div>
      </section>

      <section class="panel" id="corpora">
        <div class="panel-header">
          <h3>Corpus Explorer</h3>
          <p>Each corpus exposes its dominant tags and highest-priority sections for quick orientation.</p>
        </div>
        <div class="panel-body">
          <div class="corpus-grid" id="corpus-grid"></div>
        </div>
      </section>

      <section class="panel" id="architecture">
        <div class="panel-header">
          <h3>Architecture Map</h3>
          <p>This first map is signal-based: corpus tags, section keywords, and decision metadata form the lightweight architecture graph.</p>
        </div>
        <div class="panel-body">
          <div class="graph-grid" id="graph-grid"></div>
        </div>
      </section>

      <section class="panel" id="decisions">
        <div class="panel-header">
          <h3>Decision View</h3>
          <p>Active decisions appear first, followed by historical records that still shape the project memory.</p>
        </div>
        <div class="panel-body">
          <div class="decision-list" id="decision-list"></div>
        </div>
      </section>

      <div class="footer">Generated locally from `.king-context/` stores. Read-only by design.</div>
    </main>
  </div>

  <script id="snapshot-data" type="application/json">{snapshot_json}</script>
  <script>
    const snapshot = JSON.parse(document.getElementById('snapshot-data').textContent);

    function renderStats() {{
      const stats = [
        ['Docs corpora', snapshot.overview.doc_corpora],
        ['Research corpora', snapshot.overview.research_corpora],
        ['Sections indexed', snapshot.overview.section_count],
        ['ADRs indexed', snapshot.overview.decision_count],
        ['Active ADRs', snapshot.overview.active_decision_count],
      ];
      document.getElementById('stats').innerHTML = stats.map(([label, value]) => `
        <div class="stat">
          <div class="label">${{label}}</div>
          <div class="value">${{value}}</div>
        </div>
      `).join('');
    }}

    function scoreItem(item, query) {{
      const terms = query.toLowerCase().trim().split(/\\s+/).filter(Boolean);
      if (!terms.length) return item.priority || 0;
      const haystacks = [
        item.title || '',
        item.path || '',
        item.subtitle || '',
        ...(item.keywords || []),
        ...(item.tags || []),
        ...(item.use_cases || []),
        item.preview || '',
      ].map(value => String(value).toLowerCase());
      let score = item.priority || 0;
      for (const term of terms) {{
        for (const value of haystacks) {{
          if (value === term) score += 4;
          else if (value.includes(term)) score += 2;
        }}
      }}
      return score;
    }}

    function showDetail(item) {{
      const keywordChips = (item.keywords || []).map(v => `<span class="chip">${{v}}</span>`).join('');
      const tagChips = (item.tags || []).map(v => `<span class="chip">${{v}}</span>`).join('');
      document.getElementById('detail-panel').innerHTML = `
        <h4>${{item.title}}</h4>
        <p><strong>Origin:</strong> ${{item.source}} / ${{item.corpus}}${{item.subtitle ? ` / ${{item.subtitle}}` : ''}}</p>
        <p>${{item.preview || 'No preview available.'}}</p>
        <p><strong>Path:</strong> ${{item.path || '-'}}</p>
        <p><strong>Tokens:</strong> ${{item.token_estimate || 0}}</p>
        <div class="chips">${{keywordChips || '<span class="chip">No keywords</span>'}}</div>
        <div class="chips" style="margin-top:10px;">${{tagChips || '<span class="chip">No tags</span>'}}</div>
      `;
    }}

    function renderSearch(query = '') {{
      const ranked = [...snapshot.search_items]
        .map(item => ({{ item, score: scoreItem(item, query) }}))
        .filter(entry => !query || entry.score > (entry.item.priority || 0))
        .sort((a, b) => b.score - a.score)
        .slice(0, 14);

      const root = document.getElementById('search-results');
      if (!ranked.length) {{
        root.innerHTML = '<div class="result"><small>No matches</small><strong>Try a shorter technical query</strong></div>';
        return;
      }}

      root.innerHTML = ranked.map((entry, index) => `
        <button class="result" data-index="${{index}}" style="text-align:left;border:none;">
          <small>${{entry.item.source}} / ${{entry.item.corpus}} / score ${{entry.score.toFixed(1)}}</small>
          <strong>${{entry.item.title}}</strong>
          <div class="meta" style="margin-top:6px;">${{entry.item.preview || ''}}</div>
        </button>
      `).join('');

      Array.from(root.querySelectorAll('.result')).forEach((button, index) => {{
        button.addEventListener('click', () => showDetail(ranked[index].item));
      }});

      showDetail(ranked[0].item);
    }}

    function renderCorpora() {{
      const corpora = [
        ...snapshot.stores.docs.corpora,
        ...snapshot.stores.research.corpora,
      ];
      document.getElementById('corpus-grid').innerHTML = corpora.map(corpus => `
        <article class="corpus-card">
          <h4>${{corpus.display_name}}</h4>
          <div class="meta">${{corpus.source}} &middot; ${{corpus.section_count}} sections${{corpus.version ? ` &middot; ${{corpus.version}}` : ''}}</div>
          <div class="chips">
            ${{(corpus.top_tags || []).map(tag => `<span class="chip">${{tag.tag}} &middot; ${{tag.section_count}}</span>`).join('') || '<span class="chip">No tags indexed</span>'}}
          </div>
          <div class="submeta">
            ${{(corpus.top_domains || []).length ? `Domains: ${{corpus.top_domains.map(domain => `${{domain.name}} (${{domain.section_count}})`).join(', ')}}` : 'Domains: not inferred yet'}}
          </div>
          <div class="section-list" style="margin-top:14px;">
            ${{(corpus.top_sections || []).map(section => `
              <div class="section-item">
                <strong>${{section.title}}</strong>
                <div class="meta">${{section.path}} &middot; priority ${{section.priority}}</div>
                <div style="margin-top:6px;">${{section.preview}}</div>
              </div>
            `).join('')}}
          </div>
        </article>
      `).join('');
    }}

    function renderGraph() {{
      const edgesByNode = new Map();
      for (const edge of snapshot.graph.edges) {{
        if (!edgesByNode.has(edge.from)) edgesByNode.set(edge.from, []);
        edgesByNode.get(edge.from).push(edge);
      }}

      const nodes = snapshot.graph.nodes.filter(node => node.kind === 'corpus' || node.kind === 'decision');
      document.getElementById('graph-grid').innerHTML = nodes.map(node => {{
        const edges = edgesByNode.get(node.id) || [];
        const kindLabel = node.kind === 'decision'
          ? node.meta.status
          : `${{node.meta.source}} &middot; ${{node.meta.section_count}} sections`;
        const title = node.kind === 'decision'
          ? `${{node.label}} &middot; ${{node.meta.title}}`
          : node.label;
        const extra = node.kind === 'corpus' && node.meta.domains && node.meta.domains.length
          ? `<div class="submeta">Domains: ${{node.meta.domains.join(', ')}}</div>`
          : '';
        return `
          <article class="graph-card">
            <h4>${{title}}</h4>
            <div class="meta">${{kindLabel}}</div>
            ${{extra}}
            <div class="edge-list" style="margin-top:12px;">
              ${{edges.length ? edges.map(edge => `
                <div class="edge">
                  <strong>${{edge.kind}}</strong><br>
                  ${{edge.label}}
                </div>
              `).join('') : '<div class="edge">No linked signals yet.</div>'}}
            </div>
          </article>
        `;
      }}).join('');
    }}

    function renderDecisions() {{
      document.getElementById('decision-list').innerHTML = snapshot.decisions.map(decision => `
        <article class="decision">
          <div class="meta">${{decision.id}} &middot; ${{decision.status}}${{decision.active ? ' &middot; active' : ''}}${{decision.date ? ` &middot; ${{decision.date}}` : ''}}</div>
          <h4>${{decision.title}}</h4>
          <p>${{decision.preview || 'No preview available.'}}</p>
          <div class="chips">
            ${{(decision.areas || []).map(area => `<span class="chip">${{area}}</span>`).join('')}}
            ${{(decision.tags || []).map(tag => `<span class="chip">${{tag}}</span>`).join('')}}
          </div>
        </article>
      `).join('');
    }}

    document.getElementById('search-input').addEventListener('input', event => {{
      renderSearch(event.target.value);
    }});

    renderStats();
    renderSearch('');
    renderCorpora();
    renderGraph();
    renderDecisions();
  </script>
</body>
</html>
"""


def write_dashboard(output_path: Path | None = None) -> Path:
    """Generate the supervision dashboard HTML and return the written path."""
    snapshot = build_snapshot()
    html = render_html(snapshot)
    target = output_path or _default_output_file()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")
    return target
