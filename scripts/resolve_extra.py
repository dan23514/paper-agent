#!/usr/bin/env python3
"""Resolve ChatGPT-recommended references via CrossRef, verify, and check SJR quartile."""
import json, sys, time, urllib.parse, urllib.request
from pathlib import Path
sys.path.insert(0, "scripts")
from config import MAILTO_EMAIL, CROSSREF_BASE
from sjr_filter import get_quartile

# (label, author, year, bibliographic hint)
CANDS = [
    ("Takikawa & Yoon 2005", "Takikawa", 2005, "Volume transport Tsushima Strait sea level difference"),
    ("Moon et al. 2023", "Moon", 2023, "non-linear long-term trend volume transport Korea Tsushima Strait"),
    ("Shin et al. 2022", "Shin", 2022, "Tsushima Strait throughflow long-term variability volume transport"),
    ("Sasaki et al. 2014", "Sasaki", 2014, "decadal sea level variability coast Japan ocean circulation"),
    ("Sasaki et al. 2013", "Sasaki", 2013, "Kuroshio Extension meander sea level Japan coast"),
    ("Qiu & Chen 2010", "Qiu", 2010, "Kuroshio Extension low frequency variability Rossby wave wind"),
    ("Taguchi et al. 2007", "Taguchi", 2007, "Kuroshio Extension decadal variability response wind forcing"),
    ("Diabate et al. 2021", "Diabaté", 2021, "western boundary current coastal sea level Northern Hemisphere"),
]


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": f"paper-agent/1.0 (mailto:{MAILTO_EMAIL})"})
    return json.loads(urllib.request.urlopen(req, timeout=20).read())["message"]


def resolve(author, year, hint):
    q = f"{author} {hint}"
    url = (f"{CROSSREF_BASE}/works?query.bibliographic={urllib.parse.quote(q)}"
           f"&query.author={urllib.parse.quote(author)}&rows=5"
           f"&select=DOI,title,author,issued,container-title,ISSN&mailto={MAILTO_EMAIL}")
    items = _get(url).get("items", [])
    surname = author.split()[0].lower().replace("é", "e")
    best, best_score = None, -1
    for it in items:
        iy = (it.get("issued") or {}).get("date-parts", [[None]])[0]
        iy = iy[0] if iy else None
        auth = it.get("author") or []
        am = any(surname in (a.get("family", "").lower().replace("é", "e")) for a in auth)
        score = (2 if iy == year else (1 if iy and abs(iy - year) <= 1 else 0)) + (1 if am else 0)
        if score > best_score:
            best, best_score = it, score
    return best


for label, author, year, hint in CANDS:
    try:
        it = resolve(author, year, hint)
        if not it:
            print(f"[{label}] NOT FOUND"); continue
        doi = it.get("DOI", "")
        title = (it.get("title") or [""])[0]
        iy = (it.get("issued") or {}).get("date-parts", [[None]])[0][0]
        journal = (it.get("container-title") or [""])[0]
        issns = it.get("ISSN") or []
        q = get_quartile(issn=issns[0] if issns else "", title=journal) if journal else None
        print(f"[{label}]\n   DOI: {doi}\n   {iy} | {title[:60]} | {journal[:35]} | SJR={q}")
    except Exception as e:
        print(f"[{label}] ERROR {e}")
    time.sleep(0.3)
