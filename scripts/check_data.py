"""Niezależna kontrola danych wynikowych. Python 3.10+, bez dodatkowych pakietów."""

import argparse
import copy
import json
import math
import sys
from pathlib import Path


def load(path):
    with path.open(encoding="utf-8-sig") as source:
        return json.load(source)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def valid_coordinate(value, low, high):
    return type(value) in (int, float) and math.isfinite(value) and low <= value <= high


def validate(document, kind):
    """Zwraca naruszenia bez poprawiania lub usuwania rekordów."""
    errors = []
    key = "services" if kind == "services" else "locations"
    if not isinstance(document, dict):
        return ["Dokument musi byc obiektem JSON."]
    rows = document.get(key)
    if not isinstance(rows, list) or not rows:
        return [f"Brak niepustej listy {key}."]
    seen = set()
    for index, row in enumerate(rows):
        prefix = f"{key}[{index}]"
        if not isinstance(row, dict):
            errors.append(prefix + ": rekord nie jest obiektem.")
            continue
        identifier = row.get("id")
        if not nonempty(identifier):
            errors.append(prefix + ": pusty lub nieprawidlowy id.")
        else:
            if identifier in seen:
                errors.append(prefix + ": powtorzony id " + identifier)
            seen.add(identifier)
            parts = identifier.split("/")
            if len(parts) != 2 or parts[0] not in {"node", "way", "relation"} or not parts[1].isdigit():
                errors.append(prefix + ": nieprawidlowy format id OSM.")
        if not nonempty(row.get("name")):
            errors.append(prefix + ": brak nazwy do wyswietlenia.")
        if not valid_coordinate(row.get("latitude"), -90, 90):
            errors.append(prefix + ": nieprawidlowa latitude.")
        if not valid_coordinate(row.get("longitude"), -180, 180):
            errors.append(prefix + ": nieprawidlowa longitude.")
        if row.get("coordinate_type") not in {"osm_node", "osm_bounding_box_center"}:
            errors.append(prefix + ": nieprawidlowy coordinate_type.")
        if kind == "services":
            if row.get("category") not in {"shop", "bus_stop", "park"}:
                errors.append(prefix + ": nieprawidlowa kategoria.")
            if type(row.get("name_missing")) is not bool:
                errors.append(prefix + ": name_missing musi byc wartoscia bool.")
            else:
                original_missing = not nonempty(row.get("source_name"))
                if row["name_missing"] != original_missing:
                    errors.append(prefix + ": name_missing nie odpowiada source_name.")
        else:
            if not nonempty(row.get("address")):
                errors.append(prefix + ": brak adresu miejsca zajec.")
            if row.get("university") not in {"UR", "PRz", "WSIiZ", "WSPiA"}:
                errors.append(prefix + ": uczelnia poza zakresem projektu.")
            if row.get("location_type") not in {"building", "campus"}:
                errors.append(prefix + ": nieprawidlowy location_type.")
    return errors


def check_outputs(root):
    report = {"datasets": {}, "success": True}
    documents = {}
    for kind, filename, key in [("services", "services.json", "services"), ("universities", "universities.json", "locations")]:
        doc = load(root / "data/processed" / filename)
        documents[kind] = doc
        errors = validate(doc, kind)
        rows = doc.get(key, []) if isinstance(doc, dict) else []
        count = len(rows) if isinstance(rows, list) else 0
        report["datasets"][kind] = {"records": count, "violations": errors, "success": not errors}
        report["success"] = report["success"] and not errors
    return documents, report


def test_invalid_copies(root, documents):
    """Błędy tworzymy wyłącznie w kopiach w data/test/, nigdy w processed/raw."""
    results = []
    examples = [
        ("duplicate_service.json", "services", "powtorzony id", "Duplikat ID powinien zostac odrzucony."),
        ("invalid_coordinate.json", "services", "nieprawidlowa latitude", "Latitude 200 powinna zostac odrzucona."),
        ("missing_university_address.json", "universities", "brak adresu", "Pusty adres miejsca zajec powinien zostac odrzucony."),
    ]
    for filename, kind, expected_fragment, description in examples:
        broken = copy.deepcopy(documents[kind])
        if filename == "duplicate_service.json":
            broken["services"].append(copy.deepcopy(broken["services"][0]))
        elif filename == "invalid_coordinate.json":
            broken["services"][0]["latitude"] = 200
        else:
            broken["locations"][0]["address"] = ""
        path = root / "data/test" / filename
        write(path, broken)
        # Sprawdzamy faktycznie zapisany i ponownie otwarty plik.
        errors = validate(load(path), kind)
        detected = any(expected_fragment in error for error in errors)
        results.append({"file": "data/test/" + filename, "expected": description, "violations": errors, "success": detected})
    return {"cases": results, "success": all(result["success"] for result in results)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--test-invalid", action="store_true", help="Utworz bledne kopie i sprawdz wykrywanie bledow")
    args = parser.parse_args()
    root = args.root.resolve()
    documents, report = check_outputs(root)
    write(root / "data/test/quality-report.json", report)
    for kind, result in report["datasets"].items():
        print(f"{kind}: {result['records']} rekordow, {len(result['violations'])} naruszen")
    if not report["success"]:
        print("BLAD: wynik nie spelnia regul. Szczegoly: data/test/quality-report.json")
        return 1
    if args.test_invalid:
        tests = test_invalid_copies(root, documents)
        write(root / "data/test/invalid-tests-report.json", tests)
        print(f"Proby na blednych kopiach: {sum(case['success'] for case in tests['cases'])}/{len(tests['cases'])}")
        if not tests["success"]:
            return 1
    print("OK: wszystkie uruchomione kontrole przeszly.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"BLAD: {error}", file=sys.stderr)
        sys.exit(1)
