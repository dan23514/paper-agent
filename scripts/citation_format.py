#!/usr/bin/env python3
"""Replace [REF: Rx] placeholders with numbered citations and build reference list."""

import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# BibTeX parser (minimal, no external deps)
# ---------------------------------------------------------------------------

def parse_bibtex(bib_text: str) -> dict:
    """Return dict keyed by citekey."""
    entries = {}
    entry_re = re.compile(r"@(\w+)\s*\{\s*(\w+)\s*,([^@]*)\}", re.DOTALL)
    field_re = re.compile(r"(\w+)\s*=\s*\{((?:[^{}]|\{[^{}]*\})*)\}", re.DOTALL)
    for m in entry_re.finditer(bib_text):
        citekey = m.group(2)
        fields = {f.group(1).lower(): f.group(2).strip() for f in field_re.finditer(m.group(3))}
        fields["_type"] = m.group(1).lower()
        entries[citekey] = fields
    return entries


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------

def _author_list(raw: str) -> list:
    return [a.strip() for a in raw.split(" and ") if a.strip()]


def _short_authors(raw: str) -> str:
    authors = _author_list(raw)
    names = []
    for a in authors[:3]:
        names.append(a.split(",")[0].strip() if "," in a else a.split()[-1])
    s = ", ".join(names)
    return s + " et al." if len(authors) > 3 else s


def fmt_ieee(e: dict, n: int) -> str:
    authors = _short_authors(e.get("author", ""))
    year = e.get("year", "")
    title = e.get("title", "")
    journal = e.get("journal", "")
    vol = e.get("volume", "")
    num = e.get("number", "")
    pages = e.get("pages", "")
    doi = e.get("doi", "")
    ref = f"[{n}] {authors}, \"{title},\" "
    if journal:
        ref += f"*{journal}*"
    if vol:
        ref += f", vol. {vol}"
    if num:
        ref += f", no. {num}"
    if pages:
        ref += f", pp. {pages}"
    if year:
        ref += f", {year}"
    if doi:
        ref += f". doi: {doi}"
    return ref + "."


def fmt_apa(e: dict, n: int) -> str:
    authors = _author_list(e.get("author", ""))
    parts = []
    for a in authors:
        if "," in a:
            fam, giv = a.split(",", 1)
            parts.append(f"{fam.strip()}, {giv.strip()[:1]}.")
        else:
            parts.append(a)
    if len(parts) > 20:
        auth_str = ", ".join(parts[:19]) + ", ... " + parts[-1]
    elif len(parts) > 1:
        auth_str = ", ".join(parts[:-1]) + ", & " + parts[-1]
    else:
        auth_str = parts[0] if parts else ""
    year = e.get("year", "n.d.")
    title = e.get("title", "")
    journal = e.get("journal", "")
    vol = e.get("volume", "")
    num = e.get("number", "")
    pages = e.get("pages", "")
    doi = e.get("doi", "")
    ref = f"{auth_str} ({year}). {title}."
    if journal:
        ref += f" *{journal}*"
    if vol:
        ref += f", *{vol}*"
    if num:
        ref += f"({num})"
    if pages:
        ref += f", {pages}"
    ref += "."
    if doi:
        ref += f" https://doi.org/{doi}"
    return ref


def fmt_nature(e: dict, n: int) -> str:
    authors = _short_authors(e.get("author", ""))
    title = e.get("title", "")
    journal = e.get("journal", "")
    vol = e.get("volume", "")
    pages = e.get("pages", "")
    year = e.get("year", "")
    doi = e.get("doi", "")
    ref = f"{n}. {authors}. {title}. *{journal}* **{vol}**, {pages} ({year})."
    if doi:
        ref += f" https://doi.org/{doi}"
    return ref


FORMATTERS = {"ieee": fmt_ieee, "apa": fmt_apa, "nature": fmt_nature,
               "acs": fmt_ieee, "aip": fmt_ieee, "vancouver": fmt_ieee}


# ---------------------------------------------------------------------------
# Main API
# ---------------------------------------------------------------------------

def build_reference_list(bib_entries: dict, ref_id_to_citekey: dict, style: str = "ieee") -> tuple:
    """
    Build numbered reference list.
    ref_id_to_citekey: {'R1': 'smith2024', ...}
    Returns (ref_list_text, {ref_id: number}).
    """
    fmt = FORMATTERS.get(style.lower(), fmt_ieee)
    lines, id_to_num = [], {}
    for i, (rid, citekey) in enumerate(ref_id_to_citekey.items(), 1):
        entry = bib_entries.get(citekey, {})
        lines.append(fmt(entry, i) if entry else f"[{i}] (Entry '{citekey}' not found in BibTeX)")
        id_to_num[rid] = i
    return "\n".join(lines), id_to_num


def replace_ref_ids(text: str, id_to_num: dict) -> str:
    """Replace [REF: R1] with [1]."""
    def sub(m):
        n = id_to_num.get(m.group(1))
        return f"[{n}]" if n else m.group(0)
    return re.sub(r"\[REF:\s*(\w+)\]", sub, text)


def process(draft_text: str, bib_text: str, ref_id_map: dict, style: str = "ieee") -> str:
    """Full pipeline: replace placeholders + append reference list."""
    bib = parse_bibtex(bib_text)
    ref_list, id_to_num = build_reference_list(bib, ref_id_map, style)
    body = replace_ref_ids(draft_text, id_to_num)
    return body + "\n\n## 参考文献\n\n" + ref_list


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: citation_format.py <draft.md> <refs.bib> <id_map.json> [style]")
        sys.exit(1)
    draft = Path(sys.argv[1]).read_text(encoding="utf-8")
    bib = Path(sys.argv[2]).read_text(encoding="utf-8")
    id_map = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))  # noqa: F821
    style = sys.argv[4] if len(sys.argv) > 4 else "ieee"
    import json
    print(process(draft, bib, id_map, style))
