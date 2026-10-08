"""Gemensamma hjälpfunktioner: HTTP, tid och matchning av lagnamn."""
from __future__ import annotations

import difflib
import logging
import re
import unicodedata
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

TZ = ZoneInfo("Europe/Stockholm")
USER_AGENT = "Understreck/1.0 (privat statistikprojekt, uppdateras två gånger i veckan)"

log = logging.getLogger("understreck")


def http() -> requests.Session:
    s = requests.Session()
    s.headers["User-Agent"] = USER_AGENT
    return s


def now() -> datetime:
    return datetime.now(TZ)


# Ord som skrivs olika hos olika källor. Nyckel och värde är normaliserade (gemener, utan accenter).
_TOKEN_SWAP = {
    "utd": "united", "man": "manchester", "weds": "wednesday", "wed": "wednesday",
    "nottm": "nottingham", "brom": "bromwich", "spurs": "tottenham", "wolves": "wolverhampton",
    "qpr": "queens park rangers", "mk": "milton keynes", "&": "and",
    "u": "united", "w": "wednesday",  # tipsrader.se skriver ibland "Sheffield U" / "Sheffield W"
}
_FILLER = {"fc", "afc", "cf", "sc", "the", "ff", "if", "bk", "fk"}


def norm_team(name: str) -> str:
    s = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode().lower()
    s = s.replace("&", " and ")
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    words = []
    for w in s.split():
        w = _TOKEN_SWAP.get(w, w)
        words.extend(w.split())
    return " ".join(w for w in words if w not in _FILLER)


def team_sim(a: str, b: str) -> float:
    """Likhet 0–1 mellan två lagnamn. Täcker t.ex. 'Preston' ~ 'Preston North End'."""
    na, nb = norm_team(a), norm_team(b)
    if not na or not nb:
        return 0.0
    if na == nb:
        return 1.0
    ta, tb = set(na.split()), set(nb.split())
    if ta <= tb or tb <= ta:
        return 0.92
    return difflib.SequenceMatcher(None, na, nb).ratio()


def best_pair(home: str, away: str, candidates, get_home, get_away, min_each=0.8):
    """Hittar den kandidat (t.ex. en match hos en API-källa) som bäst motsvarar home–away."""
    best, best_score = None, 0.0
    for c in candidates:
        sh, sa = team_sim(home, get_home(c)), team_sim(away, get_away(c))
        if sh < min_each or sa < min_each:
            continue
        if sh + sa > best_score:
            best, best_score = c, sh + sa
    return best


def ordinal(n: int) -> str:
    """1:a, 2:a, 3:e … 21:a, 22:a."""
    return f"{n}:a" if n % 10 in (1, 2) and n % 100 not in (11, 12) else f"{n}:e"


def set_output(name: str, value: str) -> None:
    """Skriver en output till GitHub Actions (ignoreras lokalt)."""
    import os
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"{name}={value}\n")
