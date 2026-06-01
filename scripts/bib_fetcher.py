#!/usr/bin/env python3
"""Fetch BibTeX entries from CrossRef API by DOI."""

import json
import re
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import MAILTO_EMAIL, CROSSREF_BASE


def _crossref_url(doi: str) -> str:
    return f"{CROSSREF_BASE}/works/{urllib.parse.quote(doi, safe='')}?mailto={MAILTO_EMAIL}"


def _csl_to_bibtex(csl: dict) -> str:
    doi = csl.get("DOI", "")
    titles = csl.get("title") or [""]
    title = titles[0] if titles else ""
    authors = csl.get("author") or []
    year_parts = (csl.get("published") or {}).get("date-parts") or [[None]]
    year = str(year_parts[0][0]) if year_parts and year_parts[0] else ""
    containers = csl.get("container-title") or [""]
    journal = containers[0] if containers else ""
    volume = csl.get("volume", "")
    issue = csl.get("issue", "")
    pages = csl.get("page", "")
    publisher = csl.get("publisher", "")

    # Cite key: firstauthorYYYY
    if authors:
        family = (authors[0].get("family") or authors[0].get("name") or "unknown").lower()
        family = re.sub(r"[^a-z0-9]", "", family)
    else:
        family = "unknown"
    citekey = f"{family}{year}"

    # Author string
    author_parts = []
    for a in authors:
        if "family" in a:
            given = a.get("given", "")
            author_parts.append(f"{a['family']}, {given}".strip(", "))
        else:
            author_parts.append(a.get("name", ""))
    author_str = " and ".join(author_parts)

    # Entry type
    wtype = csl.get("type", "")
    if wtype in ("proceedings-article", "paper-conference"):
        entry_type = "inproceedings"
    elif wtype == "book":
        entry_type = "book"
    elif wtype == "book-chapter":
        entry_type = "incollection"
    else:
        entry_type = "article"

    fields = []
    if author_str:
        fields.append(f"  author    = {{{author_str}}}")
    if title:
        fields.append(f"  title     = {{{title}}}")
    if year:
        fields.append(f"  year      = {{{year}}}")
    if journal:
        fields.append(f"  journal   = {{{journal}}}")
    if volume:
        fields.append(f"  volume    = {{{volume}}}")
    if issue:
        fields.append(f"  number    = {{{issue}}}")
    if pages:
        fields.append(f"  pages     = {{{pages}}}")
    if publisher:
        fields.append(f"  publisher = {{{publisher}}}")
    if doi:
        fields.append(f"  doi       = {{{doi}}}")

    return f"@{entry_type}{{{citekey},\n" + ",\n".join(fields) + "\n}"


def fetch_bib_entry(doi: str, retries: int = 3) -> str | None:
    url = _crossref_url(doi)
    delay = 1.0
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": f"paper-agent/1.0 (mailto:{MAILTO_EMAIL})"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                return _csl_to_bibtex(data.get("message", {}))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code == 429:
                time.sleep(delay)
                delay *= 2
                continue
            return None
        except Exception:
            if attempt < retries - 1:
                time.sleep(delay)
                delay *= 2
    return None


def fetch_all(doi_list: list, output_bib: Path, missing_log: Path) -> dict:
    """Fetch BibTeX for all DOIs. Returns {'success': [...], 'failed': [...]}."""
    success, failed, entries = [], [], []
    for i, doi in enumerate(doi_list):
        print(f"  [{i+1}/{len(doi_list)}] {doi} ...", end=" ", flush=True)
        bib = fetch_bib_entry(doi)
        if bib:
            entries.append(bib)
            success.append(doi)
            print("OK")
        else:
            failed.append(doi)
            print("FAILED")
        if i < len(doi_list) - 1:
            time.sleep(0.15)

    output_bib.write_text("\n\n".join(entries), encoding="utf-8")

    if failed:
        lines = ["# BibTeX 取得失敗 DOI リスト\n",
                 "以下の DOI は CrossRef から取得できませんでした。手動で `cp1_references.bib` に追加してください。\n"]
        for doi in failed:
            lines.append(f"- `{doi}`")
        missing_log.write_text("\n".join(lines), encoding="utf-8")
    else:
        missing_log.write_text("# BibTeX 取得失敗なし\n\n全 DOI の BibTeX を正常に取得しました。\n", encoding="utf-8")

    return {"success": success, "failed": failed}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: bib_fetcher.py <dois.txt> <output.bib> [missing.md]")
        sys.exit(1)
    dois = [d.strip() for d in Path(sys.argv[1]).read_text().splitlines()
            if d.strip() and not d.startswith("#")]
    out = Path(sys.argv[2])
    missing = Path(sys.argv[3]) if len(sys.argv) > 3 else out.parent / "cp1_missing_bibtex.md"
    r = fetch_all(dois, out, missing)
    print(f"\nDone: {len(r['success'])} OK, {len(r['failed'])} failed")
