"""Rätt rad och utdelning från Svenska Spels öppna resultatdata (ingen nyckel).

/draws/{nummer}/result svarar 404 tills omgången är officiellt avgjord.
"""
from __future__ import annotations

from .util import log

BASE = "https://api.spela.svenskaspel.se/draw/1/stryktipset/draws"


def _amount(s) -> float | None:
    try:
        return float(str(s).replace(" ", "").replace(",", "."))
    except ValueError:
        return None


def parse_result(data: dict) -> dict:
    res = data["result"]
    events = sorted(res.get("events", []), key=lambda e: e["eventNumber"])
    scores = []
    for e in events:
        sc = e.get("outcomeScore") or {}
        scores.append(f"{sc['home']}–{sc['away']}" if sc.get("home") is not None and sc.get("away") is not None else None)
    payouts = [{"name": d.get("name"), "winners": d.get("winners"), "amount": _amount(d.get("amount"))}
               for d in sorted(res.get("distribution", []), key=lambda d: d.get("winDiv", 0))]
    return {
        "final": True,
        "row": [e.get("outcome") if not e.get("cancelled") else None for e in events],
        "scores": scores,
        "payouts": payouts,
    }


def fetch_result(http, draw) -> dict | None:
    """Officiell rätt rad + utdelning, eller None om omgången inte är avgjord än."""
    if not draw:
        return None
    r = http.get(f"{BASE}/{draw}/result", timeout=30)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    out = parse_result(r.json())
    log.info("Svenska Spel: officiellt resultat för omgång %s: %s", draw, "".join(x or "-" for x in out["row"]))
    return out
