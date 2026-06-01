#!/usr/bin/env python3
"""Search OpenAlex for relevant papers, apply Q1/Q2 filter and boost, output references_candidates.md."""

import json
import re
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
from collections import Counter
from datetime import datetime
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from config import MAILTO_EMAIL, OPENALEX_BASE
from sjr_filter import filter_q1_q2


# ---------------------------------------------------------------------------
# OpenAlex helpers
# ---------------------------------------------------------------------------

def _openalex_get(url: str) -> dict:
    req = urllib.request.Request(
        url, headers={"User-Agent": f"paper-agent/1.0 (mailto:{MAILTO_EMAIL})"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def search_openalex(query: str, years_back: int = 10, per_page: int = 80) -> list:
    from_year = datetime.now().year - years_back
    params = {
        "search": query,
        "filter": f"publication_year:>{from_year},type:article",
        "select": "id,doi,title,authorships,primary_location,publication_year,cited_by_count,open_access",
        "per-page": min(per_page, 200),
        "sort": "relevance_score:desc",
        "mailto": MAILTO_EMAIL,
    }
    url = f"{OPENALEX_BASE}/works?" + urllib.parse.urlencode(params)
    try:
        data = _openalex_get(url)
        return data.get("results", [])
    except Exception as e:
        print(f"[OpenAlex] search error: {e}", file=sys.stderr)
        return []


def search_by_issn(issn: str, query: str, years_back: int = 10, per_page: int = 20) -> list:
    """Search within a specific journal by ISSN."""
    from_year = datetime.now().year - years_back
    params = {
        "search": query,
        "filter": f"publication_year:>{from_year},primary_location.source.issn:{issn}",
        "select": "id,doi,title,authorships,primary_location,publication_year,cited_by_count,open_access",
        "per-page": per_page,
        "mailto": MAILTO_EMAIL,
    }
    url = f"{OPENALEX_BASE}/works?" + urllib.parse.urlencode(params)
    try:
        data = _openalex_get(url)
        return data.get("results", [])
    except Exception as e:
        print(f"[OpenAlex] ISSN search error ({issn}): {e}", file=sys.stderr)
        return []


# ---------------------------------------------------------------------------
# Work → reference dict conversion
# ---------------------------------------------------------------------------

def _extract_ref(work: dict, source: str = "open") -> dict:
    doi = (work.get("doi") or "").replace("https://doi.org/", "")
    authors = work.get("authorships", []) or []
    names = [a["author"]["display_name"] for a in authors[:3] if a.get("author", {}).get("display_name")]
    if len(authors) > 3:
        names.append("et al.")
    loc = work.get("primary_location") or {}
    src = loc.get("source") or {}
    issn_list = src.get("issn") or []
    oa = work.get("open_access") or {}
    return {
        "doi": doi,
        "title": work.get("title") or "",
        "authors": "; ".join(names),
        "year": work.get("publication_year"),
        "journal": src.get("display_name") or "",
        "issn": issn_list[0] if issn_list else "",
        "cited_by": work.get("cited_by_count") or 0,
        "oa_url": oa.get("oa_url") or "",
        "source": source,
        "score": 0.0,
        "boosted_score": 0.0,
    }


def _normalize_scores(refs: list) -> list:
    n = len(refs)
    for i, r in enumerate(refs):
        r["score"] = round(1.0 - (i / n) * 0.9, 2) if n else 0.0
    return refs


def _apply_boost(refs: list, boost_journals: list, factor: float) -> list:
    if not boost_journals:
        for r in refs:
            r["boosted_score"] = r["score"]
        return refs
    boost_issns = {re.sub(r"[^0-9X]", "", bj.get("issn", "").upper()) for bj in boost_journals}
    boost_names = {bj.get("name", "").lower() for bj in boost_journals}
    for r in refs:
        clean = re.sub(r"[^0-9X]", "", r.get("issn", "").upper())
        jl = r.get("journal", "").lower()
        hit = (clean and clean in boost_issns) or any(bn and (bn in jl or jl in bn) for bn in boost_names)
        if hit:
            r["boosted_score"] = round(r["score"] * factor, 2)
            r["source"] = "target"
        else:
            r["boosted_score"] = r["score"]
    return sorted(refs, key=lambda x: x["boosted_score"], reverse=True)


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

def _dedup(refs: list) -> list:
    seen_doi, seen_title, out = set(), set(), []
    for r in refs:
        doi = r.get("doi", "").strip().lower()
        title_norm = re.sub(r"\s+", " ", (r.get("title") or "").lower()).strip()
        if (doi and doi in seen_doi) or (title_norm and title_norm in seen_title):
            continue
        if doi:
            seen_doi.add(doi)
        if title_norm:
            seen_title.add(title_norm)
        out.append(r)
    return out


# ---------------------------------------------------------------------------
# Candidate selection with ratio guard
# ---------------------------------------------------------------------------

def _select(refs: list, max_candidates: int, reserve_slots: int, max_ratio: float) -> list:
    targets = [r for r in refs if r.get("source") == "target"]
    others = [r for r in refs if r.get("source") != "target"]
    result = []
    # Reserve slots for target journals (if score >= 0.3)
    for r in targets[:reserve_slots]:
        if r.get("boosted_score", 0) >= 0.3:
            result.append(r)
    # Fill remaining slots
    for r in refs:
        if len(result) >= max_candidates:
            break
        if r in result:
            continue
        target_count = sum(1 for x in result if x.get("source") == "target")
        if r.get("source") == "target" and target_count >= int(max_candidates * max_ratio):
            continue
        result.append(r)
    return result


# ---------------------------------------------------------------------------
# Markdown output
# ---------------------------------------------------------------------------

def _to_md(refs: list) -> str:
    lines = [
        "| ID | Authors | Year | Title | Journal | Quartile | DOI | Score | Boosted | Source |",
        "|----|---------|------|-------|---------|----------|-----|-------|---------|--------|",
    ]
    for i, r in enumerate(refs, 1):
        rid = f"R{i}"
        r["id"] = rid
        title = (r.get("title") or "")[:60] + ("…" if len(r.get("title") or "") > 60 else "")
        lines.append(
            f"| {rid} | {r.get('authors','')} | {r.get('year','')} | {title} | "
            f"{r.get('journal','')[:30]} | {r.get('quartile','?')} | {r.get('doi','')} | "
            f"{r.get('score',0):.2f} | {r.get('boosted_score',0):.2f} | {r.get('source','open')} |"
        )
    counts = Counter(r.get("journal", "unknown") for r in refs)
    t_count = sum(1 for r in refs if r.get("source") == "target")
    total = len(refs)
    lines.append("\n## Distribution")
    for j, c in counts.most_common(10):
        lines.append(f"- {j}: {c} / {total}")
    ratio = f"{100 * t_count // total}%" if total else "0%"
    lines.append(f"\n- Target journal ratio: {t_count}/{total} ({ratio})")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 3:
        print("Usage: search_openalex.py <cp0_input.yaml> <config.yaml>")
        sys.exit(1)

    inp = yaml.safe_load(Path(sys.argv[1]).read_text(encoding="utf-8"))
    cfg = yaml.safe_load(Path(sys.argv[2]).read_text(encoding="utf-8"))
    lit = cfg.get("literature", {})

    # Build query
    theme = inp.get("theme", "")
    methods_raw = inp.get("methods", "")
    if isinstance(methods_raw, list):
        methods_str = " ".join(str(m) for m in methods_raw)
    else:
        methods_str = str(methods_raw)
    query = f"{theme} {methods_str}"[:300]

    years_back = lit.get("search_years", 10)
    max_candidates = lit.get("max_candidates", 20)
    openalex_target = lit.get("openalex_target", 30)
    boost_journals = lit.get("boost_journals") or inp.get("config", {}).get("boost_journals", [])
    bypass_sjr = lit.get("bypass_sjr_for_targets", False)
    factor = lit.get("target_boost", 1.5)
    max_ratio = lit.get("max_target_citation_ratio", 0.4)
    reserve_slots = lit.get("reserve_slots", 5)

    # Main search
    print(f"[1/4] Searching OpenAlex: \"{query[:60]}\"...")
    works = search_openalex(query, years_back)
    refs = [_extract_ref(w) for w in works]
    print(f"      {len(refs)} works found")

    # Boost-journal targeted search
    if boost_journals:
        print(f"[2/4] Targeted search for {len(boost_journals)} boost journal(s)...")
        for bj in boost_journals:
            issn = bj.get("issn", "")
            if issn:
                extra = search_by_issn(issn, query, years_back)
                refs += [_extract_ref(w, source="target") for w in extra]
                time.sleep(0.2)
    else:
        print("[2/4] No boost journals specified, skipping.")

    refs = _dedup(refs)
    refs = _normalize_scores(refs)

    # Q1/Q2 filter
    print("[3/4] Applying Q1/Q2 filter...")
    bypass_issns = {bj.get("issn", "") for bj in boost_journals} if bypass_sjr else set()
    refs = filter_q1_q2(refs, bypass_issns=bypass_issns)
    print(f"      {len(refs)} references after Q1/Q2 filter")

    refs = _apply_boost(refs, boost_journals, factor)
    final = _select(refs, max_candidates, reserve_slots, max_ratio)

    # Output
    out_dir = Path(sys.argv[1]).parent
    md_path = out_dir / "cp1_references.md"
    md_path.write_text(_to_md(final), encoding="utf-8")

    json_path = out_dir / "cp1_references.json"
    json_path.write_text(json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8")

    doi_path = out_dir / "cp1_dois.txt"
    doi_path.write_text("\n".join(r["doi"] for r in final if r.get("doi")), encoding="utf-8")

    print(f"[4/4] Done. {len(final)} candidates → {md_path}")


if __name__ == "__main__":
    main()
