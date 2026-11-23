#!/usr/bin/env python3
"""Mierzy czas wygenerowania rankingu dla danych projektu."""

import argparse
import statistics
import time
from pathlib import Path

from recommendation_engine import RecommendationEngine


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repetitions", type=int, default=100)
    parser.add_argument("--university-id", default="way/197227711")
    parser.add_argument("--max-walk-minutes", type=float, default=30.0)
    args = parser.parse_args()
    if args.repetitions <= 0:
        raise SystemExit("--repetitions musi być dodatnie.")
    root = Path(__file__).resolve().parents[1]
    engine = RecommendationEngine.from_files(
        root / "data/processed/services.json",
        root / "data/processed/universities.json",
        root / "config/residential-areas.json",
    )
    measurements = []
    for _ in range(args.repetitions):
        started = time.perf_counter_ns()
        ranking = engine.recommend(args.university_id, max_walk_minutes=args.max_walk_minutes)
        measurements.append((time.perf_counter_ns() - started) / 1_000_000)
    print(f"TOP 3: {', '.join(item['area_name'] for item in ranking)}")
    print(f"Powtórzenia: {args.repetitions}")
    print(f"Mediana: {statistics.median(measurements):.3f} ms")
    print(f"Minimum: {min(measurements):.3f} ms")
    print(f"Maksimum: {max(measurements):.3f} ms")


if __name__ == "__main__":
    main()
