#!/usr/bin/env python3
"""Report PDF coverage for CITED references and rewrite missing_pdfs.md accordingly."""
import json
import re
import sys
from pathlib import Path


def main():
    proj = Path(sys.argv[1])
    pdfs = proj / "cp5_factcheck_packet" / "pdfs"
    refs = {r["id"]: r for r in json.loads((proj / "cp1_references.json").read_text(encoding="utf-8"))}
    draft = (proj / "cp6_draft_v2_review.md").read_text(encoding="utf-8")
    cited = sorted(set(re.findall(r"\[REF:\s*(\w+)\]", draft)), key=lambda x: int(x[1:]))

    have_ids = set()
    for f in pdfs.glob("*.pdf"):
        m = re.match(r"(R\d+)[_\.]", f.name)
        if m:
            have_ids.add(m.group(1))

    covered, missing = [], []
    for rid in cited:
        (covered if rid in have_ids else missing).append(rid)

    print(f"Cited refs: {len(cited)}  |  with PDF: {len(covered)}  |  missing: {len(missing)}")
    print("Missing:", missing)

    lines = ["# 手動入手が必要な PDF（本文引用分のみ）\n",
             "先行研究フォルダから 12 件をコピー済み、OA 自動取得 2 件。以下は未取得の引用文献です。\n",
             "| ID | 著者 | 年 | タイトル | DOI | 備考 |",
             "|----|------|----|----------|-----|------|"]
    notes = {
        "R4": "教科書（Pedlosky, Ocean Circulation Theory）。NotebookLM 検証は不要—理論の出典として引用のみ。",
        "R20": "Han, Hirose & Kida 2018（地形性 form drag, JGR）。フォルダの Han 2016/2019 とは別論文。",
        "R22": "Yang et al. 2020（風応力, Cont. Shelf Res.）。フォルダの Yang 2024 とは別論文。",
        "R25": "Shin et al. 2022（対馬暖流長期変動, J. Marine Syst.）。",
        "R27": "Taguchi et al. 2007（黒潮続流十年変動, J. Climate）。",
        "R28": "Qiu & Chen 2010（KE 渦-平均流, Deep-Sea Res. II）。フォルダの Qiu 2023/2025 とは別論文。",
        "R29": "Diabaté et al. 2021（西岸境界流と沿岸海面高度, Ocean Science, OA）。",
    }
    for rid in missing:
        r = refs.get(rid, {})
        lines.append(f"| {rid} | {r.get('authors','')} | {r.get('year','')} | "
                     f"{(r.get('title') or '')[:50]} | {r.get('doi','')} | {notes.get(rid,'')} |")
    (proj / "cp5_factcheck_packet" / "missing_pdfs.md").write_text("\n".join(lines), encoding="utf-8")
    print("Rewrote missing_pdfs.md")


if __name__ == "__main__":
    main()
