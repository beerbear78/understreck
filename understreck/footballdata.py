"""Tabell, form och hemma/borta-facit från football-data.org (gratis för PL och Championship m.fl.).

Gratisnivån tillåter 10 anrop per minut. Varje liga kostar två anrop (tabell + spelade matcher).
League One ingår inte gratis; de matcherna fylls i av Claude-researchen.
"""
from __future__ import annotations

import time
from datetime import datetime

from .util import log, ordinal, team_sim

BASE = "https://api.football-data.org/v4"
MIN_GAP = 6.5
CODES = {
    "soccer_epl": "PL", "soccer_efl_champ": "ELC", "soccer_germany_bundesliga": "BL1",
    "soccer_spain_la_liga": "PD", "soccer_italy_serie_a": "SA", "soccer_france_ligue_one": "FL1",
    "soccer_netherlands_eredivisie": "DED",
}


class FootballData:
    def __init__(self, http, key: str):
        self.http, self.key, self._last = http, key.strip(), 0.0

    def get(self, path: str, **params) -> dict:
        for attempt in range(2):
            wait = MIN_GAP - (time.monotonic() - self._last)
            if wait > 0:
                time.sleep(wait)
            r = self.http.get(BASE + path, params=params, headers={"X-Auth-Token": self.key}, timeout=60)
            self._last = time.monotonic()
            if r.status_code == 429 and attempt == 0:
                log.info("football-data.org: för många anrop, väntar en minut")
                time.sleep(61)
                continue
            r.raise_for_status()
            return r.json()
        return {}


def _letter(match, team_id):
    ft = match["score"]["fullTime"]
    mine, theirs = (ft["home"], ft["away"]) if match["homeTeam"]["id"] == team_id else (ft["away"], ft["home"])
    return "V" if mine > theirs else ("O" if mine == theirs else "F")


def _record(row):
    return f"{row['won']}–{row['draw']}–{row['lost']}" if row else "–"


def _find(name, rows):
    best = max(rows, key=lambda r: max(team_sim(name, r["team"]["name"]), team_sim(name, r["team"].get("shortName") or "")),
               default=None)
    if best and max(team_sim(name, best["team"]["name"]), team_sim(name, best["team"].get("shortName") or "")) >= 0.8:
        return best
    return None


def _tables_from_matches(played) -> dict:
    """Räknar fram TOTAL/HOME/AWAY-tabeller ur spelade matcher (reserv om tabellanropet inte räcker)."""
    rows = {"TOTAL": {}, "HOME": {}, "AWAY": {}}
    for x in played:
        ft = x["score"]["fullTime"]
        if ft.get("home") is None or ft.get("away") is None:
            continue
        for side, team, gf, ga in (("HOME", x["homeTeam"], ft["home"], ft["away"]),
                                   ("AWAY", x["awayTeam"], ft["away"], ft["home"])):
            for typ in ("TOTAL", side):
                r = rows[typ].setdefault(team["id"], {"team": team, "won": 0, "draw": 0, "lost": 0,
                                                      "points": 0, "playedGames": 0, "gd": 0, "gf": 0})
                r["playedGames"] += 1
                r["gf"] += gf
                r["gd"] += gf - ga
                if gf > ga:
                    r["won"] += 1; r["points"] += 3
                elif gf == ga:
                    r["draw"] += 1; r["points"] += 1
                else:
                    r["lost"] += 1
    out = {}
    for typ, d in rows.items():
        out[typ] = sorted(d.values(), key=lambda r: (-r["points"], -r["gd"], -r["gf"]))
        for i, r in enumerate(out[typ], 1):
            r["position"] = i
    return out


def enrich(fd: FootballData, matches: list) -> None:
    """Fyller i tabell, form och fakta för matcher som saknar dem."""
    by_code = {}
    for m in matches:
        code = CODES.get((m.get("_src") or {}).get("sport"))
        if code and (not m.get("table") or not (m.get("form") or {}).get("home")):
            by_code.setdefault(code, []).append(m)

    for code, ms in by_code.items():
        try:
            st = fd.get(f"/competitions/{code}/standings")
            played = fd.get(f"/competitions/{code}/matches", status="FINISHED").get("matches", [])
        except Exception as e:  # en liga som strular ska inte stoppa resten
            log.warning("football-data.org %s misslyckades: %s", code, e)
            continue
        tables = {}
        for s in st.get("standings", []):
            if s.get("type") and s.get("table") and s["type"] not in tables:
                tables[s["type"]] = s["table"]
        log.info("football-data.org %s: tabeller %s, %d spelade matcher",
                 code, {k: len(v) for k, v in tables.items()} or "inga", len(played))
        computed = _tables_from_matches(played)
        played.sort(key=lambda x: x["utcDate"])
        for m in ms:
            src = tables
            th, ta = _find(m["home"], tables.get("TOTAL", [])), _find(m["away"], tables.get("TOTAL", []))
            if not th or not ta:
                src = computed
                th, ta = _find(m["home"], computed["TOTAL"]), _find(m["away"], computed["TOTAL"])
            # Gratisnivån skickar bara TOTAL-tabellen; hemma/borta räknas då fram ur matcherna.
            by_id = lambda typ: {r["team"]["id"]: r for r in (src.get(typ) or computed[typ])}
            home_rows, away_rows = by_id("HOME"), by_id("AWAY")
            if not th or not ta:
                log.warning("football-data.org hittade inte %s – %s i %s", m["home"], m["away"], code)
                continue
            m["table"] = {side: f"{ordinal(r['position'])}, {r['points']} p ({r['playedGames']} matcher)"
                          for side, r in (("home", th), ("away", ta))}
            kick = datetime.fromisoformat(m["_src"]["kickoff"])
            form = {}
            for side, row in (("home", th), ("away", ta)):
                tid = row["team"]["id"]
                mine = [x for x in played if tid in (x["homeTeam"]["id"], x["awayTeam"]["id"])
                        and datetime.fromisoformat(x["utcDate"].replace("Z", "+00:00")) < kick]
                form[side] = "".join(_letter(x, tid) for x in mine[-5:]) or None
            if form["home"] and form["away"]:
                m["form"] = form
            m["facts"] = (f"{m['home']} hemma: {_record(home_rows.get(th['team']['id']))} (V–O–F). "
                          f"{m['away']} borta: {_record(away_rows.get(ta['team']['id']))}.")
        log.info("football-data.org: %s klar", code)
