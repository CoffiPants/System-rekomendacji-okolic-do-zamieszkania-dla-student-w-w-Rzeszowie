"""Silnik rekomendacji okolic mieszkalnych i publiczny kontrakt dla aplikacji.

Odległości są mierzone w linii prostej od środka obszaru. Czas dojścia jest
wartością orientacyjną przy prędkości 4,5 km/h (75 metrów na minutę).
"""

from __future__ import annotations

import json
import math
from pathlib import Path

try:  # moduł jest importowany jako scripts.recommendation_engine albo bezpośrednio
    from .data_validation import validate_documents
except ImportError:
    from data_validation import validate_documents


CATEGORIES = ("shop", "bus_stop", "park")
DEFAULT_WEIGHTS = {"university": 3.0, "shop": 2.0, "bus_stop": 2.0, "park": 2.0}
DEFAULT_LIMITS_M = {"university": 3000.0, "shop": 1000.0, "bus_stop": 600.0, "park": 1500.0}
WALKING_SPEED_M_PER_MINUTE = 75.0
DEFAULT_AREA_RADIUS_M = 500
DISCLAIMER = (
    "Odległości są liczone w linii prostej od środka obszaru, a czas dojścia "
    "jest szacowany przy prędkości 4,5 km/h. Wynik nie uwzględnia rzeczywistych "
    "tras pieszych, przejść ani przeszkód terenowych."
)


def load_json(path: str | Path) -> dict:
    """Wczytuje dokument JSON z kodowaniem UTF-8."""
    with Path(path).open(encoding="utf-8") as stream:
        return json.load(stream)


def distance_m(a_lat: float, a_lon: float, b_lat: float, b_lon: float) -> float:
    """Zwraca odległość Haversine'a w metrach."""
    values = (a_lat, a_lon, b_lat, b_lon)
    if any(isinstance(value, bool) or not isinstance(value, (int, float))
           or not math.isfinite(value) for value in values):
        raise ValueError("Współrzędne muszą być skończonymi liczbami.")
    if not (-90 <= a_lat <= 90 and -90 <= b_lat <= 90 and
            -180 <= a_lon <= 180 and -180 <= b_lon <= 180):
        raise ValueError("Współrzędne poza dopuszczalnym zakresem.")
    radius = 6_371_000.0
    lat1, lat2 = math.radians(a_lat), math.radians(b_lat)
    dlat = lat2 - lat1
    dlon = math.radians(b_lon - a_lon)
    haversine = (math.sin(dlat / 2) ** 2
                 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2)
    return 2 * radius * math.asin(math.sqrt(min(1.0, haversine)))


def score(distance: float, limit: float) -> float:
    """Normalizuje odległość do wyniku 0-100."""
    if limit <= 0 or not math.isfinite(limit):
        raise ValueError("Limit odległości musi być dodatni.")
    return 100.0 * max(0.0, 1.0 - distance / limit)


class RecommendationEngine:
    """Waliduje dane i tworzy ranking obszarów dla wybranej lokalizacji."""

    def __init__(self, services: list[dict], locations: list[dict], areas: list[dict],
                 area_radius_m: int = DEFAULT_AREA_RADIUS_M):
        self.services = self._validate_records(services, "services")
        self.locations = self._validate_records(locations, "locations")
        self.areas = self._validate_records(areas, "areas")
        if type(area_radius_m) is not int or area_radius_m <= 0:
            raise ValueError("Promień obszaru musi być dodatnią liczbą całkowitą.")
        self.area_radius_m = area_radius_m
        if not self.services or not self.locations or not self.areas:
            raise ValueError("Zbiory usług, lokalizacji i obszarów nie mogą być puste.")
        self._services_by_category = {
            category: [item for item in self.services if item["category"] == category]
            for category in CATEGORIES
        }
        missing = [category for category, items in self._services_by_category.items() if not items]
        if missing:
            raise ValueError("Brak usług w kategoriach: " + ", ".join(missing))

    @classmethod
    def from_files(cls, services_path: str | Path, locations_path: str | Path,
                   areas_path: str | Path) -> "RecommendationEngine":
        services_document = load_json(services_path)
        locations_document = load_json(locations_path)
        areas_document = load_json(areas_path)
        validate_documents(services_document, locations_document, areas_document)
        return cls(
            services_document.get("services", []),
            locations_document.get("locations", []),
            areas_document.get("areas", []),
            area_radius_m=areas_document.get("radius_m", DEFAULT_AREA_RADIUS_M),
        )

    @staticmethod
    def _validate_records(records: object, name: str) -> list[dict]:
        if not isinstance(records, list) or any(not isinstance(item, dict) for item in records):
            raise ValueError(f"Zbiór {name} musi być listą obiektów.")
        required = {"latitude", "longitude"}
        if name == "services":
            required |= {"category"}
        if name == "locations":
            required |= {"id", "name"}
        if name == "areas":
            required |= {"id", "name", "district"}
        for item in records:
            missing = required - item.keys()
            if missing:
                raise ValueError(f"Rekord {name} nie ma pól: {', '.join(sorted(missing))}.")
            distance_m(item["latitude"], item["longitude"],
                       item["latitude"], item["longitude"])
        return records

    def _location(self, location_id: str) -> dict:
        for location in self.locations:
            if location["id"] == location_id:
                return location
        raise ValueError(f"Nie znaleziono lokalizacji uczelni: {location_id}")

    def recommend(self, location_id: str, weights: dict[str, float] | None = None,
                  max_walk_minutes: float | None = None, top_n: int = 3) -> list[dict]:
        """Zwraca ranking obszarów z uzasadnieniem, posortowany deterministycznie."""
        if type(top_n) is not int or top_n <= 0:
            raise ValueError("top_n musi być dodatnią liczbą całkowitą.")
        if max_walk_minutes is not None and (
                isinstance(max_walk_minutes, bool) or max_walk_minutes <= 0
                or not math.isfinite(max_walk_minutes)):
            raise ValueError("Limit czasu dojścia musi być dodatni.")
        selected_weights = dict(DEFAULT_WEIGHTS)
        if weights is not None:
            unknown = set(weights) - set(DEFAULT_WEIGHTS)
            if unknown:
                raise ValueError("Nieznane wagi: " + ", ".join(sorted(unknown)))
            for key, value in weights.items():
                if (isinstance(value, bool) or not isinstance(value, (int, float))
                        or not math.isfinite(value) or value < 0):
                    raise ValueError(f"Waga {key} musi być nieujemną, skończoną liczbą.")
                selected_weights[key] = float(value)
        if sum(selected_weights.values()) <= 0:
            raise ValueError("Co najmniej jedna waga musi być dodatnia.")

        location = self._location(location_id)
        results = []
        for area in self.areas:
            distances = {
                "university": distance_m(area["latitude"], area["longitude"],
                                         location["latitude"], location["longitude"]),
            }
            distances.update({
                category: min(distance_m(area["latitude"], area["longitude"],
                                         item["latitude"], item["longitude"])
                              for item in items)
                for category, items in self._services_by_category.items()
            })
            walk_minutes = distances["university"] / WALKING_SPEED_M_PER_MINUTE
            if max_walk_minutes is not None and walk_minutes > max_walk_minutes:
                continue
            scores = {
                category: score(distances[category], DEFAULT_LIMITS_M[category])
                for category in DEFAULT_LIMITS_M
            }
            total_weight = sum(selected_weights.values())
            total_score = sum(scores[key] * selected_weights[key]
                              for key in selected_weights) / total_weight
            strongest = sorted(
                ((scores[key], key) for key in selected_weights if selected_weights[key] > 0),
                reverse=True,
            )
            reasons = [
                f"{self._label(category)}: {distances[category]:.0f} m"
                for _, category in strongest[:2]
            ]
            results.append({
                "rank": 0,
                "area_id": area["id"],
                "area_name": area["name"],
                "district": area["district"],
                "center_lat": float(area["latitude"]),
                "center_lon": float(area["longitude"]),
                "radius_m": self.area_radius_m,
                "score": round(total_score, 4),
                "walk_distance_m": round(distances["university"], 2),
                "walk_time_to_univ_min": round(walk_minutes, 2),
                "distances_m": {key: round(value, 2) for key, value in distances.items()},
                "scores": {key: round(value, 4) for key, value in scores.items()},
                "justification": "; ".join(reasons),
            })
        results.sort(key=lambda row: (-row["score"], row["area_id"]))
        for rank_number, result in enumerate(results[:top_n], 1):
            result["rank"] = rank_number
        return results[:top_n]

    @staticmethod
    def _label(category: str) -> str:
        return {
            "university": "uczelnia",
            "shop": "sklep",
            "bus_stop": "przystanek",
            "park": "park",
        }[category]


def generate_recommendations(request: object,
                             engine: RecommendationEngine | None = None) -> dict:
    """Realizuje publiczny kontrakt Request/Response wykorzystywany przez UI.

    Oczekiwane pola żądania: ``location_id``, ``max_walk_time_minutes`` i
    ``weights``. Błędy wejścia i danych są zwracane jako statusy, nie wyjątki.
    ``engine`` można przekazać z aplikacji, aby użyć już wczytanych danych.
    """
    def response(status: str, message: str, recommendations: list[dict] | None = None) -> dict:
        return {
            "status": status,
            "message": message,
            "disclaimer": DISCLAIMER,
            "recommendations": recommendations or [],
        }

    if not isinstance(request, dict):
        return response("VALIDATION_ERROR", "Żądanie musi być słownikiem parametrów.")

    required = {"location_id", "max_walk_time_minutes", "weights"}
    missing = required - request.keys()
    if missing:
        return response(
            "VALIDATION_ERROR",
            "Brak wymaganych pól: " + ", ".join(sorted(missing)) + ".",
        )

    location_id = request["location_id"]
    if not isinstance(location_id, str) or not location_id.strip():
        return response("VALIDATION_ERROR", "location_id musi być niepustym tekstem.")

    max_walk_minutes = request["max_walk_time_minutes"]
    if max_walk_minutes is not None and (
            type(max_walk_minutes) is not int or max_walk_minutes not in (15, 30, 45)):
        return response(
            "VALIDATION_ERROR",
            "Limit czasu musi wynosić 15, 30 lub 45 minut albo być równy None.",
        )

    weights = request["weights"]
    if not isinstance(weights, dict) or set(weights) != set(DEFAULT_WEIGHTS):
        return response(
            "VALIDATION_ERROR",
            "Wagi muszą zawierać kryteria university, shop, bus_stop i park.",
        )
    if any(type(value) is not int or value not in (1, 2, 3) for value in weights.values()):
        return response("VALIDATION_ERROR", "Każda waga musi być liczbą całkowitą od 1 do 3.")

    if engine is None:
        root = Path(__file__).resolve().parents[1]
        try:
            engine = RecommendationEngine.from_files(
                root / "data/processed/services.json",
                root / "data/processed/universities.json",
                root / "config/residential-areas.json",
            )
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
            return response(
                "DATA_ERROR",
                f"Nie można wczytać danych rekomendacji: {error}. "
                "Sprawdź pliki danych i uruchom scripts/prepare_data.py.",
            )

    if not isinstance(engine, RecommendationEngine):
        return response("DATA_ERROR", "Nieprawidłowy silnik rekomendacji.")

    if not any(location.get("id") == location_id for location in engine.locations):
        return response("VALIDATION_ERROR", f"Nie znaleziono lokalizacji uczelni: {location_id}.")

    try:
        recommendations = engine.recommend(
            location_id=location_id,
            weights=weights,
            max_walk_minutes=max_walk_minutes,
            top_n=3,
        )
    except (ValueError, KeyError, TypeError) as error:
        return response("DATA_ERROR", f"Nie udało się obliczyć rekomendacji: {error}.")

    if not recommendations:
        return response(
            "NO_MATCHES",
            "Nie znaleziono okolic spełniających limit czasu dojścia. "
            "Zwiększ limit lub wybierz brak limitu.",
        )

    return response(
        "SUCCESS",
        f"Znaleziono {len(recommendations)} dopasowanych okolic.",
        recommendations,
    )
