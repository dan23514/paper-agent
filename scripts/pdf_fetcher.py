#!/usr/bin/env python3
"""Download OA PDFs for citation papers via OpenAlex OA links."""

import json
import re
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import MAILTO_EMAIL, OPENALEX_BASE


def _safe_name(doi: str) -> str:
    return re.sub(r"[^\w\-]", "_", doi)[:60] + ".pdf"


def _oa_url_from_openalex(doi: str) -> str | None:
    encoded = urllib.parse.quote(f"https://doi.org/{doi}", safe="")
    url = f"{OPENALEX_BASE}/works/{encoded}?select=open_access&mailto={MAILTO_EMAIL}"
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": f"paper-agent/1.0 (mailto:{MAILTO_EMAIL})"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            oa = data.get("open_access") or {}
            return oa.get("oa_url") if oa.get("is_oa") else None
    except Exception:
        return None


def _download(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 paper-agent/1.0"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        # Validate actual PDF magic bytes (reject HTML landing pages served as .pdf)
        if not data[:5].startswith(b"%PDF"):
            return False
        dest.write_bytes(data)
        return True
    except Exception:
        return False


def fetch_all_pdfs(references: list, output_dir: Path) -> dict:
    """
    Download OA PDFs for all references.
    Each ref dict needs 'doi' and 'id' fields.
    Returns {'downloaded': [...], 'missing': [...]}.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    downloaded, missing = [], []

    for ref in references:
        doi = ref.get("doi", "")
        rid = ref.get("id", doi or "unknown")

        if not doi:
            missing.append(ref)
            continue

        fname = f"{rid}_{_safe_name(doi)}"
        dest = output_dir / fname

        if dest.exists():
            print(f"  [{rid}] already exists, skipping")
            ref["pdf_path"] = str(dest)
            downloaded.append(ref)
            continue

        print(f"  [{rid}] {doi} ...", end=" ", flush=True)
        oa_url = _oa_url_from_openalex(doi)

        if oa_url and _download(oa_url, dest):
            print("OK")
            ref["pdf_path"] = str(dest)
            downloaded.append(ref)
        else:
            print("NOT AVAILABLE")
            missing.append(ref)

        time.sleep(0.1)

    return {"downloaded": downloaded, "missing": missing}


def write_missing_list(missing: list, out_path: Path) -> None:
    lines = ["# 手動入手が必要な PDF リスト\n",
             "以下の論文は OA PDF を自動取得できませんでした。",
             "所属機関のアクセスで入手し、`pdfs/` フォルダに配置してください。\n",
             "| ID | 著者 | 年 | タイトル | DOI |",
             "|----|------|----|----------|-----|"]
    for r in missing:
        lines.append(
            f"| {r.get('id','?')} | {r.get('authors','')} | {r.get('year','')} "
            f"| {(r.get('title',''))[:60]} | {r.get('doi','')} |"
        )
    out_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: pdf_fetcher.py <references.json> <output_dir>")
        sys.exit(1)
    refs = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    out_dir = Path(sys.argv[2])
    result = fetch_all_pdfs(refs, out_dir)
    missing_path = out_dir.parent / "missing_pdfs.md"
    write_missing_list(result["missing"], missing_path)
    print(f"\nDownloaded: {len(result['downloaded'])}, Missing: {len(result['missing'])}")
    print(f"Missing list → {missing_path}")
