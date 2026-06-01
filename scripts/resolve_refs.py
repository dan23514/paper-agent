#!/usr/bin/env python3
"""Resolve existing references (author + year + hint) to DOIs via CrossRef bibliographic search."""

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import MAILTO_EMAIL, CROSSREF_BASE


def resolve_one(author: str, year, hint: str) -> dict | None:
    """Query CrossRef and return best-matching work as a reference dict."""
    query = f"{author} {hint}"
    params = {
        "query.bibliographic": query,
        "rows": 5,
        "select": "DOI,title,author,issued,container-title,ISSN",
        "mailto": MAILTO_EMAIL,
    }
    url = f"{CROSSREF_BASE}/works?" + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": f"paper-agent/1.0 (mailto:{MAILTO_EMAIL})"}
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            items = json.loads(resp.read()).get("message", {}).get("items", [])
    except Exception as e:
        print(f"    error: {e}", file=sys.stderr)
        return None

    # Pick the item whose year is closest to target and author surname matches
    target_year = int(year)
    surname = author.split()[0].lower()
    best, best_score = None, -1
    for it in items:
        it_year = None
        issued = (it.get("issued") or {}).get("date-parts") or [[None]]
        if issued and issued[0]:
            it_year = issued[0][0]
        authors = it.get("author") or []
        auth_match = any(surname in (a.get("family", "").lower()) for a in authors)
        year_match = (it_year == target_year)
        score = (2 if year_match else 0) + (1 if auth_match else 0)
        # prefer first (most relevant) on tie
        if score > best_score:
            best, best_score = it, score

    if not best:
        return None

    titles = best.get("title") or [""]
    containers = best.get("container-title") or [""]
    issns = best.get("ISSN") or []
    authors = best.get("author") or []
    names = []
    for a in authors[:3]:
        if a.get("family"):
            names.append(a["family"])
    if len(authors) > 3:
        names.append("et al.")
    issued = (best.get("issued") or {}).get("date-parts") or [[year]]
    yr = issued[0][0] if issued and issued[0] else year

    return {
        "doi": best.get("DOI", ""),
        "title": titles[0] if titles else "",
        "authors": "; ".join(names),
        "year": yr,
        "journal": containers[0] if containers else "",
        "issn": issns[0] if issns else "",
        "cited_by": 0,
        "oa_url": "",
        "source": "existing",
        "score": 1.0,
        "boosted_score": 1.0,
        "quartile": "existing",
    }


def resolve_all(existing_refs: list) -> list:
    out = []
    for ref in existing_refs:
        author = ref.get("author", "")
        year = ref.get("year", "")
        hint = ref.get("hint", "")
        print(f"  Resolving: {author} ({year}) ...", end=" ", flush=True)
        result = resolve_one(author, year, hint)
        if result and result["doi"]:
            print(f"OK -> {result['doi']}")
            result["_query_author"] = author
            result["_query_year"] = year
            out.append(result)
        else:
            print("NOT FOUND")
            out.append({
                "doi": "", "title": f"[UNRESOLVED] {author} ({year})",
                "authors": author, "year": year, "journal": "", "issn": "",
                "source": "existing", "score": 1.0, "boosted_score": 1.0,
                "quartile": "existing", "_query_author": author, "_query_year": year,
            })
        time.sleep(0.3)
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: resolve_refs.py <cp0_input.yaml>")
        sys.exit(1)
    import yaml
    inp = yaml.safe_load(Path(sys.argv[1]).read_text(encoding="utf-8"))
    existing = inp.get("config", {}).get("existing_references", [])
    resolved = resolve_all(existing)
    out_path = Path(sys.argv[1]).parent / "cp1_existing_resolved.json"
    out_path.write_text(json.dumps(resolved, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nResolved {sum(1 for r in resolved if r['doi'])}/{len(resolved)} -> {out_path}")
