#!/usr/bin/env python3
"""Add a journal abbreviation → full name entry to journal_abbr.json."""

import json
import re
import sys
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
ABBR_FILE = DATA_DIR / "journal_abbr.json"


def normalize(name: str) -> str:
    name = name.lower()
    name = re.sub(r"[^\w\s]", " ", name)
    return re.sub(r"\s+", " ", name).strip()


def add(abbr: str, full: str) -> None:
    data = json.loads(ABBR_FILE.read_text(encoding="utf-8")) if ABBR_FILE.exists() else {}
    key, val = normalize(abbr), normalize(full)
    action = "Updating" if key in data else "Adding"
    data[key] = val
    ABBR_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(f"{action}: '{key}' => '{val}' ({len(data)} entries total)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Usage: add_abbr.py "<abbreviation>" "<full name>"')
        print('Example: add_abbr.py "Nat. Commun." "Nature Communications"')
        sys.exit(1)
    add(sys.argv[1], sys.argv[2])
