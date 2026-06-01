#!/usr/bin/env python3
"""Extract every sentence containing [REF: Rx] from the draft and build claims.md + results.md."""
import json
import re
import sys
from pathlib import Path


def main():
    proj = Path(sys.argv[1])
    draft = (proj / "cp6_draft_v2_review.md").read_text(encoding="utf-8")
    refs = {r["id"]: r for r in json.loads((proj / "cp1_references.json").read_text(encoding="utf-8"))}

    # Split into sentences on Japanese period, keeping [REF:] tags
    text = re.sub(r"\n+", " ", draft)
    sentences = re.split(r"(?<=。)", text)

    rows = []
    n = 0
    for sent in sentences:
        ids = re.findall(r"\[REF:\s*(\w+)\]", sent)
        if not ids:
            continue
        n += 1
        clean = sent.strip()
        for rid in dict.fromkeys(ids):  # unique, preserve order
            r = refs.get(rid, {})
            label = f"{r.get('authors','?')} ({r.get('year','?')})"
            rows.append((n, rid, label, r.get("doi", ""), clean))

    out = proj / "cp5_factcheck_packet"
    # claims.md
    lines = ["# 引用主張リスト\n",
             "本文中で各文献に帰属させている主張の一覧。NotebookLM で各主張が当該論文に支持されるか検証する。\n",
             "| No. | 引用ID | 著者・年 | DOI | 主張（引用を含む文） |",
             "|-----|--------|----------|-----|----------------------|"]
    for no, rid, label, doi, sent in rows:
        s = sent.replace("|", "／")
        if len(s) > 140:
            s = s[:140] + "…"
        lines.append(f"| {no} | {rid} | {label} | {doi} | {s} |")
    (out / "claims.md").write_text("\n".join(lines), encoding="utf-8")

    # results.md template
    rlines = ["# Factcheck 結果\n",
              "NotebookLM の回答をこの表に転記してください。\n",
              "| No. | 引用ID | Verdict | Evidence | Comment |",
              "|-----|--------|---------|----------|---------|"]
    seen = set()
    for no, rid, label, doi, sent in rows:
        key = (no, rid)
        if key in seen:
            continue
        seen.add(key)
        rlines.append(f"| {no} | {rid} | | | |")
    (out / "results.md").write_text("\n".join(rlines), encoding="utf-8")

    print(f"claims.md: {len(rows)} claim-citation pairs across {n} sentences")
    print(f"distinct refs cited: {len(set(r[1] for r in rows))}")


if __name__ == "__main__":
    main()
