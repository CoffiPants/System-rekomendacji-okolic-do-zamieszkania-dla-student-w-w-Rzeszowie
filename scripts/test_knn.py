import unittest

from knn_recommender import knn_recommend


class TestKNN(unittest.TestCase):

    def setUp(self):
        self.areas = [
            {
                "area_id": "A",
                "area_name": "Okolica A",
                "university_score": 100,
                "shop_score": 100,
                "bus_stop_score": 100,
                "park_score": 100,
            },
            {
                "area_id": "B",
                "area_name": "Okolica B",
                "university_score": 50,
                "shop_score": 50,
                "bus_stop_score": 50,
                "park_score": 50,
            },
        ]

        self.preferences = {
            "university_score": 100,
            "shop_score": 100,
            "bus_stop_score": 100,
            "park_score": 100,
        }

    def test_best_match(self):
        result = knn_recommend(
            self.areas,
            self.preferences,
            k=1,
        )

        self.assertEqual(result[0]["area_id"], "A")
        self.assertEqual(result[0]["knn_distance"], 0)

    def test_invalid_k(self):
        with self.assertRaises(ValueError):
            knn_recommend(
                self.areas,
                self.preferences,
                k=0,
            )

    def test_missing_preferences(self):
        with self.assertRaises(ValueError):
            knn_recommend(
                self.areas,
                {},
                k=1,
            )


if __name__ == "__main__":
    unittest.main()