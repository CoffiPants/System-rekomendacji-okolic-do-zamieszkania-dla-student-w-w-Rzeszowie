import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from recommendation_engine import (
    RecommendationEngine,
    WALKING_SPEED_M_PER_MINUTE,
    distance_m,
    generate_recommendations,
    score,
)


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
        self.assertIn("sklep", ranking[0]["justification"])
        self.assertIn("walk_time_to_univ_min", ranking[0])

    def test_walk_limit_filters_areas(self):
        ranking = self.engine.recommend("u1", max_walk_minutes=1)
        self.assertEqual([item["area_id"] for item in ranking], ["near"])

    def test_public_api_returns_architecture_contract(self):
        response = generate_recommendations(
            {
                "location_id": "u1",
                "max_walk_time_minutes": 15,
                "weights": {"university": 3, "shop": 2, "bus_stop": 2, "park": 1},
            },
            engine=self.engine,
        )

        self.assertEqual(response["status"], "SUCCESS")
        self.assertEqual(response["recommendations"][0]["area_id"], "near")
        self.assertIn("center_lat", response["recommendations"][0])
        self.assertEqual(response["recommendations"][0]["radius_m"], 500)
        self.assertIn("walk_time_to_univ_min", response["recommendations"][0])
        self.assertIn("justification", response["recommendations"][0])
        self.assertNotIn("walk_time_minutes", response["recommendations"][0])
        self.assertNotIn("reason", response["recommendations"][0])
        self.assertIn("4,5 km/h", response["disclaimer"])

    def test_public_api_returns_no_matches_status(self):
        far_only_engine = RecommendationEngine(
            self.engine.services,
            self.engine.locations,
            [self.engine.areas[1]],
        )
        response = generate_recommendations(
            {
                "location_id": "u1",
                "max_walk_time_minutes": 15,
                "weights": {"university": 3, "shop": 2, "bus_stop": 2, "park": 1},
            },
            engine=far_only_engine,
        )

        self.assertEqual(response["status"], "NO_MATCHES")
        self.assertEqual(response["recommendations"], [])

    def test_public_api_validates_weights_and_uses_4_5_kmh(self):
        response = generate_recommendations(
            {
                "location_id": "u1",
                "max_walk_time_minutes": None,
                "weights": {"university": 0, "shop": 2, "bus_stop": 2, "park": 1},
            },
            engine=self.engine,
        )

        self.assertEqual(response["status"], "VALIDATION_ERROR")
        self.assertEqual(WALKING_SPEED_M_PER_MINUTE, 75.0)

    def test_invalid_weight_is_rejected(self):
        with self.assertRaises(ValueError):
            self.engine.recommend("u1", weights={"shop": -1})


if __name__ == "__main__":
    unittest.main()
