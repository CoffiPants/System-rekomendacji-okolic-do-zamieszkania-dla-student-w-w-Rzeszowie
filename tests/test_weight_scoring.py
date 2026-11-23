"""Test wymagania R2: wpływ wag na ocenę, z ręcznym obliczeniem (Valentyna Boksha, Lab 7).

Punkty leżą na jednym południku, więc odległość jest równa różnicy szerokości
geograficznej pomnożonej przez długość jednego stopnia. Dzięki temu odległości
są znane z góry, a oczekiwane oceny można policzyć ręcznie ze wzoru

    ocena kryterium = 100 * max(0, 1 - odległość / limit)
    ocena końcowa   = suma(ocena kryterium * waga) / suma(wag)

Limity: uczelnia 3000 m, sklep 1000 m, przystanek 600 m, park 1500 m.
"""

import math
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from recommendation_engine import RecommendationEngine, generate_recommendations


METERS_PER_DEGREE = 6_371_000.0 * math.pi / 180.0
UNIVERSITY_LATITUDE = 50.0
LONGITUDE = 22.0


def point(meters_north_of_university, **fields):
    """Rekord położony o podaną liczbę metrów na północ (minus: na południe) od uczelni."""
    latitude = UNIVERSITY_LATITUDE + meters_north_of_university / METERS_PER_DEGREE
    return dict(fields, latitude=latitude, longitude=LONGITUDE)


def ask(engine, **weights):
    selected = {"university": 1, "shop": 1, "bus_stop": 1, "park": 1}
    selected.update(weights)
    response = generate_recommendations(
        {"location_id": "u", "max_walk_time_minutes": None, "weights": selected},
        engine=engine,
    )
    assert response["status"] == "SUCCESS", response["message"]
    return response["recommendations"]


class SingleAreaScoreTests(unittest.TestCase):
    """Jeden obszar: uczelnia 1500 m, sklep 250 m, przystanek 300 m, park 1200 m.

    Oceny kryteriów policzone ręcznie:
        uczelnia   100 * (1 - 1500/3000) = 50
        sklep      100 * (1 -  250/1000) = 75
        przystanek 100 * (1 -  300/600)  = 50
        park       100 * (1 - 1200/1500) = 20
    """

    def setUp(self):
        self.engine = RecommendationEngine(
            [
                point(1500 + 250, category="shop"),
                point(1500 + 300, category="bus_stop"),
                point(1500 + 1200, category="park"),
            ],
            [point(0, id="u", name="Uczelnia")],
            [point(1500, id="a", name="Obszar", district="D")],
        )

    def test_distances_and_criterion_scores(self):
        result = ask(self.engine)[0]
        expected_distances = {"university": 1500, "shop": 250, "bus_stop": 300, "park": 1200}
        expected_scores = {"university": 50, "shop": 75, "bus_stop": 50, "park": 20}
        for key in expected_distances:
            with self.subTest(criterion=key):
                self.assertAlmostEqual(result["distances_m"][key], expected_distances[key], places=1)
                self.assertAlmostEqual(result["scores"][key], expected_scores[key], places=2)

    def test_final_score_for_each_weight_setting(self):
        cases = [
            # wagi                      ręczne obliczenie                    wynik
            ({},                        (50 + 75 + 50 + 20) / 4),            # 48,75
            ({"university": 3},         (3 * 50 + 75 + 50 + 20) / 6),        # 49,17
            ({"shop": 3},               (50 + 3 * 75 + 50 + 20) / 6),        # 57,50
            ({"bus_stop": 3},           (50 + 75 + 3 * 50 + 20) / 6),        # 49,17
            ({"park": 3},               (50 + 75 + 50 + 3 * 20) / 6),        # 39,17
            ({"shop": 2, "park": 3},    (50 + 2 * 75 + 50 + 3 * 20) / 7),    # 44,29
            ({"university": 3, "shop": 3, "bus_stop": 3, "park": 3},
             (50 + 75 + 50 + 20) / 4),                                       # 48,75
        ]
        for weights, expected in cases:
            with self.subTest(weights=weights):
                self.assertAlmostEqual(ask(self.engine, **weights)[0]["score"], expected, places=2)

    def test_higher_weight_moves_score_towards_that_criterion(self):
        base = ask(self.engine)[0]["score"]                 # 48,75
        self.assertGreater(ask(self.engine, shop=3)[0]["score"], base)   # sklep 75 > 48,75
        self.assertLess(ask(self.engine, park=3)[0]["score"], base)      # park 20 < 48,75

    def test_service_beyond_scoring_limit_gives_zero_but_keeps_area(self):
        engine = RecommendationEngine(
            [
                point(1500 + 250, category="shop"),
                point(1500 + 300, category="bus_stop"),
                point(1500 + 2000, category="park"),     # 2000 m > limit 1500 m
            ],
            self.engine.locations,
            self.engine.areas,
        )
        result = ask(engine)[0]
        self.assertEqual(result["scores"]["park"], 0)
        self.assertAlmostEqual(result["score"], (50 + 75 + 50 + 0) / 4, places=2)   # 43,75


class TwoAreaOrderTests(unittest.TestCase):
    """Dwa obszary, w których zmiana wagi zmienia kolejność rankingu.

                 uczelnia        sklep          przystanek     park
    obszar "a"   600 m -> 80     800 m -> 20    300 m -> 50    750 m -> 50
    obszar "b"   2400 m -> 20    200 m -> 80    300 m -> 50    750 m -> 50
    """

    def setUp(self):
        self.engine = RecommendationEngine(
            [
                point(600 + 800, category="shop"),
                point(600 + 300, category="bus_stop"),
                point(600 + 750, category="park"),
                point(-2400 - 200, category="shop"),
                point(-2400 - 300, category="bus_stop"),
                point(-2400 - 750, category="park"),
            ],
            [point(0, id="u", name="Uczelnia")],
            [
                point(-2400, id="b", name="Przy sklepie", district="D"),
                point(600, id="a", name="Przy uczelni", district="D"),
            ],
        )

    def ranking(self, **weights):
        return [(item["area_id"], item["score"]) for item in ask(self.engine, **weights)]

    def assert_ranking(self, actual, expected):
        self.assertEqual([area for area, _ in actual], [area for area, _ in expected])
        for (_, actual_score), (_, expected_score) in zip(actual, expected):
            self.assertAlmostEqual(actual_score, expected_score, places=2)

    def test_equal_weights_give_a_tie_resolved_by_area_id(self):
        # a: (80 + 20 + 50 + 50) / 4 = 50;  b: (20 + 80 + 50 + 50) / 4 = 50
        self.assert_ranking(self.ranking(), [("a", 50), ("b", 50)])

    def test_university_weight_puts_area_near_university_first(self):
        # a: (3*80 + 20 + 50 + 50) / 6 = 60;  b: (3*20 + 80 + 50 + 50) / 6 = 40
        self.assert_ranking(self.ranking(university=3), [("a", 60), ("b", 40)])

    def test_shop_weight_puts_area_near_shop_first(self):
        # a: (80 + 3*20 + 50 + 50) / 6 = 40;  b: (20 + 3*80 + 50 + 50) / 6 = 60
        self.assert_ranking(self.ranking(shop=3), [("b", 60), ("a", 40)])


if __name__ == "__main__":
    unittest.main()
