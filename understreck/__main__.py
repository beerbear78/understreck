"""Understreck – uppdaterar site/data.js.

  python -m understreck --mode friday     hämtar lördagens kupong och gör grundanalysen
  python -m understreck --mode lineups    lägger in startelvor ~1 h före första match (avbryter annars)
  python -m understreck --mode results    rätt rad (preliminär från tipsrader.se) och officiell utdelning (Svenska Spel)
  python -m understreck --mode deploy     ändrar inget, publicerar bara sidan igen
--wait: vänta i stället för att avbryta (startelvor: tills ~55 min före första avspark, resultat: upp till ~5 h).
        Används av de schemalagda körningarna, eftersom GitHub ofta startar dem timmar för sent.
--force kör startelvor utanför tidsfönstret (testläge), --dry-run sparar inget.
"""
from __future__ import annotations

import argparse
import logging
import os
import re
import sys
import time
from datetime import date, datetime, timedelta

import requests

from . import claude, footballdata, model, odds, skador, store, svenskaspel, tipsrader, understat
from .apifootball import ApiFootball, ApiFootballError, enrich_friday, lineups as af_lineups, set_injuries
from .util import TZ, http, log, now, set_output, team_sim

ODDS_KEY = os.environ.get("ODDS_API_KEY", "").strip()
AF_KEY = os.environ.get("API_FOOTBALL_KEY", "").strip()
FD_KEY = os.environ.get("FOOTBALL_DATA_KEY", "").strip()
RESEARCH = os.environ.get("RESEARCH", "1") != "0"
# xG utanför de stora ligorna finns inte gratis. Att låta Claude söka upp det kostar ca 1 dollar per körning,
# så det är avstängt som standard. Modellen klarar sig då på odds, form och skador för de matcherna.
RESEARCH_XG = os.environ.get("RESEARCH_XG", "0") == "1"
RESEARCH_FRIDAY = os.environ.get("RESEARCH_FRIDAY", "0") == "1"
MAX_WAIT = 5.2 * 3600  # GitHub avbryter jobb efter 6 timmar


def kickoff(m) -> datetime:
    return datetime.fromisoformat(m["_src"]["kickoff"])


def _missing(m, field):
    v = m.get(field)
    if field in ("form", "xg"):
        return not (v and v.get("home") and v.get("away"))
    return not v


# ---------------------------------------------------------------- fredag

def run_friday(s) -> dict:
    c = tipsrader.fetch_coupon(s)
    if c["close_at"] < now():
        raise tipsrader.CouponError("Kupongen på tipsrader.se har redan passerat spelstopp.")
    day = c["close_at"]
    matches = []
    for cm in c["matches"]:
        k = cm["kickoff_dt"] or day
        matches.append({"n": cm["n"], "home": cm["home"], "away": cm["away"], "league": None,
                        "kickoff": k.strftime("%H:%M"), "folk": cm["folk"], "odds": None,
                        "table": None, "form": {}, "xg": None, "injuries": None, "facts": None,
                        "_src": {"kickoff": k.isoformat()}})

    if ODDS_KEY:
        for n, o in odds.fetch_odds(s, ODDS_KEY, matches, day).items():
            m = next(x for x in matches if x["n"] == n)
            m.update(odds=o["odds"], league=o["league"])
            m["_src"]["sport"] = o["sport"]
            for side, full in zip(("home", "away"), o["teams"]):
                if re.search(r"\s\w$", m[side]):  # "Sheffield U" -> "Sheffield United"
                    m[side] = full
            if not m["_src"].get("kickoff") or o["kickoff_dt"].date() == day.date():
                m["_src"]["kickoff"] = o["kickoff_dt"].isoformat()
                m["kickoff"] = o["kickoff_dt"].strftime("%H:%M")
    else:
        log.warning("ODDS_API_KEY saknas – inga odds hämtas")

    if AF_KEY:
        try:
            enrich_friday(ApiFootball(s, AF_KEY), matches, day)
        except (ApiFootballError, requests.RequestException) as e:
            log.warning("API-Football gick inte att använda: %s", e)
    if FD_KEY:
        footballdata.enrich(footballdata.FootballData(s, FD_KEY), matches)
    understat.enrich(s, matches, day)
    skador.enrich(s, matches)

    # Webbsökningen görs som standard bara på lördagen (ett anrop i veckan). RESEARCH_FRIDAY=1 slår på den här.
    needs = [{"n": m["n"], "home": m["home"], "away": m["away"], "league": m["league"], "kickoff": m["kickoff"],
              "fields": [f for f in ("table", "form", "xg")
                         if _missing(m, f) and (f != "xg" or RESEARCH_XG)]} for m in matches]
    needs = [x for x in needs if x["fields"]]
    if needs and RESEARCH and RESEARCH_FRIDAY and claude.available():
        log.info("Claude söker uppgifter som saknas för %d matcher", len(needs))
        for n, found in claude.research(needs, day, lineups=False).items():
            m = next((x for x in matches if x["n"] == n), None)
            if m:
                for f, v in found.items():
                    if f != "lineup" and _missing(m, f):
                        m[f] = v
    for m in matches:
        m["injuries"] = m["injuries"] or {"home": [], "away": [], "impact": None}

    rnd = {"id": c["id"], "draw": c["draw"], "date": day.date().isoformat(), "deadline": day.strftime("%H:%M"),
           "turnover": c["turnover"], "updated": now().date().isoformat(), "lineupUpdate": None, "matches": matches}
    finalize(rnd)
    return rnd


# ---------------------------------------------------------------- lördag

def run_lineups(s, rounds, force=False, wait=False) -> dict | None:
    today = now().date().isoformat()
    rnd = next((r for r in rounds if r["date"] == today), None)
    if rnd is None and force:
        # Testläge: kör mot nästa kommande omgång, utan att markera startelvorna som inlagda.
        rnd = next((r for r in sorted(rounds, key=lambda r: r["date"]) if r["date"] > today), None)
        if rnd:
            log.info("Testläge: kör lördagsflödet för omgång %s (%s) i förväg", rnd["id"], rnd["date"])
    if rnd is None:
        log.info("Dagens omgång saknas i data.js, gör grundanalysen först")
        rnd = run_friday(s)
        if rnd["date"] != today:
            log.info("Kupongen på tipsrader.se spelas inte i dag")
            return None
    if rnd.get("lineupUpdate") and not force:
        log.info("Startelvorna är redan inlagda (%s)", rnd["lineupUpdate"])
        return None
    matches = rnd["matches"]
    first = min(kickoff(m) for m in matches)
    if not force:
        mins = (first - now()).total_seconds() / 60
        if mins < 20:
            log.info("För sent: första avspark %s var för nära eller har passerat", first.strftime("%H:%M"))
            return None
        if mins > 80:
            target = first - timedelta(minutes=55)
            secs = (target - now()).total_seconds()
            if not wait:
                log.info("Inte dags: första avspark %s, om %.0f minuter", first.strftime("%H:%M"), mins)
                return None
            if secs > MAX_WAIT:
                log.info("För tidigt (%.1f timmar kvar), en senare körning tar över", secs / 3600)
                return None
            log.info("Väntar till %s (%.0f minuter) innan startelvorna hämtas", target.strftime("%H:%M"), secs / 60)
            time.sleep(secs)

    try:
        c = tipsrader.fetch_coupon(s)
        if c["id"] == rnd["id"]:
            for cm in c["matches"]:
                m = next((x for x in matches if x["n"] == cm["n"]), None)
                if m and team_sim(m["home"], cm["home"]) >= 0.8:
                    m["folk"] = cm["folk"]
            rnd["turnover"] = c["turnover"] or rnd.get("turnover")
    except (tipsrader.CouponError, requests.RequestException) as e:
        log.warning("Kunde inte uppdatera folkets streck: %s", e)

    if ODDS_KEY:
        try:
            for n, o in odds.fetch_odds(s, ODDS_KEY, matches, first).items():
                m = next(x for x in matches if x["n"] == n)
                if o["odds"]:
                    m["odds"] = o["odds"]
        except requests.RequestException as e:
            log.warning("Kunde inte uppdatera odds: %s", e)

    early = [m for m in matches if kickoff(m) <= first + timedelta(minutes=75)]
    lineup_data = {}
    if AF_KEY:
        af = ApiFootball(s, AF_KEY)
        for m in early:
            if not m["_src"].get("fixture"):
                continue
            try:
                set_injuries(af, m)
                lu = af_lineups(af, m)
                if lu:
                    lineup_data[m["n"]] = lu
            except (ApiFootballError, requests.RequestException) as e:
                log.warning("API-Football, startelva %s – %s: %s", m["home"], m["away"], e)
    # Färsk skadelista för alla matcher (gratis). Färska odds ovan fångar marknadens reaktion på startelvorna.
    skador.enrich(s, matches)
    # Ett enda sökanrop i veckan, så litet som möjligt:
    #  - bekräftade startelvor bara för veckans tre spelvärda matcher (om de startar vid första avspark)
    #  - tabell, form och skador för matcher som de gratis källorna inte täcker (oftast League One)
    top_n = {matches[p["i"]]["n"] for p in model.top_picks([model.analyse(m) for m in matches])}
    no_injuries = lambda m: (m.get("injuries") or {}).get("impact") is None
    needs = [{"n": m["n"], "home": m["home"], "away": m["away"], "league": m["league"], "kickoff": m["kickoff"],
              "fields": (["lineup"] if m in early and m["n"] in top_n and m["n"] not in lineup_data else [])
              + (["injuries"] if no_injuries(m) and m["n"] not in lineup_data else [])
              + [f for f in ("table", "form") if _missing(m, f)]}
             for m in matches]
    needs = [x for x in needs if x["fields"]]
    if needs and RESEARCH and claude.available():
        for n, found in claude.research(needs, first, lineups=True).items():
            m = next((x for x in matches if x["n"] == n), None)
            if m:
                if found.get("lineup"):
                    m["lineup"] = found["lineup"]
                if found.get("injuries") and no_injuries(m):
                    m["injuries"] = found["injuries"]
                for f in ("table", "form"):
                    if found.get(f) and _missing(m, f):
                        m[f] = found[f]
    for m in matches:
        if m not in early:
            m["lineup"] = f"Startelvan släpps cirka {(kickoff(m) - timedelta(hours=1)):%H:%M}, efter spelstopp."

    finalize(rnd, lineup_data)
    if rnd["date"] == today:
        rnd["lineupUpdate"] = now().strftime("%Y-%m-%dT%H:%M")
    else:
        log.info("Testläge: lördagens riktiga körning gör ändå sin uppdatering")
    rnd["updated"] = today
    return rnd


# ---------------------------------------------------------------- resultat

def run_results(s, rounds, wait=False) -> dict | None:
    """Preliminär rätt rad när alla matcher är slut, officiell rad + utdelning när Svenska Spel publicerat."""
    today = now().date()
    open_rounds = [r for r in rounds if r["date"] <= today.isoformat() and not (r.get("results") or {}).get("final")]
    rnd = max(open_rounds, key=lambda r: r["date"], default=None)
    if rnd is None or (today - date.fromisoformat(rnd["date"])).days > 3:
        log.info("Ingen omgång väntar på resultat")
        return None
    if now() < min(kickoff(m) for m in rnd["matches"]):
        log.info("Omgång %s har inte börjat än", rnd["id"])
        return None
    deadline = now() + timedelta(seconds=MAX_WAIT if wait else 0)
    while True:
        try:
            res = svenskaspel.fetch_result(s, rnd.get("draw"))
        except requests.RequestException as e:
            log.warning("Svenska Spel svarade inte: %s", e)
            res = None
        if res:
            rnd["results"] = {**res, "updated": now().strftime("%Y-%m-%dT%H:%M")}
            return rnd
        try:
            live = tipsrader.fetch_live(s)
        except requests.RequestException as e:
            log.warning("tipsrader.se svarade inte: %s", e)
            live = None
        if live and live["id"] == rnd["id"] and live["matches"] and all(x["finished"] for x in live["matches"]):
            row = [x["sign"] for x in live["matches"]]
            if (rnd.get("results") or {}).get("row") != row:
                rnd["results"] = {"final": False, "row": row, "scores": [x["score"] for x in live["matches"]],
                                  "payouts": [], "updated": now().strftime("%Y-%m-%dT%H:%M")}
                log.info("Alla matcher är slut. Preliminär rätt rad: %s (utdelningen hämtas senare)", "".join(row))
                return rnd
        if now() >= deadline:
            log.info("Inget nytt resultat för omgång %s än", rnd["id"])
            return None
        log.info("Väntar 10 minuter på resultat …")
        time.sleep(600)


# ---------------------------------------------------------------- gemensamt

def finalize(rnd, lineup_data=None) -> None:
    """Räknar modellen och skriver analystexter (Claude, annars mallar)."""
    matches = rnd["matches"]
    an = [model.analyse(m) for m in matches]
    picks = model.top_picks(an)
    pick_by_n = {matches[p["i"]]["n"]: p for p in picks}
    notes = claude.write_notes(matches, an, picks, lineup_data) or {}
    if not notes:
        log.warning("Analystexterna skrivs med mallar (Claude ej tillgängligt)")
    for m, a in zip(matches, an):
        nt = notes.get(m["n"], {})
        m["note"] = nt.get("note") or claude.template_note(m, a)
        pk = pick_by_n.get(m["n"])
        m["valueNote"] = (nt.get("valueNote") or (
            f"Beräknad chans för {model.SIGNS[pk['k']]} är {round(pk['p'] * 100)} % mot folkets {round(pk['f'] * 100)} %.")) if pk else ""
        if lineup_data and m["n"] in lineup_data:
            lu = lineup_data[m["n"]]
            m["lineup"] = nt.get("lineup") or f"Startelvorna är släppta ({lu.get('home_formation') or '?'} mot {lu.get('away_formation') or '?'})."
    report(rnd, matches, an, picks)


def report(rnd, matches, an, picks) -> None:
    lines = [f"## Understreck – omgång {rnd['id']}, {rnd['date']}", "", "### Veckans spelvärda"]
    for p in picks:
        m = matches[p["i"]]
        lines.append(f"- {m['home']} – {m['away']}: **{model.SIGNS[p['k']]}**, beräknad chans {round(p['p']*100)} %, "
                     f"folket {round(p['f']*100)} %, spelvärde {p['v']:.2f}".replace(".", ","))
    for prof in ("balans", "skrall"):
        sysm = model.build_system(an, 64, profile=prof)
        lines += ["", f"### 64 rader – {model.PROFILES[prof]['label']} (chans 13 rätt ca 1 på {round(1/sysm['hit']):,})".replace(",", " "),
                  "```", model.row_text(matches, sysm), "```"]
    text = "\n".join(lines)
    log.info("\n%s", text)
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(text + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(prog="understreck")
    ap.add_argument("--mode", choices=["friday", "lineups", "results", "auto", "deploy"], default="auto")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--wait", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    mode = args.mode
    if mode == "auto":
        wd, hour = now().weekday(), now().hour
        mode = "friday" if wd == 4 else ("lineups" if wd == 5 and hour < 17 else "results")
    if mode == "deploy":
        set_output("changed", "true")
        return 0

    s = http()
    rounds = store.load()
    try:
        if mode == "friday":
            rnd = run_friday(s)
        elif mode == "lineups":
            rnd = run_lineups(s, rounds, args.force, args.wait)
        else:
            rnd = run_results(s, rounds, args.wait)
    except tipsrader.CouponError as e:
        log.error("Avbryter: %s", e)
        set_output("changed", "false")
        return 1 if mode == "friday" else 0
    if rnd is None:
        set_output("changed", "false")
        return 0
    if not args.dry_run:
        store.save(store.upsert(rounds, rnd))
        log.info("Sparade %s", store.DATA)
    set_output("changed", "false" if args.dry_run else "true")
    return 0


if __name__ == "__main__":
    sys.exit(main())
