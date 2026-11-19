"""KNN: rekomendacja okolic na podstawie podobienstwa do profilu studenta."""

import math


FEATURES = ("university_score", "shop_score", "bus_stop_score", "park_score")


def knn_recommend(rows, preferences, k=3, weights=None):
    """
    Wybiera k obszarow najblizszych profilowi studenta.

    rows: lista obszarow z ocenami 0-100
    preferences: oczekiwane oceny dla czterech kryteriow
    weights: znaczenie poszczegolnych kryteriow
    """
    if not 1 <= k <= len(rows):
        raise ValueError("Nieprawidlowa liczba sasiadow k")

    if weights is None:
        weights = {feature: 1.0 for feature in FEATURES}

    if any(feature not in preferences for feature in FEATURES):
        raise ValueError("Brakuje kryteriow w profilu studenta")

    if any(feature not in weights or weights[feature] <= 0 for feature in FEATURES):
        raise ValueError("Wagi musza byc dodatnie")

    results = []

    for area in rows:
        squared_distance = sum(
            weights[feature]
            * ((float(area[feature]) - float(preferences[feature])) / 100.0) ** 2
            for feature in FEATURES
        )

        distance = math.sqrt(squared_distance)

        results.append({
            "area_id": area["area_id"],
            "area_name": area["area_name"],
            "knn_distance": round(distance, 6),
        })

    return sorted(
        results,
        key=lambda row: (row["knn_distance"], row["area_id"])
    )[:k]


if __name__ == "__main__":
    import csv
    from pathlib import Path

    ROOT = Path(__file__).resolve().parents[1]
    observations_path = ROOT / "results" / "lab4" / "observations.csv"

    if not observations_path.exists():
        raise SystemExit(
            "Brak danych. Najpierw uruchom: "
            "py scripts/compare_methods.py"
        )

    with observations_path.open(
        encoding="utf-8", newline=""
    ) as file:
        areas = list(csv.DictReader(file))

    student_profile = {
        "university_score": 100,
        "shop_score": 100,
        "bus_stop_score": 100,
        "park_score": 100,
    }

    weights = {
        "university_score": 3.0,
        "shop_score": 2.0,
        "bus_stop_score": 2.0,
        "park_score": 2.0,
    }

    recommendations = knn_recommend(
        areas,
        student_profile,
        k=3,
        weights=weights,
    )

    print("=== KNN: REKOMENDOWANE OKOLICE RZESZOWA ===")
    print(f"Liczba analizowanych lokalizacji: {len(areas)}")

    for position, area in enumerate(recommendations, start=1):
        print(
            f"{position}. {area['area_name']} "
            f"(odleglosc KNN: {area['knn_distance']})"
        )