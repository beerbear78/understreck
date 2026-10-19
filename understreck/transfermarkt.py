"""Skador och avstängningar från Transfermarkt för ligor som sportsgambler.com inte täcker (League One m.fl.).

Transfermarkts robots.txt tillåter läsning. Ett anrop för ligans klubblista och ett per lag, med paus emellan.
"""
from __future__ import annotations

import re
import time
from datetime import date, datetime

from bs4 import BeautifulSoup

from .util import impact_level, log, team_sim

BASE = "https://www.transfermarkt.com"
LEAGUES = {
    "soccer_england_league1": "/league-one/startseite/wettbewerb/GB3",
    "soccer_england_league2": "/league-two/startseite/wettbewerb/GB4",
    "soccer_spl": "/scottish-premiership/startseite/wettbewerb/SC1",
}
PAUSE = 1.5
REASONS = [
    ("cruciate", "korsband"), ("achilles", "hälsena"), ("hamstring", "baksida lår"), ("knee", "knä"),
    ("ankle", "fotled"), ("calf", "vad"), ("thigh", "lår"), ("groin", "ljumske"), ("foot", "fot"),
    ("back", "rygg"), ("shoulder", "axel"), ("hip", "höft"), ("muscle", "muskel"), ("ill", "sjuk"),
    ("concussion", "hjärnskakning"), ("suspen", "avstängd"), ("red card", "avstängd"),
]
MAX_LISTED = 8


def _get(http, path):
    time.sleep(PAUSE)
    r = http.get(BASE + path, timeout=30)
    r.raise_for_status()
    return BeautifulSoup(r.content, "html.parser")


def clubs(http, league_path) -> dict:
    """Klubbnamn -> sökväg till klubbens skadesida."""
    out = {}
    for a in _get(http, league_path).select('table.items td.hauptlink a[href*="/startseite/verein/"]'):
        m = re.search(r"/([^/]+)/startseite/verein/(\d+)", a.get("href", ""))
        name = a.get_text(strip=True)
        if m and name:
            out[name] = f"/{m.group(1)}/sperrenundverletzungen/verein/{m.group(2)}"
    return out


def _date(s):
    try:
        return datetime.strptime(s.strip(), "%d/%m/%Y").date()
    except ValueError:
        return None


def _int(s):
    try:
        return int(s)
    except ValueError:
        return None


def injuries(http, path) -> list:
    table = _get(http, path).select_one("table.items")
    rows = []
    for tr in (table.select("tbody > tr") if table else []):
        name = tr.select_one("td.hauptlink a")
        cells = [c.get_text(" ", strip=True) for c in tr.find_all("td", recursive=False)]
        if not name or len(cells) < 6:
            continue
        rows.append({"name": name.get_text(strip=True), "reason": cells[2],
                     "until": _date(cells[4]), "missed": _int(cells[5])})
    return rows


def _describe(e) -> str:
    low = e["reason"].lower()
    what = next((sv for en, sv in REASONS if en in low), "skadad")
    return f"{e['name']} ({what})"


def _summarize(rows, match_day: date):
    active = [e for e in rows if not (e["until"] and e["until"] < match_day)]
    # Nyligen skadade väger tyngst; långtidsskadade har laget redan hunnit spela utan (syns i form och odds).
    recent = lambda e: 1.0 if (e["missed"] or 0) <= 2 else (0.5 if (e["missed"] or 0) <= 8 else 0.2)
    active.sort(key=lambda e: e["missed"] or 0)
    names = [_describe(e) for e in active[:MAX_LISTED]]
    if len(active) > MAX_LISTED:
        names.append(f"och {len(active) - MAX_LISTED} till")
    return names, impact_level(sum(recent(e) for e in active))


def enrich(http, matches: list) -> None:
    """Fyller i (och uppdaterar) m['injuries'] för matcher i Transfermarkt-ligorna."""
    lists, club_cache = {}, {}
    for m in matches:
        sport = (m.get("_src") or {}).get("sport")
        if sport not in LEAGUES:
            continue
        try:
            if sport not in club_cache:
                club_cache[sport] = clubs(http, LEAGUES[sport])
                log.info("Transfermarkt %s: %d klubbar", sport, len(club_cache[sport]))
            teams = club_cache[sport]
            day = datetime.fromisoformat(m["_src"]["kickoff"]).date()
            out = {}
            for side in ("home", "away"):
                best = max(teams, key=lambda t: team_sim(m[side], t), default=None)
                if not best or team_sim(m[side], best) < 0.8:
                    raise LookupError(f"hittade inte {m[side]}")
                if best not in lists:
                    lists[best] = injuries(http, teams[best])
                out[side] = _summarize(lists[best], day)
            m["injuries"] = {"home": out["home"][0], "away": out["away"][0],
                             "impact": [out["home"][1], out["away"][1]]}
        except Exception as e:  # skador är en bonus; Claude-researchen tar över om det här misslyckas
            log.warning("Transfermarkt %s – %s: %s", m["home"], m["away"], e)
