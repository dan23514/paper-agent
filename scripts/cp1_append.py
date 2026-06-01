#!/usr/bin/env python3
"""Append verified extra references to the CP1 candidate list and regenerate outputs."""
import json, sys, time, urllib.parse, urllib.request
from pathlib import Path
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
sys.path.insert(0, "scripts")
from config import MAILTO_EMAIL, CROSSREF_BASE

# DOIs to append, with source tag and SJR quartile (verified)
NEW = [
    ("10.1007/s10872-005-0077-4", "added", "Q2"),  # Takikawa & Yoon 2005
    ("10.3389/fmars.2023.1250452", "added", "Q1"),  # Moon et al. 2023
    ("10.1016/j.jmarsys.2022.103750", "added", "Q1"),  # Shin et al. 2022
    ("10.1002/2013JC009327", "added", "Q1"),        # Sasaki et al. 2014
    ("10.1175/jcli4142.1", "added", "Q1"),          # Taguchi et al. 2007
    ("10.1016/j.dsr2.2008.11.036", "added", "Q1"),  # Qiu & Chen 2010
    ("10.5194/os-17-1449-2021", "added", "Q1"),     # Diabaté et al. 2021
]


def enrich(doi):
    url = f"{CROSSREF_BASE}/works/{urllib.parse.quote(doi, safe='')}?mailto={MAILTO_EMAIL}"
    req = urllib.request.Request(url, headers={"User-Agent": f"paper-agent/1.0 (mailto:{MAILTO_EMAIL})"})
    m = json.loads(urllib.request.urlopen(req, timeout=15).read())["message"]
    a = m.get("author") or []
    names = [x.get("family", "") for x in a[:3] if x.get("family")]
    if len(a) > 3:
        names.append("et al.")
    issns = m.get("ISSN") or []
    iy = (m.get("issued") or {}).get("date-parts", [[None]])[0]
    return {
        "doi": doi, "title": (m.get("title") or [""])[0], "authors": "; ".join(names),
        "year": iy[0] if iy else "", "journal": (m.get("container-title") or [""])[0],
        "issn": issns[0] if issns else "", "cited_by": m.get("is-referenced-by-count", 0),
        "oa_url": "", "score": 1.0, "boosted_score": 1.0,
    }


def main():
    proj = Path(sys.argv[1])
    refs = json.loads((proj / "cp1_references.json").read_text(encoding="utf-8"))
    start = len(refs)
    for i, (doi, src, q) in enumerate(NEW, 1):
        r = enrich(doi)
        r["source"] = src
        r["quartile"] = q
        r["id"] = f"R{start + i}"
        refs.append(r)
        print(f"  {r['id']}: {r['authors']} ({r['year']}) {r['journal'][:35]} [{q}]")
        time.sleep(0.2)

    (proj / "cp1_references.json").write_text(json.dumps(refs, ensure_ascii=False, indent=2), encoding="utf-8")
    (proj / "cp1_dois.txt").write_text("\n".join(r["doi"] for r in refs if r.get("doi")), encoding="utf-8")

    lines = ["| ID | Authors | Year | Title | Journal | Quartile | DOI | Score | Source |",
             "|----|---------|------|-------|---------|----------|-----|-------|--------|"]
    for r in refs:
        title = (r.get("title") or "")[:55]
        lines.append(f"| {r['id']} | {r.get('authors','')} | {r.get('year','')} | {title} | "
                     f"{r.get('journal','')[:32]} | {r.get('quartile','?')} | {r.get('doi','')} | "
                     f"{r.get('boosted_score',0):.2f} | {r.get('source','')} |")
    lines.append(f"\n## Summary\n- 合計: {len(refs)} 件（既存10 + 検索12 + レビュー追加{len(NEW)}）")
    (proj / "cp1_references.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"\nAppended {len(NEW)} refs -> total {len(refs)} (R1-R{len(refs)})")


if __name__ == "__main__":
    main()
