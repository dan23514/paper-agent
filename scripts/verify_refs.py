#!/usr/bin/env python3
"""CP3 citation guard: ensure every [REF: Rx] in the draft exists in cp1_references.json."""

import json
import re
import sys
from collections import Counter
from pathlib import Path


def main():
    proj = Path(sys.argv[1])
    draft = (proj / "cp3_draft_v1.md").read_text(encoding="utf-8")
    refs = json.loads((proj / "cp1_references.json").read_text(encoding="utf-8"))
    valid = {r["id"] for r in refs}

    used = re.findall(r"\[REF:\s*(\w+)\]", draft)
    used_counts = Counter(used)
    invalid = sorted(set(used) - valid)

    print(f"Valid IDs available: {len(valid)} (R1-R{len(valid)})")
    print(f"Distinct IDs used in draft: {len(used_counts)}")
    print(f"Total [REF:] occurrences: {len(used)}")
    print(f"Unused candidates: {sorted(valid - set(used), key=lambda x: int(x[1:]))}")
    print("Usage count:")
    for rid in sorted(used_counts, key=lambda x: int(x[1:])):
        print(f"  {rid}: {used_counts[rid]}")
    if invalid:
        print(f"\n*** INVALID IDS (not in candidate list): {invalid} ***")
        sys.exit(1)
    print("\nOK: all citations reference valid candidate IDs.")


if __name__ == "__main__":
    main()
