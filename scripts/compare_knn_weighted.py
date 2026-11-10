"""Lab 4: porownanie Weighted Scoring i KNN na danych Rzeszowa."""

import csv
import json
import math
from pathlib import Path

from knn_recommender import FEATURES, knn_recommend

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "results/lab4/observations.csv"
OUTPUT = ROOT / "results/lab4/knn"

WEIGHTS = {
    "university_score": 3.0,
    "shop_score": 2.0,
    "bus_stop_score": 2.0,
    "park_score": 2.0,
}

PROFILES = {
    "balanced": {
        "university_score": 100,
        "shop_score": 100,
        "bus_stop_score": 100,
        "park_score": 100,
    },
    "university_priority": {
        "university_score": 100,
        "shop_score": 50,
        "bus_stop_score": 50,
        "park_score": 50,
    },
    "services_priority": {
        "university_score": 50,
        "shop_score": 100,
        "bus_stop_score": 100,
        "park_score": 100,
    },
}


def load_areas():
    with INPUT.open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def weighted_ranking(areas, preferences):
    results = []

    for area in areas:
        score = 0.0

        for feature in FEATURES:
            actual = float(area[feature])
            desired = float(preferences[feature])

            # Ocena zgodnosci z profilem studenta.
            compatibility = 100.0 - abs(actual - desired)

            score += WEIGHTS[feature] * compatibility

        score /= sum(WEIGHTS.values())

        results.append({
            "area_id": area["area_id"],
            "area_name": area["area_name"],
            "weighted_score": round(score, 6),
        })

    return sorted(
        results,
        key=lambda row: (-row["weighted_score"], row["area_id"])
    )


def save_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    areas = load_areas()

    if not areas:
        raise ValueError("Brak danych do eksperymentu.")

    summary = []
    all_rankings = []

    print("=== LAB 4: WEIGHTED SCORING VS KNN ===")
    print(f"Liczba analizowanych okolic: {len(areas)}")

    for profile_name, preferences in PROFILES.items():
        weighted = weighted_ranking(areas, preferences)

        knn = knn_recommend(
            areas,
            preferences,
            k=len(areas),
            weights=WEIGHTS,
        )

        weighted_top3 = {row["area_id"] for row in weighted[:3]}
        knn_top3 = {row["area_id"] for row in knn[:3]}

        overlap = len(weighted_top3 & knn_top3)

        print(f"\nPROFIL: {profile_name}")
        print("Weighted Scoring:")

        for position, row in enumerate(weighted[:3], 1):
            print(
                f"  {position}. {row['area_name']}: "
                f"{row['weighted_score']:.4f}"
            )

        print("KNN:")

        for position, row in enumerate(knn[:3], 1):
            print(
                f"  {position}. {row['area_name']}: "
                f"{row['knn_distance']:.6f}"
            )

        print(f"Wspolne okolice w TOP 3: {overlap}/3")

        summary.append({
            "profile": profile_name,
            "areas": len(areas),
            "top3_overlap": overlap,
            "weighted_first": weighted[0]["area_name"],
            "knn_first": knn[0]["area_name"],
        })

        for method, ranking in [
            ("weighted", weighted),
            ("knn", knn),
        ]:
            for position, row in enumerate(ranking, 1):
                value = (
                    row["weighted_score"]
                    if method == "weighted"
                    else row["knn_distance"]
                )

                all_rankings.append({
                    "profile": profile_name,
                    "method": method,
                    "rank": position,
                    "area_id": row["area_id"],
                    "area_name": row["area_name"],
                    "value": value,
                })

    save_csv(
        OUTPUT / "comparison.csv",
        summary,
        [
            "profile",
            "areas",
            "top3_overlap",
            "weighted_first",
            "knn_first",
        ],
    )

    save_csv(
        OUTPUT / "rankings.csv",
        all_rankings,
        [
            "profile",
            "method",
            "rank",
            "area_id",
            "area_name",
            "value",
        ],
    )

    print("\nZapisano wyniki w results/lab4/knn/")


if __name__ == "__main__":
    main()