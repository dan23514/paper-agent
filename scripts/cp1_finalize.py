#!/usr/bin/env python3
"""Apply user edits to CP1 candidate list: drop DOIs, fix years, renumber, regenerate outputs."""

import json
import sys
from pathlib import Path

DROP_DOIS = {
    "10.5670/oceanog.2016.42",   # R16 Indian Ocean salinity
    "10.5670/oceanog.2016.31",   # R17 Krakatau volcano
    "10.5194/sd-31-1-2022",      # R23 scientific drilling monsoon
}
# Fix online-first year -> print year
YEAR_FIX = {
    "10.1007/s10872-020-00563-5": 2021,  # Kida
    "10.1007/s00382-017-3902-8": 2018,   # Terada & Minobe
}


def main():
    proj = Path(sys.argv[1])
    refs = json.loads((proj / "cp1_references.json").read_text(encoding="utf-8"))
    refs = [r for r in refs if r.get("doi") not in DROP_DOIS]
    for r in refs:
        if r["doi"] in YEAR_FIX:
            r["year"] = YEAR_FIX[r["doi"]]
    for i, r in enumerate(refs, 1):
        r["id"] = f"R{i}"

    (proj / "cp1_references.json").write_text(json.dumps(refs, ensure_ascii=False, indent=2), encoding="utf-8")
    (proj / "cp1_dois.txt").write_text("\n".join(r["doi"] for r in refs if r.get("doi")), encoding="utf-8")

    lines = ["| ID | Authors | Year | Title | Journal | Quartile | DOI | Score | Source |",
             "|----|---------|------|-------|---------|----------|-----|-------|--------|"]
    for r in refs:
        title = (r.get("title") or "")[:55]
        lines.append(f"| {r['id']} | {r.get('authors','')} | {r.get('year','')} | {title} | "
                     f"{r.get('journal','')[:32]} | {r.get('quartile','?')} | {r.get('doi','')} | "
                     f"{r.get('boosted_score',0):.2f} | {r.get('source','')} |")
    n_exist = sum(1 for r in refs if r["source"] == "existing")
    n_target = sum(1 for r in refs if r["source"] == "target")
    lines.append(f"\n## Summary\n- 既存（必須）引用: {n_exist}")
    lines.append(f"- ターゲット誌（J. Oceanogr.）: {n_target}")
    lines.append(f"- 通常検索: {len(refs) - n_exist - n_target}")
    lines.append(f"- 合計: {len(refs)}")
    (proj / "cp1_references.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Finalized: {len(refs)} references (R1-R{len(refs)})")


if __name__ == "__main__":
    main()
