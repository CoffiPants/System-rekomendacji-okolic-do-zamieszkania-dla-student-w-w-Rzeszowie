"""Audyt kompletności i spójności danych projektu — Lab 3.

Python 3.10+, bez dodatkowych pakietów.
Skrypt nie modyfikuje danych w data/raw/ ani data/processed/.
"""

import json
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
TEST = ROOT / "data" / "test"

SERVICE_FIELDS = {
    "id",
    "category",
    "name",
    "name_missing",
    "source_name",
    "address",
    "latitude",
    "longitude",
    "coordinate_type",
    "osm_url",
}

UNIVERSITY_FIELDS = {
    "id",
    "university",
    "name",
    "address",
    "latitude",
    "longitude",
    "location_type",
    "coordinate_type",
    "osm_url",
    "source_name",
    "source_address",
    "supplement_sources",
}

CATEGORIES = {"shop", "bus_stop", "park"}
UNIVERSITIES = {"UR", "PRz", "WSIiZ", "WSPiA"}
LOCATION_TYPES = {"building", "campus"}

OPTIONAL_FIELDS = {
    "services": {"address", "source_name"},
    "universities": {"source_name"},
}


def load_data(filename, key):
    """Wczytuje dokument JSON i sprawdza podstawową strukturę."""

    path = PROCESSED / filename

    with path.open(encoding="utf-8-sig") as file:
        document = json.load(file)

    if not isinstance(document, dict):
        raise ValueError(f"{filename}: dokument nie jest obiektem JSON.")

    records = document.get(key)

    if not isinstance(records, list):
        raise ValueError(f"{filename}: brak listy {key}.")

    return records


def is_empty(value):
    """Sprawdza brak wartości, nie traktując False ani 0 jako braku."""

    return (
        value is None
        or isinstance(value, str) and not value.strip()
    )


def valid_coordinate(value, minimum, maximum):
    """Sprawdza typ i dopuszczalny zakres współrzędnych."""

    return (
        type(value) in (int, float)
        and math.isfinite(value)
        and minimum <= value <= maximum
    )


def add_issue(issues, identifier, field, description, severity):
    """Dodaje problem do raportu."""

    issues.append({
        "id": identifier,
        "field": field,
        "description": description,
        "severity": severity,
    })


def audit(records, dataset):
    """Wykonuje szczegółowy audyt wszystkich rekordów."""

    expected_fields = (
        SERVICE_FIELDS
        if dataset == "services"
        else UNIVERSITY_FIELDS
    )

    issues = []
    missing_values = Counter()
    categories = Counter()
    universities = Counter()
    location_types = Counter()

    coordinates = defaultdict(list)
    identifiers = defaultdict(list)

    for index, record in enumerate(records):

        if not isinstance(record, dict):
            add_issue(
                issues,
                f"record_{index}",
                "record",
                "Rekord nie jest obiektem JSON.",
                "ERROR",
            )
            continue

        identifier = record.get("id", f"record_{index}")

        if not isinstance(identifier, str):
            identifier = str(identifier)

        identifiers[identifier].append(index)

        # 1. Sprawdzenie struktury pól

        actual_fields = set(record.keys())

        for field in sorted(expected_fields - actual_fields):
            add_issue(
                issues,
                identifier,
                field,
                "Brak wymaganego pola w strukturze rekordu.",
                "ERROR",
            )

        for field in sorted(actual_fields - expected_fields):
            add_issue(
                issues,
                identifier,
                field,
                "Dodatkowe pole poza przyjętym schematem.",
                "WARNING",
            )

        # 2. Brakujące wartości i spacje

        for field in expected_fields:

            if field not in record:
                missing_values[field] += 1
                continue

            value = record[field]

            if is_empty(value):
                missing_values[field] += 1

                optional = field in OPTIONAL_FIELDS[dataset]

                if not optional:
                    add_issue(
                        issues,
                        identifier,
                        field,
                        "Pusta wartość w polu wymaganym.",
                        "ERROR",
                    )

            if isinstance(value, str):

                if value != value.strip():
                    add_issue(
                        issues,
                        identifier,
                        field,
                        "Spacje na początku lub końcu tekstu.",
                        "WARNING",
                    )

                if "  " in value:
                    add_issue(
                        issues,
                        identifier,
                        field,
                        "Wielokrotne spacje w tekście.",
                        "WARNING",
                    )

        # 3. Identyfikatory OSM

        parts = identifier.split("/")

        if (
            len(parts) != 2
            or parts[0] not in {"node", "way", "relation"}
            or not parts[1].isdigit()
        ):
            add_issue(
                issues,
                identifier,
                "id",
                "Nieprawidłowy format identyfikatora OSM.",
                "ERROR",
            )

        # 4. Współrzędne

        latitude = record.get("latitude")
        longitude = record.get("longitude")

        lat_ok = valid_coordinate(latitude, -90, 90)
        lon_ok = valid_coordinate(longitude, -180, 180)

        if not lat_ok:
            add_issue(
                issues,
                identifier,
                "latitude",
                "Nieprawidłowa szerokość geograficzna.",
                "ERROR",
            )

        if not lon_ok:
            add_issue(
                issues,
                identifier,
                "longitude",
                "Nieprawidłowa długość geograficzna.",
                "ERROR",
            )

        if lat_ok and lon_ok:
            coordinates[(latitude, longitude)].append(identifier)

        # 5. Typ współrzędnych

        coordinate_type = record.get("coordinate_type")

        if coordinate_type not in {
            "osm_node",
            "osm_bounding_box_center",
        }:
            add_issue(
                issues,
                identifier,
                "coordinate_type",
                "Nieprawidłowy typ współrzędnych.",
                "ERROR",
            )

        if len(parts) == 2:

            expected_type = (
                "osm_node"
                if parts[0] == "node"
                else "osm_bounding_box_center"
            )

            if (
                parts[0] in {"node", "way", "relation"}
                and coordinate_type != expected_type
            ):
                add_issue(
                    issues,
                    identifier,
                    "coordinate_type",
                    "Typ współrzędnych nie odpowiada typowi OSM.",
                    "ERROR",
                )

        # 6. Adres URL OSM

        expected_url = (
            f"https://www.openstreetmap.org/{identifier}"
        )

        if record.get("osm_url") != expected_url:
            add_issue(
                issues,
                identifier,
                "osm_url",
                "Adres OSM nie odpowiada identyfikatorowi.",
                "ERROR",
            )

        # 7. Kontrola usług

        if dataset == "services":

            category = record.get("category")

            if category not in CATEGORIES:
                add_issue(
                    issues,
                    identifier,
                    "category",
                    "Kategoria poza zakresem projektu.",
                    "ERROR",
                )
            else:
                categories[category] += 1

            name_missing = record.get("name_missing")
            source_name = record.get("source_name")

            if type(name_missing) is not bool:
                add_issue(
                    issues,
                    identifier,
                    "name_missing",
                    "Pole musi mieć wartość true lub false.",
                    "ERROR",
                )

            elif name_missing != is_empty(source_name):
                add_issue(
                    issues,
                    identifier,
                    "name_missing",
                    "Niezgodność z nazwą źródłową.",
                    "ERROR",
                )

            if is_empty(record.get("address")):
                add_issue(
                    issues,
                    identifier,
                    "address",
                    "Brak adresu; sprawdzić, czy jest potrzebny.",
                    "INFO",
                )

            if name_missing is True:
                add_issue(
                    issues,
                    identifier,
                    "name",
                    "Nazwa zastępcza; możliwa weryfikacja ręczna.",
                    "INFO",
                )

        # 8. Kontrola uczelni

        else:

            university = record.get("university")

            if university not in UNIVERSITIES:
                add_issue(
                    issues,
                    identifier,
                    "university",
                    "Uczelnia poza zakresem projektu.",
                    "ERROR",
                )
            else:
                universities[university] += 1

            location_type = record.get("location_type")

            if location_type not in LOCATION_TYPES:
                add_issue(
                    issues,
                    identifier,
                    "location_type",
                    "Nieprawidłowy typ lokalizacji.",
                    "ERROR",
                )
            else:
                location_types[location_type] += 1

            if not isinstance(record.get("source_address"), dict):
                add_issue(
                    issues,
                    identifier,
                    "source_address",
                    "Nieprawidłowa struktura adresu źródłowego.",
                    "ERROR",
                )

            if not isinstance(record.get("supplement_sources"), dict):
                add_issue(
                    issues,
                    identifier,
                    "supplement_sources",
                    "Nieprawidłowa struktura źródeł uzupełnień.",
                    "ERROR",
                )

    # 9. Powtórzone identyfikatory

    for identifier, indexes in identifiers.items():

        if len(indexes) > 1:
            add_issue(
                issues,
                identifier,
                "id",
                f"Powtórzony identyfikator: {len(indexes)} rekordy.",
                "ERROR",
            )

    # 10. Powtórzone współrzędne

    duplicate_coordinates = []

    for position, ids in coordinates.items():

        if len(ids) > 1:

            duplicate_coordinates.append({
                "latitude": position[0],
                "longitude": position[1],
                "ids": ids,
            })

            add_issue(
                issues,
                ", ".join(ids),
                "coordinates",
                "Kilka obiektów ma identyczne współrzędne.",
                "WARNING",
            )

    # 11. Podsumowanie

    severity_counts = Counter(
        issue["severity"] for issue in issues
    )

    return {
        "dataset": dataset,
        "records": len(records),
        "expected_fields": sorted(expected_fields),
        "missing_values": dict(sorted(missing_values.items())),
        "categories": dict(sorted(categories.items())),
        "universities": dict(sorted(universities.items())),
        "location_types": dict(sorted(location_types.items())),
        "duplicate_coordinates": duplicate_coordinates,
        "errors": severity_counts["ERROR"],
        "warnings": severity_counts["WARNING"],
        "information": severity_counts["INFO"],
        "issues": issues,
    }


def save_json(path, document):

    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps(
            document,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        ) + "\n",
        encoding="utf-8",
    )


def main():

    services = load_data("services.json", "services")
    universities = load_data("universities.json", "locations")

    report = {
        "services": audit(services, "services"),
        "universities": audit(universities, "universities"),
    }

    report["summary"] = {
        "total_records": len(services) + len(universities),
        "total_errors": sum(
            report[name]["errors"]
            for name in ("services", "universities")
        ),
        "total_warnings": sum(
            report[name]["warnings"]
            for name in ("services", "universities")
        ),
        "total_information": sum(
            report[name]["information"]
            for name in ("services", "universities")
        ),
    }

    report["summary"]["success"] = (
        report["summary"]["total_errors"] == 0
    )

    output = TEST / "audit-report.json"

    save_json(output, report)

    for name in ("services", "universities"):

        result = report[name]

        print(f"\n=== {name.upper()} ===")
        print("Rekordy:", result["records"])
        print("Brakujace wartosci:", result["missing_values"])
        print("Bledy:", result["errors"])
        print("Ostrzezenia:", result["warnings"])
        print("Informacje:", result["information"])
        print(
            "Powtarzajace sie wspolrzedne:",
            len(result["duplicate_coordinates"]),
        )

        if name == "services":
            print("Kategorie:", result["categories"])
        else:
            print("Uczelnie:", result["universities"])
            print("Typy lokalizacji:", result["location_types"])

    print("\n=== PODSUMOWANIE ===")
    print("Wszystkie rekordy:", report["summary"]["total_records"])
    print("Bledy:", report["summary"]["total_errors"])
    print("Ostrzezenia:", report["summary"]["total_warnings"])
    print("Informacje:", report["summary"]["total_information"])

    if report["summary"]["success"]:
        print("WYNIK: PASS - brak bledow krytycznych.")
    else:
        print("WYNIK: FAIL - wykryto bledy wymagajace poprawy.")

    print("\nRaport zapisano: data/test/audit-report.json")

    return 0 if report["summary"]["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())