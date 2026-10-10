"""Kupong och svenska folkets streck från tipsrader.se.

Läser bara startsidan (tillåten i deras robots.txt). Adresserna /external/,
/ext/, /spel/index/ och /spela/ är spärrade och används inte.
"""
from __future__ import annotations

import re
import time
from datetime import datetime

from bs4 import BeautifulSoup

from .util import TZ, log

URL = "https://tipsrader.se/"


class CouponError(RuntimeError):
    pass


def _decode(raw: bytes) -> str:
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp1252", errors="replace")


def _text(soup, selector):
    el = soup.select_one(selector)
    return el.get_text(strip=True) if el else ""


def _load(http, attempts=3, pause=30):
    """Hämtar startsidan. Försöker igen om svaret saknar kupong (t.ex. en tillfällig spärrsida)."""
    for i in range(1, attempts + 1):
        try:
            r = http.get(URL, timeout=30)
            soup = BeautifulSoup(_decode(r.content), "html.parser")
            kind = _text(soup, "#roundtype")
            if r.ok and kind:
                return soup, kind
            title = soup.title.get_text(strip=True) if soup.title else ""
            log.warning("tipsrader.se försök %d: status %s, %d byte, titel '%s', början: %s", i, r.status_code,
                        len(r.content), title[:80], soup.get_text(" ", strip=True)[:160])
        except Exception as e:  # nätverksfel räknas som ett misslyckat försök
            log.warning("tipsrader.se försök %d: %s", i, e)
        if i < attempts:
            time.sleep(pause)
    return None, ""


def fetch_coupon(http) -> dict:
    soup, kind = _load(http)
    if soup is None:
        raise CouponError("tipsrader.se svarade inte med någon kupong efter tre försök (se loggen ovan).")
    if kind.lower() != "stryktipset":
        raise CouponError(f"tipsrader.se visar '{kind}', inte Stryktipset just nu.")
    try:
        round_id = int(_text(soup, "#roundid"))
        close_at = datetime.fromtimestamp(int(_text(soup, "#closeat")), TZ)
    except ValueError as e:
        raise CouponError("Hittade inte omgångsnummer eller spelstopp på tipsrader.se.") from e
    draw = _text(soup, "#drawnumber")
    turnover = None
    m = re.search(r"([\d\s ]+)\s*kr", _text(soup, ".prizepool"))
    if m:
        turnover = int(re.sub(r"\D", "", m.group(1)) or 0) or None

    matches = []
    for tr in soup.select("#matchestable tbody tr"):
        tds = tr.find_all("td", recursive=False)
        if not tds or not tds[0].get_text(strip=True).isdigit():
            continue
        home = _text(tr, "span.hometeam.hide-for-small-only")
        away = _text(tr, "span.awayteam.hide-for-small-only")
        folk = [int(s.get_text(strip=True)) for s in tr.select("td.percentinfo span")
                if s.get_text(strip=True).isdigit()][:3]
        kickoff = None
        km = re.search(r"(\d{1,2})/(\d{1,2})\s+(\d{1,2}):(\d{2})", _text(tr, "td.scorecell .score"))
        if km:
            day, month, hh, mm = map(int, km.groups())
            year = close_at.year + (1 if month < close_at.month - 6 else 0)
            kickoff = datetime(year, month, day, hh, mm, tzinfo=TZ)
        if not home or not away or len(folk) != 3:
            raise CouponError(f"Kunde inte läsa match {tds[0].get_text(strip=True)} på tipsrader.se.")
        matches.append({"n": int(tds[0].get_text(strip=True)), "home": home, "away": away,
                        "folk": folk, "kickoff_dt": kickoff})

    if len(matches) != 13:
        raise CouponError(f"Hittade {len(matches)} matcher på tipsrader.se, väntade 13.")
    log.info("tipsrader.se: omgång %s, spelstopp %s, %d matcher", round_id, close_at.strftime("%a %H:%M"), len(matches))
    return {"id": round_id, "draw": draw, "close_at": close_at, "turnover": turnover, "matches": matches}


FINISHED = {"FT", "AET", "PEN", "SLUT"}


def parse_live(soup) -> list:
    """Ställning, status och aktuellt tecken per match (tipsraders liverättning)."""
    out = []
    for tr in soup.select("#matchestable tbody tr"):
        tds = tr.find_all("td", recursive=False)
        if not tds or not tds[0].get_text(strip=True).isdigit():
            continue
        score = _text(tr, "td.scorecell .score")
        status = tds[3].get_text(" ", strip=True) if len(tds) > 3 else ""
        sign = _text(tr, "td.sign .sign-choice.active")
        played = bool(re.fullmatch(r"\d+\s*-\s*\d+", score))
        out.append({"n": int(tds[0].get_text(strip=True)),
                    "score": score.replace("-", "–").replace(" ", "") if played else None,
                    "sign": sign if played and sign in ("1", "X", "2") else None,
                    "finished": played and status.upper() in FINISHED})
    return out


def fetch_live(http) -> dict | None:
    soup, kind = _load(http)
    if soup is None or kind.lower() != "stryktipset":
        return None
    try:
        round_id = int(_text(soup, "#roundid"))
    except ValueError:
        return None
    return {"id": round_id, "matches": parse_live(soup)}
