#!/usr/bin/env python3
"""SJR Q1/Q2 filter — journal quartile lookup using Scimago CSV data."""

import csv
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
from config import SJR_YEAR

DATA_DIR = Path(__file__).parent.parent / "data"


def _ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def _normalize(name: str) -> str:
    name = name.lower()
    name = re.sub(r"[^\w\s]", " ", name)
    return re.sub(r"\s+", " ", name).strip()


def _load_abbr() -> dict:
    p = DATA_DIR / "journal_abbr.json"
    if p.exists():
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _load_sjr(year: int = SJR_YEAR):
    """Return (by_issn, by_norm_title) from SJR CSV. Falls back up to 5 prior years."""
    for y in range(year, year - 6, -1):
        p = DATA_DIR / f"sjr_{y}.csv"
        if p.exists():
            break
    else:
        raise FileNotFoundError(
            f"SJR CSV not found in {DATA_DIR}. "
            "Download from https://www.scimagojr.com/journalrank.php and save as sjr_YYYY.csv"
        )

    by_issn: dict = {}
    by_title: dict = {}
    with open(p, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            q = row.get("SJR Best Quartile", "").strip()
            if q not in ("Q1", "Q2", "Q3", "Q4"):
                continue
            raw_issn = row.get("Issn", "").strip()
            title = row.get("Title", "").strip()
            entry = {"quartile": q, "title": title}
            for issn in re.split(r"[,\s]+", raw_issn):
                clean = re.sub(r"[^0-9X]", "", issn.upper())
                if clean:
                    by_issn[clean] = entry
            norm = _normalize(title)
            if norm:
                by_title[norm] = entry
    return by_issn, by_title


def _issn_lookup(issn: str, by_issn: dict) -> Optional[str]:
    clean = re.sub(r"[^0-9X]", "", issn.upper())
    return by_issn.get(clean, {}).get("quartile")


def _title_lookup(title: str, by_title: dict, abbr: dict, threshold: float = 0.85) -> Optional[str]:
    norm = _normalize(title)
    norm = abbr.get(norm, norm)
    best, best_q = 0.0, None
    for key, entry in by_title.items():
        r = _ratio(norm, key)
        if r > best:
            best, best_q = r, entry["quartile"]
    return best_q if best >= threshold else None


def get_quartile(issn: str = "", title: str = "", year: int = SJR_YEAR) -> Optional[str]:
    """Return SJR quartile string ('Q1'–'Q4') or None if not found."""
    by_issn, by_title = _load_sjr(year)
    abbr = _load_abbr()
    if issn:
        q = _issn_lookup(issn, by_issn)
        if q:
            return q
    if title:
        return _title_lookup(title, by_title, abbr)
    return None


def filter_q1_q2(references: list, bypass_issns: set = None, year: int = SJR_YEAR) -> list:
    """
    Filter a list of reference dicts to Q1/Q2 only.
    Each dict should have 'issn' and/or 'journal' keys.
    Adds 'quartile' key to each passing reference.
    bypass_issns: ISSNs exempt from SJR filter (for boost_journals with bypass_sjr_for_targets).
    """
    by_issn, by_title = _load_sjr(year)
    abbr = _load_abbr()
    bypass = {re.sub(r"[^0-9X]", "", i.upper()) for i in (bypass_issns or set())}
    result = []
    for ref in references:
        issn = ref.get("issn", "")
        title = ref.get("journal", "")
        clean_issn = re.sub(r"[^0-9X]", "", issn.upper()) if issn else ""
        if clean_issn and clean_issn in bypass:
            ref["quartile"] = "bypass"
            result.append(ref)
            continue
        q = _issn_lookup(issn, by_issn) if issn else None
        if not q and title:
            q = _title_lookup(title, by_title, abbr)
        if q in ("Q1", "Q2"):
            ref["quartile"] = q
            result.append(ref)
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: sjr_filter.py <issn_or_title> [year]", file=sys.stderr)
        sys.exit(1)
    arg = sys.argv[1]
    yr = int(sys.argv[2]) if len(sys.argv) > 2 else SJR_YEAR
    q = get_quartile(
        issn=arg if re.match(r"[\dX]{4}-?[\dX]{4}", arg, re.I) else "",
        title="" if re.match(r"[\dX]{4}-?[\dX]{4}", arg, re.I) else arg,
        year=yr,
    )
    print(q or "Not found")
