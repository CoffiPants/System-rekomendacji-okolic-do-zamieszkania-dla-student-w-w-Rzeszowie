"""Walidacja dokumentów JSON wczytywanych przez aplikację.

Moduł nie wczytuje plików i niczego nie poprawia. Sprawdza strukturę danych
przekazanych przez ``RecommendationEngine.from_files`` i zgłasza
``DataValidationError`` z listą naruszeń. Wyjątek dziedziczy po ``ValueError``,
dlatego aplikacja pokazuje go jako zwykły komunikat o błędzie danych.

Pełna kontrola jakości danych (format identyfikatora OSM, ``coordinate_type``,
``name_missing``) pozostaje w ``scripts/check_data.py``.
"""

from __future__ import annotations

import math


SERVICE_CATEGORIES = ("shop", "bus_stop", "park")
MAX_REPORTED_ERRORS = 5

# Pola tekstowe, bez których silnik lub interfejs nie zadziała poprawnie.
REQUIRED_TEXT_FIELDS = {
    "services": ("category",),
    "locations": ("university", "name", "address"),
    "areas": ("name", "district"),
}


class DataValidationError(ValueError):
    """Dane wejściowe aplikacji nie spełniają reguł walidacji."""

    def __init__(self, errors: list[str]):
        self.errors = list(errors)
        shown = self.errors[:MAX_REPORTED_ERRORS]
        message = "Nieprawidłowe dane: " + " ".join(shown)
        hidden = len(self.errors) - len(shown)
        if hidden > 0:
            message += f" (oraz {hidden} kolejnych naruszeń)"
        super().__init__(message)


def _is_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_coordinate(value: object, low: float, high: float) -> bool:
    return (type(value) in (int, float) and math.isfinite(value)
            and low <= value <= high)


def find_violations(document: object, key: str) -> list[str]:
    """Zwraca listę naruszeń dla jednego dokumentu; pusta lista oznacza brak błędów.

    ``key`` to nazwa listy rekordów: ``services``, ``locations`` albo ``areas``.
    """
    if key not in REQUIRED_TEXT_FIELDS:
        raise ValueError(f"Nieznany zbiór danych: {key}")
    if not isinstance(document, dict):
        return [f"Dokument {key} musi być obiektem JSON, a nie typem "
                f"{type(document).__name__}."]
    if key not in document:
        return [f"Dokument nie zawiera listy {key}."]
    records = document[key]
    if not isinstance(records, list):
        return [f"Pole {key} musi być listą."]
    if not records:
        return [f"Lista {key} jest pusta."]

    errors = []
    seen_ids = set()
    for index, record in enumerate(records):
        prefix = f"{key}[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{prefix}: rekord nie jest obiektem.")
            continue
        identifier = record.get("id")
        if not _is_text(identifier):
            errors.append(f"{prefix}: brak identyfikatora id.")
        else:
            prefix = f"{key}[{index}] (id {identifier})"
            if identifier in seen_ids:
                errors.append(f"{prefix}: powtórzony identyfikator.")
            seen_ids.add(identifier)
        if not _is_coordinate(record.get("latitude"), -90, 90):
            errors.append(f"{prefix}: nieprawidłowa lub brakująca latitude.")
        if not _is_coordinate(record.get("longitude"), -180, 180):
            errors.append(f"{prefix}: nieprawidłowa lub brakująca longitude.")
        for field in REQUIRED_TEXT_FIELDS[key]:
            if not _is_text(record.get(field)):
                errors.append(f"{prefix}: brak pola {field}.")
        if key == "services" and _is_text(record.get("category")) \
                and record["category"] not in SERVICE_CATEGORIES:
            errors.append(f"{prefix}: nieznana kategoria {record['category']}.")
    return errors


def validate_documents(services_document: object, locations_document: object,
                       areas_document: object) -> None:
    """Sprawdza trzy dokumenty aplikacji; przy naruszeniach zgłasza wyjątek."""
    errors = (find_violations(services_document, "services")
              + find_violations(locations_document, "locations")
              + find_violations(areas_document, "areas"))
    if errors:
        raise DataValidationError(errors)
