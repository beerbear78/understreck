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


class TestModel(unittest.TestCase):
    def test_round_matches_page(self):
        r = store.load()
        if not r or r[0]["id"] != 7763:
            self.skipTest("referensomgången finns inte längre")
        an = [model.analyse(m) for m in r[0]["matches"]]
        self.assertEqual([round(x * 100) for x in an[0]["p"]], [55, 24, 22])
        s = model.build_system(an, 64, profile="balans")
        self.assertEqual(round(1 / s["hit"]), 2754)


if __name__ == "__main__":
    unittest.main()
