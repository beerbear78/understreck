"""Modellen – en exakt kopia av beräkningarna i site/index.html.

Ändras något här måste samma ändring göras i sidans JavaScript, annars
stämmer analystexterna inte med siffrorna på sidan.
"""
from __future__ import annotations

import math

SIGNS = ["1", "X", "2"]
W_MARKET, HOME, AWAY, MIN_PICK = 0.65, 1.10, 0.91, 0.22
RHO = -0.13                     # Dixon–Coles
XG_MEAN, XG_KEEP = 1.40, 0.65   # xG dras 35 % mot ligasnittet

SYSTEMS = {
    1:   {"rows": 1,   "h": 0, "b": 0, "label": "Enkelrad"},
    64:  {"rows": 64,  "h": 0, "b": 6, "label": "64 rader"},
    192: {"rows": 192, "h": 1, "b": 6, "label": "192 rader"},
    576: {"rows": 576, "h": 2, "b": 6, "label": "576 rader"},
}
PROFILES = {
    "balans": {"label": "Balanserad", "tilt": 0.5, "skrall": False},
    "skrall": {"label": "Skräll", "tilt": 1.5, "skrall": True},
}
SUBSETS = [[0], [1], [2], [0, 1], [0, 2], [1, 2], [0, 1, 2]]


def _norm(a):
    s = sum(a)
    return [x / s for x in a]


def _shrink(x):
    return XG_MEAN + XG_KEEP * (x - XG_MEAN)


def _ok_pair(v):
    return isinstance(v, (list, tuple)) and len(v) == 2 and all(
        isinstance(x, (int, float)) and math.isfinite(x) for x in v)


def form_ppg(s):
    if not s:
        return None
    p = n = 0
    for c in str(s).upper():
        if c in "VW":
            p += 3; n += 1
        elif c in "OD":
            p += 1; n += 1
        elif c in "FL":
            n += 1
    return p / n if n else None


def _pois(k, lam):
    r = math.exp(-lam)
    for i in range(1, k + 1):
        r *= lam / i
    return r


def poisson1x2(lh, la):
    p = [0.0, 0.0, 0.0]
    by = [{"p": 0.0}, {"p": 0.0}, {"p": 0.0}]
    for h in range(10):
        for a in range(10):
            q = _pois(h, lh) * _pois(a, la)
            if h == 0 and a == 0:
                q *= 1 - lh * la * RHO
            elif h == 0 and a == 1:
                q *= 1 + lh * RHO
            elif h == 1 and a == 0:
                q *= 1 + la * RHO
            elif h == 1 and a == 1:
                q *= 1 - RHO
            k = 0 if h > a else (1 if h == a else 2)
            p[k] += q
            if q > by[k]["p"]:
                by[k] = {"p": q, "h": h, "a": a}
    return {"p": _norm(p), "scoreBy": by}


def analyse(m, override=None):
    folk = _norm(override or m["folk"])
    a = {"folk": folk, "market": None, "stats": None, "score": None}
    odds = m.get("odds")
    market = None
    if isinstance(odds, list) and len(odds) == 3 and all(isinstance(o, (int, float)) and o > 1 for o in odds):
        inv = [1 / o for o in odds]
        a["margin"] = sum(inv) - 1
        market = _norm(inv)
        a["market"] = market
    tH = tA = 1.0
    form = m.get("form") or {}
    fh, fa = form_ppg(form.get("home")), form_ppg(form.get("away"))
    if fh is not None and fa is not None:
        d = (fh - fa) / 3
        tH *= 1 + 0.05 * d
        tA *= 1 - 0.05 * d
    imp = (m.get("injuries") or {}).get("impact")
    if _ok_pair(imp):
        tH *= (1 - 0.04 * imp[0]) * (1 + 0.02 * imp[1])
        tA *= (1 - 0.04 * imp[1]) * (1 + 0.02 * imp[0])
    xg = m.get("xg") or {}
    stats = None
    if _ok_pair(xg.get("home")) and _ok_pair(xg.get("away")):
        xh, xa = xg["home"], xg["away"]
        lh = (_shrink(xh[0]) + _shrink(xa[1])) / 2 * HOME * tH
        la = (_shrink(xa[0]) + _shrink(xh[1])) / 2 * AWAY * tA
        stats = poisson1x2(lh, la)
        a["lambda"] = [lh, la]
        a["stats"] = stats["p"]
    if market and stats:
        p = [W_MARKET * market[i] + (1 - W_MARKET) * stats["p"][i] for i in range(3)]
    elif stats:
        p = list(stats["p"])
    else:
        base = market or folk
        shift = (tH - tA) * 0.25
        p = [base[0] + shift, base[1], base[2] - shift]
    p = _norm([max(0.02, x) for x in p])
    a["p"] = p
    a["value"] = [x / max(folk[i], 0.005) for i, x in enumerate(p)]
    a["likely"] = p.index(max(p))
    if stats:
        sc = stats["scoreBy"][a["likely"]]
        a["score"] = f"{sc['h']}–{sc['a']}"
    order = sorted(range(3), key=lambda i: -p[i])
    if p[order[0]] >= 0.55:
        a["verdict"] = f"Spik {SIGNS[order[0]]}"
    elif p[order[0]] >= 0.42 or p[order[0]] + p[order[1]] >= 0.76:
        a["verdict"] = "Halvgardera " + "".join(SIGNS[i] for i in sorted(order[:2]))
    else:
        a["verdict"] = "Helgardera"
    return a


def top_picks(an):
    c = []
    for i, a in enumerate(an):
        best = None
        for k, p in enumerate(a["p"]):
            if p < MIN_PICK:
                continue
            if best is None or a["value"][k] > best["v"]:
                best = {"i": i, "k": k, "v": a["value"][k], "p": p, "f": a["folk"][k]}
        if best and best["v"] > 1.0:
            c.append(best)
    c.sort(key=lambda x: -x["v"])
    return c[:3]


def fav_of(a):
    return a["folk"].index(max(a["folk"]))


def build_system(an, rows=64, min_x=None, profile="balans"):
    cfg, prof = SYSTEMS[rows], PROFILES[profile]
    if min_x is None:
        min_x = math.floor(sum(a["p"][1] for a in an))

    def val_of(a, s):
        return sum(a["p"][j] * a["value"][j] for j in s) / sum(a["p"][j] for j in s)

    def score(a, s):
        return math.log(sum(a["p"][j] for j in s)) + prof["tilt"] * math.log(val_of(a, s))

    dp = {(0, 0, 0, 0): {"s": 0.0, "pick": []}}
    for a in an:
        fav = fav_of(a)
        nxt = {}
        for (h, b, x, d), st in dp.items():
            for s in SUBSETS:
                nh, nb = h + (len(s) == 3), b + (len(s) == 2)
                if nh > cfg["h"] or nb > cfg["b"]:
                    continue
                nx = min(min_x, x + (1 in s))
                nd = d + (fav not in s) - (len(s) == 1 and s[0] == fav) if prof["skrall"] else 0
                sc = st["s"] + score(a, s)
                k2 = (nh, nb, nx, nd)
                cur = nxt.get(k2)
                if cur is None or sc > cur["s"]:
                    nxt[k2] = {"s": sc, "pick": st["pick"] + [s]}
        dp = nxt
    fin = None
    for x in range(min_x, -1, -1):
        for (h, b, xx, d), st in dp.items():
            if h != cfg["h"] or b != cfg["b"] or xx != x or (prof["skrall"] and d < 1):
                continue
            if fin is None or st["s"] > fin["s"]:
                fin = st
        if fin:
            break
    if fin is None:
        fin = max(dp.values(), key=lambda st: st["s"])
    sel = [list(s) for s in fin["pick"]]
    return {
        "sel": sel,
        "skrall": [fav_of(a) not in sel[i] for i, a in enumerate(an)],
        "rows": math.prod(len(s) for s in sel),
        "hit": math.prod(sum(a["p"][j] for j in sel[i]) for i, a in enumerate(an)),
        "x": sum(1 in s for s in sel),
    }


def row_text(matches, system):
    return "\n".join(
        f"{m['n']:>2}. {m['home']} – {m['away']}: {''.join(SIGNS[k] for k in s)}"
        + ("  (skräll)" if sk else "")
        for m, s, sk in zip(matches, system["sel"], system["skrall"]))
