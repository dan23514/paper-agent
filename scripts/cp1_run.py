#!/usr/bin/env python3
"""CP1 orchestrator: enrich existing refs + OpenAlex supplementary search + Q1/Q2 filter + merge."""

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from config import MAILTO_EMAIL, CROSSREF_BASE
from search_openalex import search_openalex, search_by_issn, _extract_ref, _dedup, _normalize_scores, _apply_boost
from sjr_filter import filter_q1_q2


def enrich_from_crossref(doi: str) -> dict:
    url = f"{CROSSREF_BASE}/works/{urllib.parse.quote(doi, safe='')}?mailto={MAILTO_EMAIL}"
    req = urllib.request.Request(url, headers={"User-Agent": f"paper-agent/1.0 (mailto:{MAILTO_EMAIL})"})
    m = json.loads(urllib.request.urlopen(req, timeout=15).read())["message"]
    authors = m.get("author") or []
    names = [a.get("family", "") for a in authors[:3] if a.get("family")]
    if len(authors) > 3:
        names.append("et al.")
    issns = m.get("ISSN") or []
    issued = (m.get("issued") or {}).get("date-parts", [[None]])[0]
    return {
        "doi": doi,
        "title": (m.get("title") or [""])[0],
        "authors": "; ".join(names),
        "year": issued[0] if issued else "",
        "journal": (m.get("container-title") or [""])[0],
        "issn": issns[0] if issns else "",
        "cited_by": m.get("is-referenced-by-count", 0),
        "oa_url": "",
    }


def main():
    proj = Path(sys.argv[1])  # projects/<name>/checkpoints
    cfg = yaml.safe_load((proj.parent / "config.yaml").read_text(encoding="utf-8"))
    inp = yaml.safe_load((proj / "cp0_input.yaml").read_text(encoding="utf-8"))
    lit = cfg.get("literature", {})

    # --- 1. Enrich existing references ---
    print("[1/5] Enriching existing references from CrossRef...")
    existing_meta = json.loads((proj / "cp1_existing_resolved.json").read_text(encoding="utf-8"))
    existing = []
    for e in existing_meta:
        try:
            full = enrich_from_crossref(e["doi"])
            full.update({"source": "existing", "score": 1.0, "boosted_score": 1.0, "quartile": "existing"})
            existing.append(full)
            print(f"      OK  {e['label']}: {full['journal'][:40]}")
        except Exception as ex:
            print(f"      ERR {e['label']}: {ex}")
        time.sleep(0.2)

    # --- 2. OpenAlex supplementary search (multiple short queries; long queries over-narrow) ---
    queries = [
        "Japan Sea throughflow",
        "Tsushima Strait transport",
        "Japan Sea throughflow climate change",
        "Japan Sea sea level projection CMIP",
        "Kuroshio Extension sea level future projection",
        "coastal sea level trapped waves western boundary",
    ]
    print(f"[2/5] OpenAlex supplementary search ({len(queries)} queries)...")
    supp = []
    for q in queries:
        works = search_openalex(q, lit.get("search_years", 15))
        supp += [_extract_ref(w) for w in works]
        print(f"      \"{q}\": {len(works)}")
        time.sleep(0.2)
    supp = _dedup(supp)
    print(f"      {len(supp)} unique works after merge")

    # Boost-journal targeted search
    boost_journals = lit.get("boost_journals", [])
    for bj in boost_journals:
        if bj.get("issn"):
            extra = search_by_issn(bj["issn"], "Japan Sea throughflow sea level", lit.get("search_years", 15))
            supp += [_extract_ref(w, source="target") for w in extra]
            time.sleep(0.2)

    # --- 3. Q1/Q2 filter on supplementary only ---
    print("[3/5] Applying Q1/Q2 filter to supplementary hits...")
    bypass = {bj.get("issn", "") for bj in boost_journals} if lit.get("bypass_sjr_for_targets") else set()
    supp = filter_q1_q2(supp, bypass_issns=bypass)
    print(f"      {len(supp)} supplementary refs after Q1/Q2 filter")

    # --- 4. Merge (existing first), dedup, score ---
    existing_dois = {e["doi"].lower() for e in existing}
    supp = [s for s in supp if s.get("doi", "").lower() not in existing_dois]
    supp = _dedup(supp)
    supp = _normalize_scores(supp)
    supp = _apply_boost(supp, boost_journals, lit.get("target_boost", 1.5))

    max_supp = lit.get("max_candidates", 25) - len(existing)
    supp = supp[:max(max_supp, 0)]
    final = existing + supp

    # --- 5. Output ---
    for i, r in enumerate(final, 1):
        r["id"] = f"R{i}"

    # Markdown
    lines = ["| ID | Authors | Year | Title | Journal | Quartile | DOI | Score | Source |",
             "|----|---------|------|-------|---------|----------|-----|-------|--------|"]
    for r in final:
        title = (r.get("title") or "")[:55]
        lines.append(f"| {r['id']} | {r.get('authors','')} | {r.get('year','')} | {title} | "
                     f"{r.get('journal','')[:32]} | {r.get('quartile','?')} | {r.get('doi','')} | "
                     f"{r.get('boosted_score',0):.2f} | {r.get('source','')} |")
    n_exist = sum(1 for r in final if r["source"] == "existing")
    n_target = sum(1 for r in final if r["source"] == "target")
    lines.append(f"\n## Summary\n- 既存（必須）引用: {n_exist}")
    lines.append(f"- ターゲット誌（J. Oceanogr.）: {n_target}")
    lines.append(f"- 通常検索: {len(final) - n_exist - n_target}")
    lines.append(f"- 合計: {len(final)}")
    (proj / "cp1_references.md").write_text("\n".join(lines), encoding="utf-8")
    (proj / "cp1_references.json").write_text(json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8")
    (proj / "cp1_dois.txt").write_text("\n".join(r["doi"] for r in final if r.get("doi")), encoding="utf-8")

    print(f"[4/5] Wrote {len(final)} candidates ({n_exist} existing + {len(final)-n_exist} new)")
    print(f"[5/5] Run bib_fetcher next.")


if __name__ == "__main__":
    main()
