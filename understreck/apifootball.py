"""Tabell, form, skador och startelvor från API-Football (api-sports.io).

Gratisnivån ger 100 anrop per dag. En fredagskörning använder ungefär
3 anrop per liga + 1 per match, en lördagskörning 2 per match.
Om gratisnivån inte täcker innevarande säsong kastas ApiFootballError,
och då tar Claude-researchen över.
"""
from __future__ import annotations

import time
from datetime import datetime

from .util import TZ, best_pair, log, ordinal

BASE = "https://v3.football.api-sports.io"
RAPID_HOST = "api-football-v1.p.rapidapi.com"   # samma API om kontot skapades via RapidAPI
MIN_GAP = 6.5  # sekunder mellan anrop, håller oss under gratisnivåns minutgräns

LEAGUE_IDS = {
    "soccer_epl": 39, "soccer_efl_champ": 40, "soccer_england_league1": 41, "soccer_england_league2": 42,
    "soccer_fa_cup": 45, "soccer_england_efl_cup": 48, "soccer_spl": 179,
    "soccer_sweden_allsvenskan": 113, "soccer_sweden_superettan": 114, "soccer_norway_eliteserien": 103,
    "soccer_denmark_superliga": 119, "soccer_germany_bundesliga": 78, "soccer_germany_bundesliga2": 79,
    "soccer_spain_la_liga": 140, "soccer_italy_serie_a": 135, "soccer_france_ligue_one": 61,
    "soccer_netherlands_eredivisie": 88,
}
FINISHED = {"FT", "AET", "PEN"}
REASONS = {"suspended": "avstängd", "red card": "avstängd", "yellow cards": "avstängd",
           "injury": "skadad", "illness": "sjuk", "knock": "känning"}


class ApiFootballError(RuntimeError):
    pass


class ApiFootball:
    def __init__(self, http, key: str):
        self.http, self.key, self._last = http, key.strip(), 0.0
        self.calls = 0
        self.rapid = False

    def _request(self, path, params):
        wait = MIN_GAP - (time.monotonic() - self._last)
        if wait > 0:
            time.sleep(wait)
        if self.rapid:
            url, headers = f"https://{RAPID_HOST}/v3{path}", {"x-rapidapi-key": self.key, "x-rapidapi-host": RAPID_HOST}
        else:
            url, headers = BASE + path, {"x-apisports-key": self.key}
        r = self.http.get(url, params=params, headers=headers, timeout=60)
        self._last = time.monotonic()
        self.calls += 1
        return r

    def get(self, path: str, **params):
        r = self._request(path, params)
        if r.status_code in (401, 403) and not self.rapid:
            log.info("API-Football nekade nyckeln (%s), provar RapidAPI-adressen", r.status_code)
            self.rapid = True
            r = self._request(path, params)
        if r.status_code in (401, 403):
            raise ApiFootballError(
                f"nyckeln nekades ({r.status_code}) både hos api-sports.io och RapidAPI. Kontrollera att "
                "API_FOOTBALL_KEY är rätt kopierad och att kontot är aktiverat (bekräftad e-post).")
        r.raise_for_status()
        j = r.json()
        if j.get("errors"):
            raise ApiFootballError(f"API-Football {path}: {j['errors']}")
        log.debug("API-Football %s – %s anrop kvar i dag", path, r.headers.get("x-ratelimit-requests-remaining", "?"))
        return j.get("response", [])

    def current_season(self, league_id: int) -> int:
        resp = self.get("/leagues", id=league_id, current="true")
        for s in (resp[0]["seasons"] if resp else []):
            if s.get("current"):
                return int(s["year"])
        raise ApiFootballError(f"Ingen aktuell säsong för liga {league_id}")


def _letter(fx, team_id):
    gh, ga = fx["goals"]["home"], fx["goals"]["away"]
    mine, theirs = (gh, ga) if fx["teams"]["home"]["id"] == team_id else (ga, gh)
    return "V" if mine > theirs else ("O" if mine == theirs else "F")


def _record(split):
    return f"{split.get('win', 0)}–{split.get('draw', 0)}–{split.get('lose', 0)}"


def enrich_friday(af: ApiFootball, matches: list, day: datetime) -> None:
    """Fyller i tabell, form, skador och fakta. Lägger API-id:n i m['_src']."""
    by_sport = {}
    for m in matches:
        sport = (m.get("_src") or {}).get("sport")
        if sport in LEAGUE_IDS:
            by_sport.setdefault(sport, []).append(m)

    for sport, ms in by_sport.items():
        league = LEAGUE_IDS[sport]
        season = af.current_season(league)
        fixtures = af.get("/fixtures", league=league, season=season, timezone="Europe/Stockholm")
        table = {}
        for group in (af.get("/standings", league=league, season=season) or [{}])[0].get("league", {}).get("standings", []):
            for row in group:
                table[row["team"]["id"]] = row
        today = [f for f in fixtures if f["fixture"]["date"][:10] == day.strftime("%Y-%m-%d")]
        for m in ms:
            fx = best_pair(m["home"], m["away"], today,
                           lambda f: f["teams"]["home"]["name"], lambda f: f["teams"]["away"]["name"])
            if not fx:
                log.warning("API-Football hittade inte %s – %s", m["home"], m["away"])
                continue
            hid, aid = fx["teams"]["home"]["id"], fx["teams"]["away"]["id"]
            m["_src"].update({"league_id": league, "season": season, "fixture": fx["fixture"]["id"],
                              "home_id": hid, "away_id": aid})
            kick = datetime.fromisoformat(fx["fixture"]["date"])
            played = sorted((f for f in fixtures if f["fixture"]["status"]["short"] in FINISHED
                             and datetime.fromisoformat(f["fixture"]["date"]) < kick), key=lambda f: f["fixture"]["date"])
            form = {}
            for side, tid in (("home", hid), ("away", aid)):
                mine = [f for f in played if tid in (f["teams"]["home"]["id"], f["teams"]["away"]["id"])]
                form[side] = "".join(_letter(f, tid) for f in mine[-5:]) or None
            m["form"] = form
            th, ta = table.get(hid), table.get(aid)
            if th and ta:
                m["table"] = {side: f"{ordinal(t['rank'])}, {t['points']} p ({t['all']['played']} matcher)"
                              for side, t in (("home", th), ("away", ta))}
                m["facts"] = (f"{m['home']} hemma: {_record(th.get('home', {}))} (V–O–F). "
                              f"{m['away']} borta: {_record(ta.get('away', {}))}.")
        log.info("API-Football: %s klar (%d anrop hittills)", sport, af.calls)

    for m in matches:
        if (m.get("_src") or {}).get("fixture"):
            set_injuries(af, m)


def set_injuries(af: ApiFootball, m: dict) -> None:
    src = m["_src"]
    rows = af.get("/injuries", fixture=src["fixture"])
    lists, weight = {"home": [], "away": []}, {"home": 0.0, "away": 0.0}
    for row in rows:
        side = "home" if row["team"]["id"] == src["home_id"] else "away"
        p = row["player"]
        doubtful = (p.get("type") or "").lower().startswith("question")
        reason = REASONS.get((p.get("reason") or "").lower(), (p.get("reason") or "").lower())
        lists[side].append(f"{p['name']} ({'osäker' if doubtful else reason or 'borta'})")
        weight[side] += 0.5 if doubtful else 1.0
    level = lambda w: 0 if w == 0 else (1 if w <= 2 else (2 if w <= 4 else 3))
    m["injuries"] = {"home": lists["home"], "away": lists["away"],
                     "impact": [level(weight["home"]), level(weight["away"])]}


def lineups(af: ApiFootball, m: dict) -> dict | None:
    """Startelvor som {'home': [...], 'away': [...]}, eller None om de inte är släppta."""
    src = m["_src"]
    resp = af.get("/fixtures/lineups", fixture=src["fixture"])
    if len(resp) < 2:
        return None
    out = {}
    for team in resp:
        side = "home" if team["team"]["id"] == src["home_id"] else "away"
        out[side] = [x["player"]["name"] for x in team.get("startXI", [])]
        out[side + "_formation"] = team.get("formation")
    return out
