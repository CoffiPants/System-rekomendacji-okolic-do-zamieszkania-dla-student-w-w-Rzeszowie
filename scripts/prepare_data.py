"""Przygotowanie danych projektu. Python 3.10+, bez dodatkowych pakietów."""

import argparse
import json
import math
import sys
from pathlib import Path


def read_json(path):
    with path.open(encoding="utf-8-sig") as source:
        return json.load(source)


def text(value):
    return " ".join(str(value).split()) if value is not None else ""


def index_objects(document):
    if document.get("remark"):
        raise ValueError("Overpass zwrócił ostrzeżenie lub błąd: " + document["remark"])
    objects = document.get("elements")
    if not isinstance(objects, list) or not objects:
        raise ValueError("Brak niepustej listy elements w danych wejściowych.")
    result = {}
    for obj in objects:
        kind, number = obj.get("type"), obj.get("id")
        if kind not in ("node", "way", "relation") or type(number) is not int:
            raise ValueError("Nieprawidłowy typ lub identyfikator obiektu OSM.")
        key = f"{kind}/{number}"
        if key in result:
            raise ValueError("Powtórzony identyfikator OSM: " + key)
        result[key] = obj
    return result


def coordinates(obj):
    point = obj if obj["type"] == "node" else obj.get("center", {})
    lat, lon = point.get("lat"), point.get("lon")
    for value in (lat, lon):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"Brak lub nieprawidłowy typ współrzędnych: {obj['id']}")
        if not math.isfinite(value):
            raise ValueError("Współrzędne muszą być skończonymi liczbami.")
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("Współrzędne poza dopuszczalnym zakresem.")
    return lat, lon


def address(tags):
    street, number = text(tags.get("addr:street")), text(tags.get("addr:housenumber"))
    if not street or not number:
        return None
    city = text(tags.get("addr:city")) or "Rzeszów"
    return f"{street} {number}, {city}"


def prepare_services(document):
    objects = index_objects(document)
    labels = {"shop": "Sklep spożywczy", "bus_stop": "Przystanek", "park": "Park"}
    rows = []
    skipped = 0
    for key, obj in objects.items():
        tags = obj.get("tags", {})
        if tags.get("shop") in ("supermarket", "convenience"):
            category = "shop"
        elif obj["type"] == "node" and tags.get("highway") == "bus_stop":
            category = "bus_stop"
        elif tags.get("leisure") == "park":
            category = "park"
        else:
            skipped += 1
            continue
        lat, lon = coordinates(obj)
        source_name = tags.get("name")
        name = text(source_name)
        rows.append({
            "id": key,
            "category": category,
            "name": name or f"{labels[category]} ({key})",
            "name_missing": not bool(name),
            "source_name": source_name,
            "address": address(tags),
            "latitude": lat,
            "longitude": lon,
            "coordinate_type": "osm_node" if obj["type"] == "node" else "osm_bounding_box_center",
            "osm_url": f"https://www.openstreetmap.org/{key}",
        })
    if not rows:
        raise ValueError("Brak usług po przetworzeniu.")
    return sorted(rows, key=lambda row: row["id"]), len(objects), skipped


def prepare_universities(document, configuration):
    objects = index_objects(document)
    rules = configuration.get("locations")
    if not isinstance(rules, list) or not rules:
        raise ValueError("Brak reguł wyboru lokalizacji.")
    rows, used = [], set()
    for rule in rules:
        key = rule["osm_id"]
        if key in used:
            raise ValueError("Powtórzona reguła wyboru: " + key)
        used.add(key)
        if key not in objects:
            raise ValueError("Wybrany obiekt nie występuje w próbce: " + key)
        obj = objects[key]
        tags = obj.get("tags", {})
        overrides = rule.get("overrides", {})
        sources = rule.get("override_sources", {})
        if set(overrides) - {"name", "address"}:
            raise ValueError("Nieobsługiwane pole uzupełnienia: " + key)
        if any(not text(sources.get(field)) for field in overrides):
            raise ValueError("Uzupełnienie nie ma podanego źródła: " + key)
        name = text(overrides.get("name", tags.get("name")))
        location_address = text(overrides.get("address", address(tags)))
        if not name or not location_address:
            raise ValueError("Wybrana lokalizacja nie ma nazwy lub pełnego adresu: " + key)
        university = rule.get("university")
        if university not in {"UR", "PRz", "WSIiZ", "WSPiA"}:
            raise ValueError("Uczelnia poza zakresem projektu: " + key)
        if rule.get("location_type") not in {"building", "campus"}:
            raise ValueError("Nieprawidłowy typ miejsca zajęć: " + key)
        lat, lon = coordinates(obj)
        rows.append({
            "id": key,
            "university": university,
            "name": name,
            "address": location_address,
            "latitude": lat,
            "longitude": lon,
            "location_type": rule["location_type"],
            "coordinate_type": "osm_node" if obj["type"] == "node" else "osm_bounding_box_center",
            "osm_url": f"https://www.openstreetmap.org/{key}",
            "source_name": tags.get("name"),
            "source_address": {"street": tags.get("addr:street"), "housenumber": tags.get("addr:housenumber")},
            "supplement_sources": sources,
        })
    return sorted(rows, key=lambda row: row["id"]), len(objects)


def save_json(path, document):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1], help="Katalog repozytorium")
    args = parser.parse_args()
    root = args.root.resolve()
    service_source = read_json(root / "data/raw/sample.json")
    university_source = read_json(root / "data/raw/universities.json")
    selection = read_json(root / "config/university-selection.json")
    services, input_services, skipped = prepare_services(service_source)
    universities, input_universities = prepare_universities(university_source, selection)
    # Walidacja obu zbiorów kończy się przed zapisem plików wynikowych.
    common = {
        "attribution": "© OpenStreetMap contributors",
        "license": "ODbL-1.0",
        "license_url": "https://www.openstreetmap.org/copyright",
    }
    save_json(root / "data/processed/services.json", {**common, "services": services})
    save_json(root / "data/processed/universities.json", {**common, "locations": universities})
    print(f"Uslugi: {input_services} -> {len(services)}; poza kategoriami: {skipped}")
    print(f"Brak nazwy zrodlowej: {sum(row['name_missing'] for row in services)}")
    print(f"Obiekty uczelni: {input_universities} -> {len(universities)}")
    print("Zapisano data/processed/services.json i data/processed/universities.json")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"BLAD: {error}", file=sys.stderr)
        sys.exit(1)
