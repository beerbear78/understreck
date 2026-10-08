"""xG (och form) från understat.com för de stora ligorna. Gratis, ingen nyckel."""
from __future__ import annotations

from datetime import datetime

from .util import log, team_sim

LEAGUES = {
    "soccer_epl": "EPL", "soccer_germany_bundesliga": "Bundesliga", "soccer_spain_la_liga": "La_liga",
    "soccer_italy_serie_a": "Serie_A", "soccer_france_ligue_one": "Ligue_1",
}


def season_for(day: datetime) -> int:
    """Understat märker säsongen med startåret: 2026/27 = 2026."""
    return day.year if day.month >= 7 else day.year - 1


def fetch_teams(http, sport: str, day: datetime) -> dict:
    league = LEAGUES[sport]
    season = season_for(day)
    r = http.get(f"https://understat.com/getLeagueData/{league}/{season}", timeout=30, headers={
        "X-Requested-With": "XMLHttpRequest", "Referer": f"https://understat.com/league/{league}/{season}"})
    r.raise_for_status()
    teams = {}
    for t in r.json().get("teams", {}).values():
        hist = [h for h in t.get("history", []) if h.get("date", "") < day.strftime("%Y-%m-%d")]
        if not hist:
            continue
        n = len(hist)
        teams[t["title"]] = {
            "xg": [round(sum(h["xG"] for h in hist) / n, 2), round(sum(h["xGA"] for h in hist) / n, 2)],
            "form": "".join({"w": "V", "d": "O", "l": "F"}[h["result"]] for h in hist[-5:]),
            "played": n,
        }
    return teams


def enrich(http, matches: list, day: datetime) -> None:
    cache = {}
    for m in matches:
        sport = (m.get("_src") or {}).get("sport")
        if sport not in LEAGUES:
            continue
        if sport not in cache:
            try:
                cache[sport] = fetch_teams(http, sport, day)
            except Exception as e:  # understat är en bonus, inte ett krav
                log.warning("understat %s misslyckades: %s", sport, e)
                cache[sport] = {}
        teams = cache[sport]
        if not teams:
            continue
        pick = lambda name: max(teams, key=lambda t: team_sim(name, t))
        th, ta = pick(m["home"]), pick(m["away"])
        if team_sim(m["home"], th) < 0.8 or team_sim(m["away"], ta) < 0.8:
            log.warning("understat hittade inte %s – %s", m["home"], m["away"])
            continue
        m["xg"] = {"home": teams[th]["xg"], "away": teams[ta]["xg"]}
        form = m.get("form") or {}
        if not form.get("home") or not form.get("away"):
            m["form"] = {"home": teams[th]["form"], "away": teams[ta]["form"]}
