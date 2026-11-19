import csv
import statistics
import time

from pathlib import Path

from knn_recommender import knn_recommend


FEATURES = (
    "university_score",
    "shop_score",
    "bus_stop_score",
    "park_score",
)

WEIGHTS = {
    "university_score": 3.0,
    "shop_score": 2.0,
    "bus_stop_score": 2.0,
    "park_score": 2.0,
}

PREFERENCES = {feature: 100.0 for feature in FEATURES}

REPETITIONS = 1000


def load_areas():
    path = Path("results/lab4/observations.csv")

    with path.open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        return [
            {
                "area_id": row["area_id"],
                "area_name": row["area_name"],
                **{
                    feature: float(row[feature])
                    for feature in FEATURES
                },
            }
            for row in reader
        ]


def weighted_scoring(areas):
    results = []

    for area in areas:
        value = sum(
            area[feature] * WEIGHTS[feature]
            for feature in FEATURES
        ) / sum(WEIGHTS.values())

        results.append((area["area_id"], value))

    return sorted(results, key=lambda row: (-row[1], row[0]))[:3]


def measure(function, repetitions):
    times = []

    for _ in range(repetitions):
        start = time.perf_counter_ns()
        function()
        elapsed = time.perf_counter_ns() - start
        times.append(elapsed / 1_000_000)

    return statistics.median(times)


def main():
    areas = load_areas()

    weighted_time = measure(
        lambda: weighted_scoring(areas),
        REPETITIONS,
    )

    knn_time = measure(
        lambda: knn_recommend(
            areas,
            PREFERENCES,
            k=3,
            weights=WEIGHTS,
        ),
        REPETITIONS,
    )

    print("=== LAB 4: POROWNANIE CZASU ===")
    print(f"Liczba okolic: {len(areas)}")
    print(f"Liczba powtorzen: {REPETITIONS}")
    print(f"Weighted Scoring: {weighted_time:.6f} ms")
    print(f"KNN: {knn_time:.6f} ms")

    if weighted_time < knn_time:
        print("Szybsza metoda: Weighted Scoring")
    elif knn_time < weighted_time:
        print("Szybsza metoda: KNN")
    else:
        print("Metody maja podobny czas wykonania")


if __name__ == "__main__":
    main()