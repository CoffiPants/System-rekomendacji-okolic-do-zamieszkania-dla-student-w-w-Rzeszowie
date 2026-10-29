#!/usr/bin/env python3
"""Compare a university-only baseline with the project's weighted ranking."""

import argparse
import csv
import json
import math
from pathlib import Path


LIMITS = {"university": 3000.0, "shop": 1000.0, "bus_stop": 600.0, "park": 1500.0}
WEIGHTS = {"university": 3.0, "shop": 2.0, "bus_stop": 2.0, "park": 2.0}


def load_json(path):
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def distance_m(a_lat, a_lon, b_lat, b_lon):
    radius = 6_371_000
    lat1, lat2 = math.radians(a_lat), math.radians(b_lat)
    dlat = lat2 - lat1
    dlon = math.radians(b_lon - a_lon)
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(h))


def score(distance, limit):
    return 100.0 * max(0.0, 1.0 - distance / limit)


def nearest_distance(area, objects):
    return min(
        distance_m(area["latitude"], area["longitude"], item["latitude"], item["longitude"])
        for item in objects
    )


def rank(rows, field):
    return sorted(rows, key=lambda row: (-row[field], row["area_id"]))


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run(args):
    services = load_json(args.services)["services"]
    universities = load_json(args.universities)["locations"]
    areas = load_json(args.areas)["areas"]
    selected = [item for item in universities if item["id"] == args.university_id]
    if not selected:
        raise SystemExit(f"Nie znaleziono lokalizacji uczelni: {args.university_id}")
    university = selected[0]
    limits = dict(LIMITS)
    limits["shop"] = args.shop_limit
    grouped = {category: [item for item in services if item["category"] == category]
               for category in ("shop", "bus_stop", "park")}
    rows = []
    for area in areas:
        distances = {
            "university": distance_m(area["latitude"], area["longitude"],
                                     university["latitude"], university["longitude"]),
            **{category: nearest_distance(area, items) for category, items in grouped.items()},
        }
        scores = {category: score(distance, limits[category]) for category, distance in distances.items()}
        weighted = sum(scores[key] * WEIGHTS[key] for key in scores) / sum(WEIGHTS.values())
        rows.append({
            "area_id": area["id"],
            "area_name": area["name"],
            "district": area["district"],
            "university_distance_m": round(distances["university"], 2),
            "shop_distance_m": round(distances["shop"], 2),
            "bus_stop_distance_m": round(distances["bus_stop"], 2),
            "park_distance_m": round(distances["park"], 2),
            "university_score": round(scores["university"], 4),
            "shop_score": round(scores["shop"], 4),
            "bus_stop_score": round(scores["bus_stop"], 4),
            "park_score": round(scores["park"], 4),
            "baseline_score": round(scores["university"], 4),
            "proposed_score": round(weighted, 4),
        })

    baseline = rank(rows, "baseline_score")
    proposed = rank(rows, "proposed_score")
    baseline_top = {row["area_id"] for row in baseline[:3]}
    proposed_top = {row["area_id"] for row in proposed[:3]}
    baseline_utility = sum(row["proposed_score"] for row in baseline[:3]) / 3
    proposed_utility = sum(row["proposed_score"] for row in proposed[:3]) / 3
    comparison = [{
        "metric": "mean_full_utility_top3",
        "baseline": round(baseline_utility, 4),
        "proposed": round(proposed_utility, 4),
        "unit": "points (0-100)",
        "direction": "higher_is_better",
    }, {
        "metric": "top3_overlap",
        "baseline": len(baseline_top & proposed_top),
        "proposed": 3,
        "unit": "areas",
        "direction": "descriptive",
    }]
    output = Path(args.output)
    observation_fields = list(rows[0])
    write_csv(output / "observations.csv", rows, observation_fields)
    write_csv(output / "comparison.csv", comparison,
              ["metric", "baseline", "proposed", "unit", "direction"])
    write_csv(output / "ranking_baseline.csv",
              [{"rank": i, "area_id": row["area_id"], "area_name": row["area_name"],
                "score": row["baseline_score"]} for i, row in enumerate(baseline, 1)],
              ["rank", "area_id", "area_name", "score"])
    write_csv(output / "ranking_proposed.csv",
              [{"rank": i, "area_id": row["area_id"], "area_name": row["area_name"],
                "score": row["proposed_score"]} for i, row in enumerate(proposed, 1)],
              ["rank", "area_id", "area_name", "score"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--services", type=Path, default=Path("data/processed/services.json"))
    parser.add_argument("--universities", type=Path, default=Path("data/processed/universities.json"))
    parser.add_argument("--areas", type=Path, default=Path("config/residential-areas.json"))
    parser.add_argument("--output", type=Path, default=Path("results/lab4"))
    parser.add_argument("--university-id", default="way/197227711")
    parser.add_argument("--shop-limit", type=float, default=1000.0)
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
