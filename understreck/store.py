"""Läser och skriver site/data.js, som sidan läser in."""
from __future__ import annotations

import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "site" / "data.js"
PREFIX = "window.STRYK_ROUNDS = "
HEADER = """/*
  Understreck – omgångsdata. Skrivs automatiskt av GitHub Actions (python -m understreck).
  Fält per match: folk [1,X,2] %, odds [1,X,2], form (äldst först, V/O/F), xg {home:[för,emot], away:[...]},
  injuries {home:[...], away:[...], impact:[0-3,0-3]}, note, valueNote, lineup. Fält som börjar med _ används bara av skriptet.
*/
"""
KEEP_ROUNDS = 8


def load() -> list:
    if not DATA.exists():
        return []
    text = DATA.read_text(encoding="utf-8")
    start = text.index(PREFIX) + len(PREFIX)
    return json.loads(text[start:text.rindex(";")])


def save(rounds: list) -> None:
    rounds = sorted(rounds, key=lambda r: r["id"], reverse=True)[:KEEP_ROUNDS]
    DATA.write_text(HEADER + PREFIX + json.dumps(rounds, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")


def upsert(rounds: list, rnd: dict) -> list:
    return [rnd] + [r for r in rounds if r["id"] != rnd["id"]]
