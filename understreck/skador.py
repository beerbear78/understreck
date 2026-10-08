"""Skador och avstängningar från sportsgambler.com (gratis, tillåtet i deras robots.txt).

En sida per liga listar alla lag. För varje spelare finns typ (skadad / osäker / avstängd),
orsak, antal matcher spelaren spelat i år och beräknad återkomst.
"""
from __future__ import annotations

from datetime import date, datetime

from bs4 import BeautifulSoup

from .util import impact_level, log, team_sim

URL = "https://www.sportsgambler.com/injuries/football/{}/"
PAGES = {
    "soccer_epl": "england-premier-league", "soccer_efl_champ": "england-championship",
    "soccer_fa_cup": "england-fa-cup", "soccer_england_efl_cup": "england-efl-cup",
    "soccer_sweden_allsvenskan": "sweden-allsvenskan", "soccer_norway_eliteserien": "norway-eliteserien",
    "soccer_denmark_superliga": "denmark-superliga", "soccer_germany_bundesliga": "germany-bundesliga",
    "soccer_germany_bundesliga2": "germany-2-bundesliga", "soccer_spain_la_liga": "spain-la-liga",
    "soccer_italy_serie_a": "italy-serie-a", "soccer_france_ligue_one": "france-ligue-1",
}
REASONS = {
    "muscle": "muskel", "knee": "knä", "ankle": "fotled", "calf": "vad", "thigh": "lår", "hamstring": "baksida lår",
    "groin": "ljumske", "foot": "fot", "back": "rygg", "shoulder": "axel", "hip": "höft", "illness": "sjuk",
    "achilles": "hälsena", "cruciate ligame": "korsband", "concussion": "hjärnskakning", "head": "huvud",
    "toe": "tå", "wrist": "handled", "hand": "hand", "arm": "arm", "leg": "ben", "knock": "känning",
}
MAX_LISTED = 8


def _int(s):
    try:
        return int(s)
    except (TypeError, ValueError):
        return None


def _date(s):
    try:
        return date.fromisoformat(s)
    except (TypeError, ValueError):
        return None


def fetch_league(http, slug: str) -> dict:
    r = http.get(URL.format(slug), timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.content, "html.parser")
    teams = {}
    for block in soup.select("div.injury-block"):
        title = block.select_one("h3.injuries-title")
        if not title:
            continue
        rows = []
        for row in block.select("div.inj-row"):
            pick = lambda cls: (row.select_one(f"span.{cls}").get_text(strip=True) if row.select_one(f"span.{cls}") else "")
            kind = " ".join(row.select_one("span.inj-type").get("class", [])) if row.select_one("span.inj-type") else ""
            status = "susp" if "redcard" in kind else ("doubt" if "questionmark" in kind else "out")
            rows.append({"name": pick("inj-player"), "status": status, "reason": pick("inj-info"),
                         "matches": _int(pick("inj-game")), "back": _date(pick("inj-return"))})
        teams[title.get_text(strip=True)] = rows
    return teams


def _describe(e) -> str:
    if e["status"] == "susp":
        what = "avstängd"
    elif e["status"] == "doubt":
        what = "osäker"
    else:
        what = REASONS.get(e["reason"].lower(), "skadad") if e["reason"] and e["reason"] != "Other" else "skadad"
    return f"{e['name']} ({what})"


def _summarize(rows, match_day: date):
    """Listar frånvarande (frånvarande först, sedan osäkra) och räknar påverkan 0–3."""
    active = [e for e in rows if not (e["back"] and e["back"] < match_day)]
    active.sort(key=lambda e: (e["status"] == "doubt", -(e["matches"] or 0)))
    # Ordinarie spelare (3+ matcher i år) väger tyngst; långtidsskadade som inte spelat alls påverkar
    # knappt, eftersom laget redan har spelat utan dem (och det syns i form och xG).
    regular = lambda e: 1.0 if (e["matches"] or 0) >= 3 else (0.5 if (e["matches"] or 0) >= 1 else 0.2)
    weight = sum((0.5 if e["status"] == "doubt" else 1.0) * regular(e) for e in active)
    names = [_describe(e) for e in active[:MAX_LISTED]]
    if len(active) > MAX_LISTED:
        names.append(f"och {len(active) - MAX_LISTED} till")
    return names, impact_level(weight)


def enrich(http, matches: list) -> None:
    """Skriver m['injuries'] för matcher i ligor som sportsgambler täcker."""
    cache = {}
    for m in matches:
        slug = PAGES.get((m.get("_src") or {}).get("sport"))
        if not slug:
            continue
        if slug not in cache:
            try:
                cache[slug] = fetch_league(http, slug)
                log.info("sportsgambler %s: %d lag", slug, len(cache[slug]))
            except Exception as e:  # skador är en bonus, inte ett krav
                log.warning("sportsgambler %s misslyckades: %s", slug, e)
                cache[slug] = {}
        teams = cache[slug]
        if not teams:
            continue
        day = datetime.fromisoformat(m["_src"]["kickoff"]).date()
        out = {}
        for side in ("home", "away"):
            best = max(teams, key=lambda t: team_sim(m[side], t))
            if team_sim(m[side], best) < 0.8:
                break
            out[side] = _summarize(teams[best], day)
        else:
            m["injuries"] = {"home": out["home"][0], "away": out["away"][0],
                             "impact": [out["home"][1], out["away"][1]]}
            continue
        log.warning("sportsgambler hittade inte %s – %s", m["home"], m["away"])
