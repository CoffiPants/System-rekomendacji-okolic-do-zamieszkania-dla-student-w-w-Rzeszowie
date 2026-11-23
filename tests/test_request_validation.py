"""Testy parametrów żądania i test integracyjny na danych projektu (Valentyna Boksha, Lab 7).

Sprawdzają publiczną funkcję ``generate_recommendations`` zgodnie z kontraktem
z ``docs/architecture.md`` (punkt 4).
"""

import math
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from recommendation_engine import RecommendationEngine, generate_recommendations


WEIGHTS = {"university": 2, "shop": 2, "bus_stop": 2, "park": 2}
ALLOWED_LIMITS = (15, 30, 45, None)


def load_project_engine():
    return RecommendationEngine.from_files(
        ROOT / "data/processed/services.json",
        ROOT / "data/processed/universities.json",
        ROOT / "config/residential-areas.json",
    )


class RequestValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = load_project_engine()
        cls.location_id = cls.engine.locations[0]["id"]

    def request(self, **changes):
        request = {
            "location_id": self.location_id,
            "max_walk_time_minutes": 30,
            "weights": dict(WEIGHTS),
        }
        request.update(changes)
        return request

    def status(self, request):
        return generate_recommendations(request, engine=self.engine)["status"]

    def assert_validation_error(self, request):
        response = generate_recommendations(request, engine=self.engine)
        self.assertEqual(response["status"], "VALIDATION_ERROR")
        self.assertEqual(response["recommendations"], [])
        self.assertTrue(response["message"].strip())

    # --- żądanie ------------------------------------------------------------

    def test_request_must_be_a_dictionary(self):
        for request in (None, [], "way/1"):
            with self.subTest(request=request):
                self.assert_validation_error(request)

    def test_missing_request_field_is_rejected(self):
        for field in ("location_id", "max_walk_time_minutes", "weights"):
            with self.subTest(field=field):
                request = self.request()
                del request[field]
                self.assert_validation_error(request)

    # --- location_id --------------------------------------------------------

    def test_unknown_location_is_rejected(self):
        self.assert_validation_error(self.request(location_id="way/0"))

    def test_invalid_location_type_is_rejected(self):
        for value in ("", "   ", None, 208515700):
            with self.subTest(value=value):
                self.assert_validation_error(self.request(location_id=value))

    # --- wagi ---------------------------------------------------------------

    def test_boundary_weights_are_accepted(self):
        for value in (1, 3):
            with self.subTest(weight=value):
                weights = dict.fromkeys(WEIGHTS, value)
                self.assertEqual(self.status(self.request(weights=weights)), "SUCCESS")

    def test_weights_outside_range_are_rejected(self):
        for value in (0, 4, -1):
            with self.subTest(weight=value):
                weights = dict(WEIGHTS, shop=value)
                self.assert_validation_error(self.request(weights=weights))

    def test_invalid_weight_type_is_rejected(self):
        for value in (2.0, "2", None, True, float("nan"), float("inf")):
            with self.subTest(weight=value):
                weights = dict(WEIGHTS, park=value)
                self.assert_validation_error(self.request(weights=weights))

    def test_incomplete_or_extended_weights_are_rejected(self):
        incomplete = {key: value for key, value in WEIGHTS.items() if key != "park"}
        extended = dict(WEIGHTS, pharmacy=2)
        for weights in (incomplete, extended, {}, None, [2, 2, 2, 2]):
            with self.subTest(weights=weights):
                self.assert_validation_error(self.request(weights=weights))

    # --- limit czasu --------------------------------------------------------

    def test_allowed_time_limits_are_accepted(self):
        for limit in ALLOWED_LIMITS:
            with self.subTest(limit=limit):
                status = self.status(self.request(max_walk_time_minutes=limit))
                self.assertIn(status, ("SUCCESS", "NO_MATCHES"))

    def test_other_time_limits_are_rejected(self):
        for limit in (0, 1, 14, 16, 60, -15, 15.0, "15", True, float("nan"), float("inf")):
            with self.subTest(limit=limit):
                self.assert_validation_error(self.request(max_walk_time_minutes=limit))

    # --- silnik niskiego poziomu -------------------------------------------

    def test_engine_rejects_non_finite_weight(self):
        for value in (float("nan"), float("inf")):
            with self.subTest(weight=value):
                with self.assertRaises(ValueError):
                    self.engine.recommend(self.location_id, weights={"shop": value})


class ProjectDataIntegrationTests(unittest.TestCase):
    """Pliki projektu -> wczytanie -> żądanie -> odpowiedź, dla każdego miejsca zajęć."""

    @classmethod
    def setUpClass(cls):
        cls.engine = load_project_engine()

    def test_every_location_and_limit_gives_a_consistent_response(self):
        area_ids = {area["id"] for area in self.engine.areas}
        statuses = set()
        for location in self.engine.locations:
            for limit in ALLOWED_LIMITS:
                with self.subTest(location=location["id"], limit=limit):
                    response = generate_recommendations(
                        {"location_id": location["id"],
                         "max_walk_time_minutes": limit,
                         "weights": dict(WEIGHTS)},
                        engine=self.engine,
                    )
                    results = response["recommendations"]
                    statuses.add(response["status"])
                    self.assertIn(response["status"], ("SUCCESS", "NO_MATCHES"))
                    self.assertEqual(response["status"] == "SUCCESS", bool(results))
                    self.assertLessEqual(len(results), 3)
                    self.assertTrue(response["disclaimer"].strip())
                    self.assertEqual([item["rank"] for item in results],
                                     list(range(1, len(results) + 1)))
                    self.assertEqual(
                        results,
                        sorted(results, key=lambda item: (-item["score"], item["area_id"])))
                    for item in results:
                        self.assertIn(item["area_id"], area_ids)
                        self.assertTrue(math.isfinite(item["score"]))
                        self.assertTrue(0 <= item["score"] <= 100)
                        self.assertEqual(item["radius_m"], 500)
                        self.assertTrue(item["justification"].strip())
                        if limit is not None:
                            self.assertLessEqual(item["walk_time_to_univ_min"], limit)
        # W danych projektu występują oba statusy: jest miejsce zajęć bez okolic w 15 minut.
        self.assertEqual(statuses, {"SUCCESS", "NO_MATCHES"})

    def test_same_request_gives_same_response(self):
        request = {"location_id": self.engine.locations[0]["id"],
                   "max_walk_time_minutes": None, "weights": dict(WEIGHTS)}
        first = generate_recommendations(request, engine=self.engine)
        second = generate_recommendations(request, engine=self.engine)
        self.assertEqual(first, second)

    def test_walk_time_matches_distance_at_4_5_kmh(self):
        response = generate_recommendations(
            {"location_id": self.engine.locations[0]["id"],
             "max_walk_time_minutes": None, "weights": dict(WEIGHTS)},
            engine=self.engine,
        )
        for item in response["recommendations"]:
            self.assertAlmostEqual(
                item["walk_time_to_univ_min"], item["walk_distance_m"] / 75.0, places=1)


if __name__ == "__main__":
    unittest.main()
