"""Offlinetest med simulerade API-svar. Kör: python -m unittest discover tests"""
import unittest
from datetime import datetime
from unittest import mock

from understreck import apifootball, model, odds, store
from understreck.util import TZ, best_pair, team_sim

DAY = datetime(2026, 10, 10, 15, 59, tzinfo=TZ)
COUPON = [("Manchester United", "Tottenham"), ("Sheffield U", "Lincoln"), ("Huddersfield", "Sheffield W"),
          ("Middlesbrough", "Wolverhampton"), ("Sunderland", "Brighton"), ("Preston", "Millwall"),
          ("Man United", "Spurs"), ("Derby", "Wrexham")]
API_NAMES = [("Manchester United", "Tottenham Hotspur"), ("Sheffield United", "Lincoln City"),
             ("Huddersfield Town", "Sheffield Wednesday"), ("Middlesbrough", "Wolverhampton Wanderers"),
             ("Sunderland", "Brighton and Hove Albion"), ("Preston North End", "Millwall"),
             ("Manchester City", "Tottenham Hotspur"), ("Derby County", "Wrexham AFC"),
             ("Sheffield Wednesday", "Lincoln City")]


class Resp:
    def __init__(self, data, headers=None, status=200):
        self._d, self.headers, self.status_code, self.text = data, headers or {}, status, ""

    def json(self):
        return self._d

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(self.status_code)


class TestNames(unittest.TestCase):
    def test_pairs(self):
        expected = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 0, 7: 7}
        for i, (h, a) in enumerate(COUPON):
            got = best_pair(h, a, API_NAMES, lambda x: x[0], lambda x: x[1])
            self.assertEqual(got, API_NAMES[expected[i]], f"{h} – {a}")

    def test_no_false_match(self):
        self.assertLess(team_sim("Sheffield United", "Sheffield Wednesday"), 0.8)
        self.assertLess(team_sim("Bristol City", "Bristol Rovers"), 0.8)


class TestOdds(unittest.TestCase):
    def test_fetch(self):
        ev = {"home_team": "Sheffield United", "away_team": "Lincoln City", "commence_time": "2026-10-10T14:00:00Z",
              "bookmakers": [{"markets": [{"key": "h2h", "outcomes": [
                  {"name": "Sheffield United", "price": 2.1}, {"name": "Draw", "price": 3.4}, {"name": "Lincoln City", "price": 3.4}]}]},
                  {"markets": [{"key": "h2h", "outcomes": [
                      {"name": "Sheffield United", "price": 2.2}, {"name": "Draw", "price": 3.3}, {"name": "Lincoln City", "price": 3.2}]}]}]}

        def get(url, params=None, timeout=None):
            if url.endswith("/sports"):
                return Resp([{"key": "soccer_epl", "active": True}, {"key": "soccer_efl_champ", "active": True}])
            if "soccer_epl" in url:
                return Resp([], {"x-requests-remaining": "498"})
            return Resp([ev], {"x-requests-remaining": "496"})

        http = mock.Mock(get=get)
        found = odds.fetch_odds(http, "k", [{"n": 11, "home": "Sheffield U", "away": "Lincoln"}], DAY)
        self.assertEqual(found[11]["odds"], [2.15, 3.35, 3.3])
        self.assertEqual(found[11]["league"], "Championship")
        self.assertEqual(found[11]["kickoff_dt"].strftime("%H:%M"), "16:00")


class TestApiFootball(unittest.TestCase):
    def test_enrich(self):
        def fx(fid, date, h, a, gh, ga, status="FT"):
            return {"fixture": {"id": fid, "date": date, "status": {"short": status}},
                    "teams": {"home": {"id": h[0], "name": h[1]}, "away": {"id": a[0], "name": a[1]}},
                    "goals": {"home": gh, "away": ga}}
        SU, LI, X = (1, "Sheffield Utd"), (2, "Lincoln"), (3, "Other")
        fixtures = [fx(10, "2026-09-01T16:00:00+02:00", SU, X, 2, 0), fx(11, "2026-09-08T16:00:00+02:00", X, SU, 1, 1),
                    fx(12, "2026-09-15T16:00:00+02:00", LI, X, 0, 1), fx(13, "2026-09-20T16:00:00+02:00", X, LI, 0, 3),
                    fx(99, "2026-10-10T16:00:00+02:00", SU, LI, None, None, "NS")]
        table = [{"league": {"standings": [[
            {"rank": 18, "team": {"id": 1}, "points": 9, "all": {"played": 8}, "home": {"win": 1, "draw": 1, "lose": 2}, "away": {}},
            {"rank": 12, "team": {"id": 2}, "points": 11, "all": {"played": 8}, "home": {}, "away": {"win": 3, "draw": 0, "lose": 1}}]]}}]
        inj = [{"team": {"id": 1}, "player": {"name": "A", "type": "Missing Fixture", "reason": "Suspended"}},
               {"team": {"id": 1}, "player": {"name": "B", "type": "Questionable", "reason": "Knock"}},
               {"team": {"id": 2}, "player": {"name": "C", "type": "Missing Fixture", "reason": "Knee Injury"}}]
        routes = {"/leagues": [{"seasons": [{"year": 2026, "current": True}]}], "/fixtures": fixtures,
                  "/standings": table, "/injuries": inj,
                  "/fixtures/lineups": [{"team": {"id": 1}, "formation": "4-4-2", "startXI": [{"player": {"name": "P1"}}]},
                                        {"team": {"id": 2}, "formation": "3-5-2", "startXI": [{"player": {"name": "P2"}}]}]}
        af = apifootball.ApiFootball(None, "k")
        af.get = lambda path, **kw: routes[path]
        m = {"n": 11, "home": "Sheffield U", "away": "Lincoln", "_src": {"sport": "soccer_efl_champ"}}
        apifootball.enrich_friday(af, [m], DAY)
        self.assertEqual(m["form"], {"home": "VO", "away": "FV"})
        self.assertEqual(m["table"]["home"], "18:e, 9 p (8 matcher)")
        self.assertEqual(m["table"]["away"], "12:e, 11 p (8 matcher)")
        self.assertIn("1–1–2", m["facts"])
        self.assertEqual(m["injuries"]["home"], ["A (avstängd)", "B (osäker)"])
        self.assertEqual(m["injuries"]["impact"], [1, 1])
        lu = apifootball.lineups(af, m)
        self.assertEqual(lu["home"], ["P1"])
        self.assertEqual(lu["away_formation"], "3-5-2")


class TestFootballData(unittest.TestCase):
    def test_enrich(self):
        from understreck import footballdata
        team = lambda i, n, s: {"id": i, "name": n, "shortName": s}
        SU, LI, X = team(1, "Sheffield United FC", "Sheffield Utd"), team(2, "Lincoln City FC", "Lincoln"), team(3, "Other FC", "Other")
        row = lambda t, pos, pts, w, d, l: {"position": pos, "team": t, "points": pts, "playedGames": w + d + l,
                                             "won": w, "draw": d, "lost": l}
        standings = {"standings": [
            {"type": "TOTAL", "group": None, "table": [row(SU, 18, 9, 2, 3, 3), row(LI, 12, 11, 3, 2, 3)]},
            {"type": "HOME", "group": None, "table": [row(SU, 18, 4, 1, 1, 2), row(LI, 9, 4, 1, 1, 2)]},
            {"type": "AWAY", "group": None, "table": [row(SU, 18, 5, 1, 2, 1), row(LI, 3, 9, 3, 0, 1)]}]}
        mk = lambda d, h, a, gh, ga: {"utcDate": d, "homeTeam": h, "awayTeam": a, "score": {"fullTime": {"home": gh, "away": ga}}}
        played = {"matches": [mk("2026-09-20T14:00:00Z", X, LI, 0, 3), mk("2026-09-01T14:00:00Z", SU, X, 2, 0),
                              mk("2026-09-08T14:00:00Z", X, SU, 1, 1), mk("2026-09-15T14:00:00Z", LI, X, 0, 1)]}
        fd = footballdata.FootballData(None, "k")
        fd.get = lambda path, **kw: played if path.endswith("/matches") else standings
        m = {"n": 11, "home": "Sheffield United", "away": "Lincoln", "table": None, "form": {},
             "_src": {"sport": "soccer_efl_champ", "kickoff": "2026-10-10T16:00:00+02:00"}}
        footballdata.enrich(fd, [m])
        self.assertEqual(m["table"]["home"], "18:e, 9 p (8 matcher)")
        self.assertEqual(m["form"], {"home": "VO", "away": "FV"})
        self.assertIn("Lincoln borta: 3–0–1", m["facts"])

    def test_only_total_table(self):
        """Gratisnivån skickar bara TOTAL – hemma/borta ska räknas fram ur matcherna."""
        from understreck import footballdata
        A, B = {"id": 1, "name": "Arsenal FC", "shortName": "Arsenal"}, {"id": 2, "name": "Chelsea FC", "shortName": "Chelsea"}
        mk = lambda d, h, a, gh, ga: {"utcDate": d, "homeTeam": h, "awayTeam": a, "score": {"fullTime": {"home": gh, "away": ga}}}
        played = {"matches": [mk("2026-09-01T14:00:00Z", A, B, 2, 1), mk("2026-09-08T14:00:00Z", B, A, 0, 0)]}
        total = [{"position": 1, "team": A, "points": 4, "playedGames": 2, "won": 1, "draw": 1, "lost": 0},
                 {"position": 2, "team": B, "points": 1, "playedGames": 2, "won": 0, "draw": 1, "lost": 1}]
        fd = footballdata.FootballData(None, "k")
        fd.get = lambda path, **kw: played if path.endswith("/matches") else {"standings": [{"type": "TOTAL", "table": total}]}
        m = {"n": 1, "home": "Arsenal", "away": "Chelsea", "table": None, "form": {},
             "_src": {"sport": "soccer_epl", "kickoff": "2026-10-10T16:00:00+02:00"}}
        footballdata.enrich(fd, [m])
        self.assertEqual(m["facts"], "Arsenal hemma: 1–0–0 (V–O–F). Chelsea borta: 0–0–1.")

    def test_without_standings(self):
        from understreck import footballdata
        A, B = {"id": 1, "name": "Arsenal FC", "shortName": "Arsenal"}, {"id": 2, "name": "Chelsea FC", "shortName": "Chelsea"}
        mk = lambda d, h, a, gh, ga: {"utcDate": d, "homeTeam": h, "awayTeam": a, "score": {"fullTime": {"home": gh, "away": ga}}}
        played = {"matches": [mk("2026-09-01T14:00:00Z", A, B, 2, 1), mk("2026-09-08T14:00:00Z", B, A, 0, 0)]}
        fd = footballdata.FootballData(None, "k")
        fd.get = lambda path, **kw: played if path.endswith("/matches") else {"standings": []}
        m = {"n": 1, "home": "Arsenal", "away": "Chelsea", "table": None, "form": {},
             "_src": {"sport": "soccer_epl", "kickoff": "2026-10-10T16:00:00+02:00"}}
        footballdata.enrich(fd, [m])
        self.assertEqual(m["table"], {"home": "1:a, 4 p (2 matcher)", "away": "2:a, 1 p (2 matcher)"})
        self.assertEqual(m["form"], {"home": "VO", "away": "FO"})
        self.assertIn("Arsenal hemma: 1–0–0", m["facts"])


class TestResearchClean(unittest.TestCase):
    def test_tolerant(self):
        from understreck.claude import _clean
        got = _clean({"n": 13, "table": {"home": "3rd, 15 pts", "away": "4:e, 14 p"},
                      "form": {"home": "W D L W W", "away": "V-O-O-F-V"},
                      "injuries": {"home": ["A (skadad)"], "away": [], "impact": [1, 0]}})
        self.assertEqual(got["form"], {"home": "VOFVV", "away": "VOOFV"})
        self.assertEqual(got["table"]["home"], "3rd, 15 pts")
        self.assertEqual(got["injuries"]["impact"], [1, 0])
        self.assertEqual(_clean({"n": 1, "form": {"home": None, "away": "WW"}}), {})


class TestModel(unittest.TestCase):
    def test_round_matches_page(self):
        # Fast kopia av omgång 7763; siffrorna kontrollerades mot sidans JavaScript.
        import json, pathlib
        rnd = json.loads((pathlib.Path(__file__).parent / "fixtures" / "round_7763.json").read_text(encoding="utf-8"))
        an = [model.analyse(m) for m in rnd["matches"]]
        self.assertEqual([round(x * 100) for x in an[0]["p"]], [55, 24, 22])
        s = model.build_system(an, 64, profile="balans")
        self.assertEqual(round(1 / s["hit"]), 2754)


class TestResults(unittest.TestCase):
    def test_svenskaspel_parse(self):
        import json, pathlib
        from understreck import svenskaspel
        data = json.loads((pathlib.Path(__file__).parent / "fixtures" / "svs_result_4973.json").read_text(encoding="utf-8"))
        r = svenskaspel.parse_result(data)
        self.assertTrue(r["final"])
        self.assertEqual("".join(r["row"]), "22122X111X211")
        self.assertEqual(r["scores"][0], "0–7")
        self.assertEqual(r["payouts"][0], {"name": "13 rätt", "winners": 77, "amount": 59266.0})
        self.assertEqual([p["name"] for p in r["payouts"]], ["13 rätt", "12 rätt", "11 rätt", "10 rätt"])

    def test_tipsrader_live(self):
        from bs4 import BeautifulSoup
        from understreck import tipsrader
        row = lambda n, score, status, sign: f"""<tr><td>{n}</td><td class="teams"></td>
            <td class="scorecell"><span><span class="score">{score}</span></span></td><td>{status}</td>
            <td class="sign"><span class="sign-choice{' active' if sign == '1' else ''}">1</span>
            <span class="sign-choice{' active' if sign == 'X' else ''}">X</span>
            <span class="sign-choice{' active' if sign == '2' else ''}">2</span></td></tr>"""
        html = "<table id='matchestable'><tbody>" + row(1, "0-0", "49", "X") + row(2, "5-1", "FT", "1") +                row(3, "10/10 18:30", "Inte startat", "X") + "</tbody></table>"
        live = tipsrader.parse_live(BeautifulSoup(html, "html.parser"))
        self.assertEqual(live[0], {"n": 1, "score": "0–0", "sign": "X", "finished": False})
        self.assertEqual(live[1], {"n": 2, "score": "5–1", "sign": "1", "finished": True})
        self.assertEqual(live[2], {"n": 3, "score": None, "sign": None, "finished": False})

    def _round(self):
        import json, pathlib
        return json.loads((pathlib.Path(__file__).parent / "fixtures" / "round_7763.json").read_text(encoding="utf-8"))

    def test_run_results_preliminary_then_final(self):
        import understreck.__main__ as M
        rnd = self._round()
        rnd["draw"] = "4974"
        live = {"id": 7763, "matches": [{"n": i + 1, "score": "1–0", "sign": "1", "finished": True} for i in range(13)]}
        sat_evening = datetime(2026, 10, 10, 20, 30, tzinfo=TZ)
        with mock.patch.object(M, "now", lambda: sat_evening),              mock.patch.object(M.svenskaspel, "fetch_result", lambda s, d: None),              mock.patch.object(M.tipsrader, "fetch_live", lambda s: live):
            out = M.run_results(None, [rnd])
        self.assertFalse(out["results"]["final"])
        self.assertEqual("".join(out["results"]["row"]), "1" * 13)
        final = {"final": True, "row": ["X"] * 13, "scores": ["0–0"] * 13,
                 "payouts": [{"name": "13 rätt", "winners": 1, "amount": 100.0}]}
        with mock.patch.object(M, "now", lambda: sat_evening),              mock.patch.object(M.svenskaspel, "fetch_result", lambda s, d: dict(final)):
            out = M.run_results(None, [out])
        self.assertTrue(out["results"]["final"])
        with mock.patch.object(M, "now", lambda: sat_evening):
            self.assertIsNone(M.run_results(None, [out]))  # redan klar

    def test_lineups_waits_until_one_hour_before(self):
        import understreck.__main__ as M
        rnd = self._round()
        rnd["lineupUpdate"] = None
        slept = []
        morning = datetime(2026, 10, 10, 10, 0, tzinfo=TZ)
        with mock.patch.object(M, "now", lambda: morning),              mock.patch.object(M.time, "sleep", lambda s: slept.append(s) or (_ for _ in ()).throw(StopIteration)):
            with self.assertRaises(StopIteration):
                M.run_lineups(None, [rnd], wait=True)
        self.assertAlmostEqual(slept[0] / 3600, 5 + 5 / 60, places=2)  # 10:00 -> 15:05
        with mock.patch.object(M, "now", lambda: morning):
            self.assertIsNone(M.run_lineups(None, [rnd], wait=False))  # utan --wait avbryts den
        early = datetime(2026, 10, 10, 8, 0, tzinfo=TZ)
        with mock.patch.object(M, "now", lambda: early):
            self.assertIsNone(M.run_lineups(None, [rnd], wait=True))  # mer än 5,2 h kvar: senare körning tar över


if __name__ == "__main__":
    unittest.main()
