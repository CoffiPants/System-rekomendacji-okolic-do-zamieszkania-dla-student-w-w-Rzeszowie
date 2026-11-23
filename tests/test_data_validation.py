"""Testy wczytywania i walidacji plików danych (Valentyna Boksha, Lab 7).

Każdy test tworzy własne pliki w katalogu tymczasowym. Pliki projektu w
``data/`` i ``config/`` są tylko odczytywane.
"""

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from data_validation import DataValidationError, find_violations, validate_documents
from recommendation_engine import RecommendationEngine


# Wyjątki, które app.py zamienia na komunikat "Nie można wczytać danych projektu".
HANDLED_BY_APP = (OSError, ValueError, KeyError, TypeError)


def valid_documents():
    """Najmniejszy poprawny zestaw: po jednej usłudze z kategorii, 1 miejsce, 2 obszary."""
    services = {"services": [
        {"id": "node/1", "category": "shop", "latitude": 50.000, "longitude": 22.000},
        {"id": "node/2", "category": "bus_stop", "latitude": 50.001, "longitude": 22.000},
        {"id": "node/3", "category": "park", "latitude": 50.002, "longitude": 22.000},
    ]}
    locations = {"locations": [
        {"id": "way/1", "university": "UR", "name": "Budynek A",
         "address": "Testowa 1, Rzeszów", "latitude": 50.000, "longitude": 22.000},
    ]}
    areas = {"radius_m": 500, "areas": [
        {"id": "a-1", "name": "Blisko", "district": "D1",
         "latitude": 50.000, "longitude": 22.000},
        {"id": "a-2", "name": "Daleko", "district": "D2",
         "latitude": 50.050, "longitude": 22.000},
    ]}
    return services, locations, areas


class FileLoadingTests(unittest.TestCase):
    """Testy przez RecommendationEngine.from_files, czyli tak jak wczytuje aplikacja."""

    def setUp(self):
        self._directory = tempfile.TemporaryDirectory()
        self.addCleanup(self._directory.cleanup)
        self.directory = Path(self._directory.name)
        self.services, self.locations, self.areas = valid_documents()

    def write(self, name, content):
        path = self.directory / name
        if isinstance(content, str):
            path.write_text(content, encoding="utf-8")
        else:
            path.write_text(json.dumps(content, ensure_ascii=False), encoding="utf-8")
        return path

    def load(self):
        return RecommendationEngine.from_files(
            self.write("services.json", self.services),
            self.write("universities.json", self.locations),
            self.write("areas.json", self.areas),
        )

    def assert_rejected(self, fragment):
        with self.assertRaises(HANDLED_BY_APP) as caught:
            self.load()
        self.assertIn(fragment, str(caught.exception))

    # --- przypadek poprawny -------------------------------------------------

    def test_valid_files_are_loaded(self):
        engine = self.load()
        self.assertEqual(
            (len(engine.services), len(engine.locations), len(engine.areas)), (3, 1, 2))

    def test_project_files_are_loaded(self):
        engine = RecommendationEngine.from_files(
            ROOT / "data/processed/services.json",
            ROOT / "data/processed/universities.json",
            ROOT / "config/residential-areas.json",
        )
        self.assertEqual(
            (len(engine.services), len(engine.locations), len(engine.areas)), (500, 28, 25))

    # --- pliki --------------------------------------------------------------

    def test_missing_file_is_reported(self):
        with self.assertRaises(OSError):
            RecommendationEngine.from_files(
                self.directory / "brak.json",
                self.write("universities.json", self.locations),
                self.write("areas.json", self.areas),
            )

    def test_damaged_json_is_reported(self):
        self.services = '{"services": [{"id": "node/1", '
        with self.assertRaises(ValueError):
            self.load()

    def test_top_level_list_is_rejected(self):
        for name in ("services", "locations", "areas"):
            with self.subTest(document=name):
                self.services, self.locations, self.areas = valid_documents()
                setattr(self, name, [])
                self.assert_rejected("musi być obiektem JSON")

    def test_missing_record_list_is_rejected(self):
        self.locations = {"universities": self.locations["locations"]}
        self.assert_rejected("nie zawiera listy locations")

    def test_empty_record_list_is_rejected(self):
        for name in ("services", "locations", "areas"):
            with self.subTest(document=name):
                self.services, self.locations, self.areas = valid_documents()
                getattr(self, name)[name] = []
                self.assert_rejected(f"Lista {name} jest pusta")

    def test_record_that_is_not_an_object_is_rejected(self):
        self.areas["areas"].append("a-3")
        self.assert_rejected("rekord nie jest obiektem")

    # --- identyfikatory -----------------------------------------------------

    def test_duplicate_id_is_rejected(self):
        for name in ("services", "locations", "areas"):
            with self.subTest(document=name):
                self.services, self.locations, self.areas = valid_documents()
                records = getattr(self, name)[name]
                records.append(copy.deepcopy(records[0]))
                self.assert_rejected("powtórzony identyfikator")

    def test_missing_id_is_rejected(self):
        del self.areas["areas"][0]["id"]
        self.assert_rejected("brak identyfikatora id")

    # --- współrzędne --------------------------------------------------------

    def test_invalid_coordinates_are_rejected(self):
        cases = [("latitude", 200), ("latitude", -91), ("longitude", 181),
                 ("latitude", "50.0"), ("longitude", None), ("latitude", True)]
        for field, value in cases:
            with self.subTest(field=field, value=value):
                self.services, self.locations, self.areas = valid_documents()
                self.services["services"][0][field] = value
                self.assert_rejected(f"nieprawidłowa lub brakująca {field}")

    def test_missing_coordinate_is_rejected(self):
        del self.locations["locations"][0]["longitude"]
        self.assert_rejected("nieprawidłowa lub brakująca longitude")

    def test_nan_coordinate_is_rejected(self):
        # json.dumps zapisuje NaN jako literał, który json.load odczytuje jako float('nan').
        self.areas["areas"][0]["latitude"] = float("nan")
        self.assert_rejected("nieprawidłowa lub brakująca latitude")

    def test_boundary_coordinates_are_accepted(self):
        self.services["services"][0].update(latitude=90, longitude=-180)
        self.assertEqual(len(self.load().services), 3)

    # --- kategorie ----------------------------------------------------------

    def test_unknown_category_is_rejected(self):
        self.services["services"][0]["category"] = "pharmacy"
        self.assert_rejected("nieznana kategoria pharmacy")

    def test_missing_category_is_rejected(self):
        del self.services["services"][0]["category"]
        self.assert_rejected("brak pola category")

    def test_category_without_any_service_is_rejected(self):
        self.services["services"] = [
            item for item in self.services["services"] if item["category"] != "park"]
        self.assert_rejected("Brak usług w kategoriach: park")

    # --- pola używane przez interfejs --------------------------------------

    def test_location_fields_used_by_interface_are_required(self):
        for field in ("university", "name", "address"):
            for label, change in (("brak", "delete"), ("pusty", "blank")):
                with self.subTest(field=field, case=label):
                    self.services, self.locations, self.areas = valid_documents()
                    record = self.locations["locations"][0]
                    if change == "delete":
                        del record[field]
                    else:
                        record[field] = "  "
                    self.assert_rejected(f"brak pola {field}")

    def test_area_fields_used_in_results_are_required(self):
        for field in ("name", "district"):
            with self.subTest(field=field):
                self.services, self.locations, self.areas = valid_documents()
                del self.areas["areas"][0][field]
                self.assert_rejected(f"brak pola {field}")


class ViolationReportTests(unittest.TestCase):
    """Testy samych funkcji walidacji, bez plików."""

    def test_valid_documents_have_no_violations(self):
        services, locations, areas = valid_documents()
        self.assertEqual(find_violations(services, "services"), [])
        self.assertEqual(find_violations(locations, "locations"), [])
        self.assertEqual(find_violations(areas, "areas"), [])
        self.assertIsNone(validate_documents(services, locations, areas))

    def test_message_names_the_record(self):
        services, _, _ = valid_documents()
        services["services"][1]["latitude"] = 200
        self.assertEqual(
            find_violations(services, "services"),
            ["services[1] (id node/2): nieprawidłowa lub brakująca latitude."])

    def test_all_violations_are_collected_and_message_is_shortened(self):
        services, locations, areas = valid_documents()
        services["services"] = [
            {"id": f"node/{number}", "category": "shop", "latitude": 200, "longitude": 22.0}
            for number in range(8)
        ]
        with self.assertRaises(DataValidationError) as caught:
            validate_documents(services, locations, areas)
        self.assertEqual(len(caught.exception.errors), 8)
        self.assertIn("oraz 3 kolejnych naruszeń", str(caught.exception))

    def test_unknown_dataset_name_is_a_programming_error(self):
        with self.assertRaises(ValueError):
            find_violations({}, "parks")


if __name__ == "__main__":
    unittest.main()
