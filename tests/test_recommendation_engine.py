import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from recommendation_engine import RecommendationEngine, distance_m, score


class RecommendationEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = RecommendationEngine(
            [
                {"category": "shop", "latitude": 50.000, "longitude": 22.000},
                {"category": "bus_stop", "latitude": 50.001, "longitude": 22.000},
                {"category": "park", "latitude": 50.002, "longitude": 22.000},
            ],
            [{"id": "u1", "name": "Budynek A", "latitude": 50.000, "longitude": 22.000}],
            [
                {"id": "near", "name": "Blisko", "district": "D1",
                 "latitude": 50.000, "longitude": 22.000},
                {"id": "far", "name": "Daleko", "district": "D2",
                 "latitude": 50.050, "longitude": 22.000},
            ],
        )

    def test_distance_and_score_are_normalized(self):
        self.assertAlmostEqual(distance_m(50, 22, 50, 22), 0)
        self.assertEqual(score(150, 300), 50)
        self.assertEqual(score(400, 300), 0)

    def test_ranking_contains_top_three_fields_and_is_deterministic(self):
        ranking = self.engine.recommend("u1", top_n=1)
        self.assertEqual([item["area_id"] for item in ranking], ["near"])
        self.assertEqual(ranking[0]["rank"], 1)
        self.assertIn("sklep", ranking[0]["reason"])
        self.assertIn("walk_time_minutes", ranking[0])

    def test_walk_limit_filters_areas(self):
        ranking = self.engine.recommend("u1", max_walk_minutes=1)
        self.assertEqual([item["area_id"] for item in ranking], ["near"])

    def test_invalid_weight_is_rejected(self):
        with self.assertRaises(ValueError):
            self.engine.recommend("u1", weights={"shop": -1})


if __name__ == "__main__":
    unittest.main()
