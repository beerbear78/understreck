"""1X2-odds från The Odds API (gratisnivå: 500 krediter per månad).

Varje odds-anrop kostar regioner × marknader = 2 krediter (eu + uk, h2h).
Ligorna provas i tur och ordning och letandet slutar när alla 13 matcher
hittats, så en normal omgång kostar 4–6 krediter.
"""
from __future__ import annotations

import statistics
from datetime import datetime, timedelta, timezone

from .util import TZ, best_pair, log

BASE = "https://api.the-odds-api.com/v4"

# Sport-nyckel hos The Odds API -> ligans namn på sidan. Ordningen är sökordningen.
SPORTS = {
    "soccer_epl": "Premier League",
    "soccer_efl_champ": "Championship",
    "soccer_england_league1": "League One",
    "soccer_england_league2": "League Two",
    "soccer_fa_cup": "FA-cupen",
    "soccer_england_efl_cup": "Ligacupen",
    "soccer_spl": "Skotska Premiership",
    "soccer_sweden_allsvenskan": "Allsvenskan",
    "soccer_sweden_superettan": "Superettan",
    "soccer_norway_eliteserien": "Eliteserien",
    "soccer_denmark_superliga": "Superligaen",
    "soccer_germany_bundesliga": "Bundesliga",
    "soccer_germany_bundesliga2": "2. Bundesliga",
    "soccer_spain_la_liga": "La Liga",
    "soccer_italy_serie_a": "Serie A",
    "soccer_france_ligue_one": "Ligue 1",
    "soccer_netherlands_eredivisie": "Eredivisie",
}


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _median_odds(event) -> list | None:
    home, away = event["home_team"], event["away_team"]
    cols = {home: [], "Draw": [], away: []}
    for bm in event.get("bookmakers", []):
        for market in bm.get("markets", []):
            if market.get("key") != "h2h":
                continue
            for o in market.get("outcomes", []):
                if o.get("name") in cols and isinstance(o.get("price"), (int, float)):
                    cols[o["name"]].append(float(o["price"]))
    if not all(cols.values()):
        return None
    return [round(statistics.median(cols[k]), 2) for k in (home, "Draw", away)]


def fetch_odds(http, api_key: str, matches: list, day: datetime) -> dict:
    """Returnerar {matchnummer: {odds, league, sport, kickoff_dt, bookmakers}}."""
    sports = http.get(f"{BASE}/sports", params={"apiKey": api_key}, timeout=30)  # kostar inga krediter
    sports.raise_for_status()
    active = {s["key"] for s in sports.json() if s.get("active")}

    start = day.astimezone(TZ).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(hours=12)
    params = {"apiKey": api_key, "regions": "eu,uk", "markets": "h2h", "oddsFormat": "decimal",
              "commenceTimeFrom": _iso(start), "commenceTimeTo": _iso(start + timedelta(hours=48))}
    found, left = {}, list(matches)
    for sport, league in SPORTS.items():
        if not left:
            break
        if sport not in active:
            continue
        r = http.get(f"{BASE}/sports/{sport}/odds", params=params, timeout=30)
        if r.status_code in (401, 429):
            log.warning("The Odds API: %s %s", r.status_code, r.text[:200])
            break
        r.raise_for_status()
        events = r.json()
        log.info("The Odds API %s: %d matcher, %s krediter kvar", sport, len(events),
                 r.headers.get("x-requests-remaining", "?"))
        for m in list(left):
            ev = best_pair(m["home"], m["away"], events, lambda e: e["home_team"], lambda e: e["away_team"])
            if not ev:
                continue
            odds = _median_odds(ev)
            found[m["n"]] = {
                "odds": odds, "league": league, "sport": sport,
                "kickoff_dt": datetime.fromisoformat(ev["commence_time"].replace("Z", "+00:00")).astimezone(TZ),
                "bookmakers": len(ev.get("bookmakers", [])),
                "teams": [ev["home_team"], ev["away_team"]],
            }
            left.remove(m)
    for m in left:
        log.warning("Inga odds hittades för %s – %s", m["home"], m["away"])
    return found
