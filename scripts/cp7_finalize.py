#!/usr/bin/env python3
"""CP7: replace [REF: Rx] with APA in-text citations, append reference list, write cp7_final.md."""
import json
import re
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
from citation_format import parse_bibtex, build_reference_list


def author_year_intext(entry: dict) -> str:
    """APA-style (Author, Year) or (Author1 & Author2, Year) or (Author et al., Year)."""
    authors = [a.strip() for a in entry.get("author", "").split(" and ") if a.strip()]
    fams = [a.split(",")[0].strip() if "," in a else a.split()[-1] for a in authors]
    year = entry.get("year", "n.d.")
    if len(fams) == 1:
        name = fams[0]
    elif len(fams) == 2:
        name = f"{fams[0]} & {fams[1]}"
    else:
        name = f"{fams[0]} et al."
    return f"({name}, {year})", (name, year)


def main():
    proj = Path(sys.argv[1])
    draft = (proj / "cp6_draft_v2.md").read_text(encoding="utf-8")
    bib_text = (proj / "cp1_references.bib").read_text(encoding="utf-8")
    refs = json.loads((proj / "cp1_references.json").read_text(encoding="utf-8"))
    bib = parse_bibtex(bib_text)

    # Map R-id -> citekey via DOI match
    doi_to_key = {}
    for key, e in bib.items():
        d = e.get("doi", "").lower()
        if d:
            doi_to_key[d] = key
    id_to_key = {}
    for r in refs:
        d = r.get("doi", "").lower()
        if d in doi_to_key:
            id_to_key[r["id"]] = doi_to_key[d]

    # Only cited ids, in first-appearance order
    cited_order = []
    for m in re.finditer(r"\[REF:\s*(\w+)\]", draft):
        if m.group(1) not in cited_order:
            cited_order.append(m.group(1))

    # Build in-text replacement + collect entries for reference list (APA = alphabetical)
    id_to_intext = {}
    used_entries = {}  # citekey -> entry
    for rid in cited_order:
        key = id_to_key.get(rid)
        if not key:
            id_to_intext[rid] = f"(未解決: {rid})"
            continue
        e = bib[key]
        intext, _ = author_year_intext(e)
        id_to_intext[rid] = intext
        used_entries[key] = e

    # Replace consecutive [REF: a][REF: b] cleanly: collapse adjacent intext citations
    def repl(m):
        return id_to_intext.get(m.group(1), m.group(0))
    body = re.sub(r"\[REF:\s*(\w+)\]", repl, draft)
    # Merge adjacent "(...)( ...)" produced by [REF:a][REF:b]
    body = re.sub(r"\)\s*\(", "; ", body)

    # Remove redundant parenthetical when author is already named narratively
    # in the same sentence, e.g. "Ohshima (1994) は … を示した (Ohshima, 1994)。"
    def dedup_sentence(sent: str) -> str:
        for pm in list(re.finditer(r"\(([^()]+?),\s*(\d{4}|n\.d\.)\)", sent)):
            name, year = pm.group(1).strip(), pm.group(2)
            # narrative form uses a space before the year-paren: "Name (year)"
            narrative = f"{name} ({year})"
            if narrative in sent:
                sent = sent.replace(f" {pm.group(0)}", "", 1).replace(pm.group(0), "", 1)
        return sent
    parts = re.split(r"(。)", body)
    body = "".join(dedup_sentence(p) if i % 2 == 0 else p for i, p in enumerate(parts))

    # APA reference list: alphabetical by first author family, then year
    def sortkey(item):
        key, e = item
        authors = e.get("author", "")
        fam = authors.split(",")[0] if authors else key
        return (fam.lower(), str(e.get("year", "")))
    ordered = sorted(used_entries.items(), key=sortkey)

    # Build APA reference entries
    sys.path.insert(0, "scripts")
    from citation_format import fmt_apa
    ref_lines = []
    for i, (key, e) in enumerate(ordered, 1):
        ref_lines.append(fmt_apa(e, i))

    final = body.rstrip() + "\n\n## References\n\n" + "\n\n".join(ref_lines) + "\n"
    (proj / "cp7_final.md").write_text(final, encoding="utf-8")
    print(f"Cited refs: {len(cited_order)} | resolved: {len(used_entries)} | references listed: {len(ordered)}")
    unresolved = [r for r in cited_order if r not in id_to_key]
    if unresolved:
        print("UNRESOLVED:", unresolved)
    else:
        print("All citations resolved to BibTeX entries.")


if __name__ == "__main__":
    main()
