"""Claude-API: analystexter, och webbresearch när de fria API:erna saknar data.

Kräver miljövariabeln ANTHROPIC_API_KEY. Saknas den skrivs enklare
malltexter i stället, så sidan fungerar ändå.
"""
from __future__ import annotations

import json
import os
import re

import anthropic

from .model import SIGNS
from .util import log

MODEL = os.environ.get("CLAUDE_MODEL") or "claude-opus-5-5"
RESEARCH_MAX_SEARCHES = int(os.environ.get("RESEARCH_MAX_SEARCHES") or 12)
FALLBACK_BETA = "server-side-fallback-2026-07-01"
PRICES = {"claude-opus-5-5": (4.0, 20.0), "claude-sonnet-5-5": (2.0, 10.0), "claude-haiku-5-5": (0.10, 0.50)}

STYLE = """Skriv på enkel, rak svenska för en tippare. Använd bara siffror och fakta som finns i underlaget,
hitta aldrig på spelare, resultat eller statistik. Inga tankstreck-inskott, inga klyschor, inga utropstecken.
Skriv "folket" för svenska folkets streck och "modellen" för sidans sannolikheter."""

NOTES_SCHEMA = {
    "type": "object",
    "properties": {"matches": {"type": "array", "items": {
        "type": "object",
        "properties": {"n": {"type": "integer"}, "note": {"type": "string"},
                       "valueNote": {"type": "string"}, "lineup": {"type": "string"}},
        "required": ["n", "note", "valueNote", "lineup"],
        "additionalProperties": False}}},
    "required": ["matches"],
    "additionalProperties": False,
}


_KEY = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()
_disabled = False


def available() -> bool:
    return bool(_KEY) and not _disabled


def _client():
    return anthropic.Anthropic(api_key=_KEY, max_retries=3)


def _auth_failed(e) -> None:
    """Stänger av Claude resten av körningen och förklarar vad som är fel."""
    global _disabled
    _disabled = True
    log.error("Claude: nyckeln godkänns inte (%s). Skapa en ny nyckel på platform.claude.com → API Keys "
              "och klistra in hela värdet (börjar med sk-ant-) i secret ANTHROPIC_API_KEY.", e.status_code)


def _log_cost(resp, what):
    u = resp.usage
    pin, pout = PRICES.get(MODEL, (4.0, 20.0))
    searches = getattr(getattr(u, "server_tool_use", None), "web_search_requests", 0) or 0
    cost = u.input_tokens / 1e6 * pin + u.output_tokens / 1e6 * pout + searches * 0.01
    log.info("Claude %s: %d in, %d ut, %d sökningar, ca $%.3f", what, u.input_tokens, u.output_tokens, searches, cost)


def _create(**kw):
    return _client().beta.messages.create(
        model=MODEL, max_tokens=16000, betas=[FALLBACK_BETA],
        fallbacks="default", **kw)


# ---------------------------------------------------------------- analystexter

def _pct(x):
    return round(x * 100)


def _payload(m, a, pick, lineup):
    return {
        "n": m["n"], "match": f"{m['home']} – {m['away']}", "liga": m.get("league"),
        "folket_1X2_procent": [_pct(x) for x in a["folk"]],
        "modellen_1X2_procent": [_pct(x) for x in a["p"]],
        "odds_1X2": m.get("odds"),
        "oddsens_1X2_procent": [_pct(x) for x in a["market"]] if a.get("market") else None,
        "spelvarde_1X2": [round(v, 2) for v in a["value"]],
        "troligt_utfall": SIGNS[a["likely"]], "troligaste_resultat": a.get("score"),
        "bedomning": a["verdict"], "tabell": m.get("table"), "form_aldst_forst": m.get("form"),
        "xg_for_emot_per_match": m.get("xg"), "skador": m.get("injuries"), "fakta": m.get("facts"),
        "veckans_spelvarda_tecken": SIGNS[pick["k"]] if pick else None,
        "startelvor": lineup,
    }


def write_notes(matches, analyses, picks, lineups=None) -> dict | None:
    """Returnerar {n: {note, valueNote, lineup}} eller None om Claude inte gick att använda."""
    if not available():
        return None
    by_match = {p["i"]: p for p in picks}
    lineups = lineups or {}
    data = [_payload(m, a, by_match.get(i), lineups.get(m["n"])) for i, (m, a) in enumerate(zip(matches, analyses))]
    prompt = f"""Här är veckans 13 Stryktipsmatcher med modellens beräkningar (JSON):

{json.dumps(data, ensure_ascii=False)}

Skriv för varje match:
- note: 2–4 meningar. Förklara varför det troliga utfallet är troligast och om något tecken är under- eller
  överstreckat, med konkreta siffror ur underlaget (xG, form, skador, modell mot folk).
- valueNote: en mening om varför tecknet är spelvärt, men bara för matcher där veckans_spelvarda_tecken
  inte är null. Annars tom sträng.
- lineup: om startelvor finns, en mening om det som påverkar matchen (vilka i skadelistan som saknas,
  oväntade bänkningar bland spelarna i listorna). Nämn bara spelare som står i underlaget. Annars tom sträng.

{STYLE}"""
    try:
        resp = _create(system="Du är analytiker för Stryktipset.", output_config={
            "effort": "medium", "format": {"type": "json_schema", "schema": NOTES_SCHEMA}},
            messages=[{"role": "user", "content": prompt}])
    except anthropic.AuthenticationError as e:
        _auth_failed(e)
        return None
    except anthropic.APIError as e:
        log.error("Claude-anropet för analyser misslyckades: %s", e)
        return None
    _log_cost(resp, "analyser")
    if resp.stop_reason != "end_turn":
        log.error("Claude avbröt analyserna (%s)", resp.stop_reason)
        return None
    text = next((b.text for b in resp.content if b.type == "text"), "")
    try:
        rows = json.loads(text)["matches"]
    except (ValueError, KeyError) as e:
        log.error("Kunde inte läsa Claudes svar: %s", e)
        return None
    return {r["n"]: r for r in rows if isinstance(r.get("n"), int)}


def template_note(m, a) -> str:
    """Enkel text utan AI, används om Claude inte är tillgängligt."""
    s = SIGNS[a["likely"]]
    parts = [f"Modellen ger {s} {_pct(a['p'][a['likely']])} % mot folkets {_pct(a['folk'][a['likely']])} %."]
    best = max(range(3), key=lambda k: a["value"][k] if a["p"][k] >= 0.22 else 0)
    if a["value"][best] >= 1.15:
        parts.append(f"{SIGNS[best]} är understreckat: {_pct(a['p'][best])} % enligt modellen, "
                     f"{_pct(a['folk'][best])} % hos folket.")
    worst = min(range(3), key=lambda k: a["value"][k])
    if a["value"][worst] <= 0.85:
        parts.append(f"{SIGNS[worst]} är överstreckat.")
    xg = m.get("xg") or {}
    if xg.get("home") and xg.get("away"):
        d = lambda v: f"{v:.1f}".replace(".", ",")
        parts.append(f"xG för och emot per match: {m['home']} {d(xg['home'][0])} och {d(xg['home'][1])}, "
                     f"{m['away']} {d(xg['away'][0])} och {d(xg['away'][1])}.")
    return " ".join(parts)


# ---------------------------------------------------------------- webbresearch

FORM_RE = re.compile(r"^[VOF]{1,5}$")


def _extract_json(text: str):
    m = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", text, re.S)
    raw = m.group(1) if m else text[text.find("["): text.rfind("]") + 1]
    return json.loads(raw)


def research(needs: list[dict], day, lineups: bool) -> dict:
    """needs = [{n, home, away, league, kickoff, fields: [...]}]. Returnerar {n: {...}}."""
    if not available() or not needs:
        return {}
    prompt = f"""Ta reda på aktuell data för de här fotbollsmatcherna som spelas {day:%Y-%m-%d}
(säsongen {day.year if day.month >= 7 else day.year - 1}/{(day.year + 1 if day.month >= 7 else day.year) % 100:02d}).
Sök bara efter fälten i "fields" för respektive match.

{json.dumps(needs, ensure_ascii=False)}

Fält:
- table: {{"home": "3:e, 15 p (8 matcher)", "away": ...}}
- form: {{"home": "VOFVV", "away": ...}} de fem senaste ligamatcherna, äldst först, V/O/F
- xg: {{"home": [xG för per match, xG emot per match], "away": [...]}} säsongssnitt (fbref, footystats, fotmob, understat)
- injuries: {{"home": ["Namn (skadad)", "Namn (avstängd)", "Namn (osäker)"], "away": [...], "impact": [0-3, 0-3]}}
  impact: 0 inga frånvarande, 1 liten, 2 märkbar, 3 stor påverkan på laget
- lineup: en mening på svenska om den bekräftade startelvan, t.ex. vilka nyckelspelare som saknas{
" (startelvorna släpps cirka en timme före avspark)" if lineups else ""}

Regler: använd bara källor för innevarande säsong och se upp för förhandssidor med förra säsongens data.
Gissa aldrig. Sätt null för det du inte hittar säkert.
Svara till sist med enbart en JSON-lista: [{{"n": 1, "table": ..., "form": ..., "xg": ..., "injuries": ..., "lineup": ...}}, ...]
med bara de fält som efterfrågats."""
    messages = [{"role": "user", "content": prompt}]
    tools = [{"type": "web_search_20260209", "name": "web_search", "max_uses": RESEARCH_MAX_SEARCHES}]
    try:
        for _ in range(5):
            resp = _create(tools=tools, output_config={"effort": "medium"}, messages=messages)
            if resp.stop_reason != "pause_turn":
                break
            messages = [messages[0], {"role": "assistant", "content": resp.content}]
    except anthropic.AuthenticationError as e:
        _auth_failed(e)
        return {}
    except anthropic.APIError as e:
        log.error("Claude-researchen misslyckades: %s", e)
        return {}
    _log_cost(resp, "research")
    text = "".join(b.text for b in resp.content if b.type == "text")
    try:
        rows = _extract_json(text)
    except ValueError:
        log.error("Kunde inte läsa researchsvaret")
        return {}
    return {r["n"]: _clean(r) for r in rows if isinstance(r, dict) and isinstance(r.get("n"), int)}


def _clean(r: dict) -> dict:
    out = {}
    t = r.get("table")
    if isinstance(t, dict) and isinstance(t.get("home"), str) and isinstance(t.get("away"), str):
        out["table"] = {"home": t["home"], "away": t["away"]}
    f = r.get("form")
    if isinstance(f, dict) and all(isinstance(f.get(s), str) and FORM_RE.match(f[s]) for s in ("home", "away")):
        out["form"] = {"home": f["home"], "away": f["away"]}
    x = r.get("xg")
    ok = lambda v: isinstance(v, list) and len(v) == 2 and all(isinstance(n, (int, float)) and 0 <= n <= 5 for n in v)
    if isinstance(x, dict) and ok(x.get("home")) and ok(x.get("away")):
        out["xg"] = {"home": [float(v) for v in x["home"]], "away": [float(v) for v in x["away"]]}
    inj = r.get("injuries")
    if isinstance(inj, dict):
        imp = inj.get("impact")
        if isinstance(imp, list) and len(imp) == 2 and all(isinstance(i, int) and 0 <= i <= 3 for i in imp):
            out["injuries"] = {"home": [str(s) for s in inj.get("home") or []],
                               "away": [str(s) for s in inj.get("away") or []], "impact": imp}
    if isinstance(r.get("lineup"), str) and r["lineup"].strip():
        out["lineup"] = r["lineup"].strip()
    return out
