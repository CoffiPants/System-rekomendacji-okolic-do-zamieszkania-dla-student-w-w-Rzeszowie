# Testy — Laboratorium 7

Autorka: Valentyna Boksha (dane i testowanie). Stan na 23.11.2026.

Statusy: **PASS** — sprawdzono, wynik zgodny z oczekiwanym; **FAIL** — sprawdzono, wynik niezgodny; **NOT RUN** — nie sprawdzano (z przyczyną).

## 1. Zakres oraz wersja kodu i danych

| Element | Wartość |
|---|---|
| Gałąź | `main`, commit `653393e` (po połączeniu PR #14–#20) |
| Commit kodu | Silnik i walidacja (`scripts/`) bez zmian od commita `0df4f8b`. `app.py` zmieniony w PR #20: eksport CSV i komunikat przy mniej niż trzech wynikach |
| Dane | `data/processed/services.json` (500), `data/processed/universities.json` (28), `config/residential-areas.json` (25) — bez zmian od commita `1d9e312` |
| Środowisko | Windows 11, Python 3.12.6, streamlit 1.67.0, folium 1.0.0, streamlit-folium 0.27.4 |

Zakres: wczytywanie i walidacja plików danych, parametry żądania, przebieg dane → silnik → odpowiedź, ręczne sprawdzenie interfejsu.

Eksport rankingu i instrukcja użytkownika zostały dodane w PR #20; ich sprawdzenie opisują punkty 2.2 i 6.

## 2. Plan przypadków testowych i dziennik uruchomień

### 2.1. Testy automatyczne

Polecenie (w katalogu głównym repozytorium):

```shell
python -m unittest discover -s tests -v
```

| ID | Rodzaj | Przypadek | Oczekiwany wynik | Podstawa oczekiwania | Test |
|---|---|---|---|---|---|
| T01 | poprawny | Pliki projektu | Wczytane 500 / 28 / 25 rekordów | `docs/data.md` | `test_project_files_are_loaded` |
| T02 | błędny | Brak pliku | Błąd `OSError`, który aplikacja zamienia na komunikat | architektura 4.3 | `test_missing_file_is_reported` |
| T03 | błędny | Uszkodzony JSON | Błąd `ValueError` | architektura 4.3 | `test_damaged_json_is_reported` |
| T04 | błędny | `[]` zamiast obiektu JSON | Odrzucenie z komunikatem „musi być obiektem JSON” | struktura plików, architektura 5.2 | `test_top_level_list_is_rejected` |
| T05 | pusty | Pusta lista rekordów | Odrzucenie „Lista … jest pusta” | silnik wymaga niepustych zbiorów | `test_empty_record_list_is_rejected` |
| T06 | błędny | Powtórzony `id` | Odrzucenie „powtórzony identyfikator” | `id` jest kluczem (architektura 5.2) | `test_duplicate_id_is_rejected` |
| T07 | błędny | Współrzędne 200, −91, 181, tekst, brak, NaN | Odrzucenie | zakres WGS84 | `test_invalid_coordinates_are_rejected`, `test_missing_coordinate_is_rejected`, `test_nan_coordinate_is_rejected` |
| T08 | graniczny | Współrzędne 90 i −180 | Przyjęte | zakres WGS84 włącznie | `test_boundary_coordinates_are_accepted` |
| T09 | błędny | Nieznana lub brakująca kategoria; kategoria bez usług | Odrzucenie | kategorie `shop`, `bus_stop`, `park` | `test_unknown_category_is_rejected`, `test_missing_category_is_rejected`, `test_category_without_any_service_is_rejected` |
| T10 | błędny | Brak `university`, `name`, `address` miejsca zajęć; brak `name`, `district` obszaru | Odrzucenie „brak pola …” | pola używane przez `app.py` i odpowiedź silnika | `test_location_fields_used_by_interface_are_required`, `test_area_fields_used_in_results_are_required` |
| T11 | błędny | Nieznane `location_id`, zły typ | `VALIDATION_ERROR` | architektura 4.3 | `test_unknown_location_is_rejected`, `test_invalid_location_type_is_rejected` |
| T12 | graniczny | Wagi 1 i 3 | `SUCCESS` | wagi 1–3 | `test_boundary_weights_are_accepted` |
| T13 | błędny | Wagi 0, 4, −1, 2.0, tekst, NaN, inf, niepełny zestaw | `VALIDATION_ERROR` | wagi całkowite 1–3 | `test_weights_outside_range_are_rejected`, `test_invalid_weight_type_is_rejected`, `test_incomplete_or_extended_weights_are_rejected` |
| T14 | poprawny / błędny | Limit 15, 30, 45, brak; inne wartości | Dozwolone: `SUCCESS` lub `NO_MATCHES`; pozostałe: `VALIDATION_ERROR` | architektura 4.1 | `test_allowed_time_limits_are_accepted`, `test_other_time_limits_are_rejected` |
| T15 | integracyjny | 28 miejsc zajęć × 4 limity na danych projektu | Do 3 wyników, malejąco według oceny, remis według `area_id`, czas ≤ limit, ocena 0–100, promień 500 m, niepuste uzasadnienie i zastrzeżenie | kryteria odbioru UC-01 | `test_every_location_and_limit_gives_a_consistent_response` |
| T16 | integracyjny | To samo żądanie dwa razy | Identyczna odpowiedź | determinizm rankingu | `test_same_request_gives_same_response` |
| T17 | integracyjny | Czas a odległość | czas = odległość / 75 m/min | prędkość 4,5 km/h | `test_walk_time_matches_distance_at_4_5_kmh` |
| T18 | poprawny | R2: jeden obszar o znanych odległościach (1500 / 250 / 300 / 1200 m), siedem ustawień wag | Oceny kryteriów 50 / 75 / 50 / 20; ocena końcowa równa obliczeniu ręcznemu, np. wagi 1/1/1/1 → 48,75, sklep 3 → 57,50, park 3 → 39,17 | wzór punktacji z `docs/problem.md`; obliczenia zapisane w teście | `tests/test_weight_scoring.py`: `test_distances_and_criterion_scores`, `test_final_score_for_each_weight_setting`, `test_higher_weight_moves_score_towards_that_criterion` |
| T19 | graniczny | Usługa dalej niż limit punktacji (park 2000 m) | Ocena kryterium 0, obszar pozostaje w rankingu (43,75) | limit punktacji nie wyklucza obszaru | `test_service_beyond_scoring_limit_gives_zero_but_keeps_area` |
| T20 | poprawny | R2 i R4: dwa obszary, zmiana wagi zmienia kolejność | Równe wagi: remis 50 / 50, pierwszy `a` (według ID); uczelnia 3 → `a` 60, `b` 40; sklep 3 → `b` 60, `a` 40 | wzór punktacji, kryterium odbioru 3 UC-01 | `test_equal_weights_give_a_tie_resolved_by_area_id`, `test_university_weight_puts_area_near_university_first`, `test_shop_weight_puts_area_near_shop_first` |

Dziennik uruchomień:

| Data | Wersja | Kto uruchomił | Wynik |
|---|---|---|---|
| 23.11.2026 | `1d9e312` + nowe testy, bez zmian w silniku | asystent AI, lokalnie | 44 testy: 29 niepowodzeń, 3 błędy. Część niepowodzeń wynika tylko z innej treści komunikatu; faktycznie niewykrywane były: powtórzone ID, `[]` zamiast obiektu (`AttributeError`), nieznana kategoria, brak `university`/`address`, waga NaN/inf w `recommend()`. |
| 23.11.2026 | `0df4f8b` | Valentyna Boksha, lokalnie | **44/44 PASS** (`Ran 44 tests in 4.564s`, `OK`) |
| 23.11.2026 | `27c0438` + `tests/test_weight_scoring.py` | Valentyna Boksha, lokalnie (polecenie wpisał asystent AI) | **51/51 PASS** (`Ran 51 tests in 4.856s`, `OK`) |
| 23.11.2026 | `main` `d3aa845` (bez `test_weight_scoring.py`) | asystent AI, lokalnie | 44/44 PASS; `check_data.py --test-invalid`: 0 naruszeń, 3/3; `test_knn.py`: OK; Streamlit AppTest: brak wyjątków, 3 karty |
| 23.11.2026 | `main` `d3aa845` + `tests/test_weight_scoring.py` (commit `de8b08a`) | Valentyna Boksha, lokalnie (polecenie wpisał asystent AI) | **51/51 PASS** (`Ran 51 tests in 2.348s`, `OK`) |
| 23.11.2026 | `main` `e6db774` | Valentyna Boksha, lokalnie (polecenie wpisał asystent AI) | **51/51 PASS** (`Ran 51 tests in 2.380s`, `OK`) |
| 23.11.2026 | `main` `e6db774` | asystent AI, lokalnie | `check_data.py --test-invalid`: 0 naruszeń, 3/3; `verify_repeatability.py`: PASS; `audit_data.py`: PASS; `test_knn.py`: OK; Streamlit AppTest: brak wyjątków, 3 karty |

| 23.11.2026 | `main` `2539038` (tag `lab8-demo`) | Valentyna Boksha, lokalnie (polecenie wpisał asystent AI) | **51/51 PASS** (`Ran 51 tests in 2.437s`, `OK`) |
| 23.11.2026 | `main` `2539038` (tag `lab8-demo`) | asystent AI, lokalnie | `check_data.py --test-invalid`: 0 naruszeń, 3/3; `verify_repeatability.py`: PASS; `audit_data.py`: PASS; `test_knn.py`: OK; Streamlit AppTest: scenariusz 1 — 3 karty, scenariusz 2 (WSIiZ, 15 min) — komunikat o braku okolic, brak wyjątków |
| 23.11.2026 | `main` `653393e` | Valentyna Boksha, lokalnie (polecenie wpisał asystent AI) | **51/51 PASS** (`Ran 51 tests in 2.362s`, `OK`) |
| 23.11.2026 | `main` `653393e` | asystent AI, lokalnie | `check_data.py --test-invalid`: 0 naruszeń, 3/3; `test_knn.py`: OK; Streamlit AppTest: 3 karty i przycisk eksportu; przy 2 wynikach komunikat informacyjny i przycisk eksportu; WSIiZ / 15 min — komunikat o braku okolic, bez przycisku eksportu; brak wyjątków |

T01–T20: **PASS** na `main` `653393e`. Nowe testy T18–T20 nie wymagały zmian w kodzie silnika.

### 2.2. Ręczne sprawdzenie interfejsu

Polecenie: `python -m streamlit run app.py`. Wykonała Valentyna Boksha, 23.11.2026, wersja `0df4f8b` Po zmianie `app.py` w PR #20 sprawdzenia w przeglądarce nie powtarzano; wersję `653393e` sprawdzono tylko automatycznie (Streamlit AppTest, asystent AI).

| ID | Przypadek | Oczekiwany wynik | Status |
|---|---|---|---|
| U01 | Wybór uczelni UR i budynku, „Generuj rekomendacje” | Karty z oceną, czasem i odległością | PASS |
| U02 | Mapa po wygenerowaniu | Koła, numery 1–3, znacznik uczelni, podkład mapy | PASS |
| U03 | Zmiana suwaka po wygenerowaniu | Stare wyniki znikają | PASS |
| U04 | „Bez limitu” | Trzy wyniki | PASS |
| U05 | Zastrzeżenie pod wynikami | Tekst o linii prostej i 4,5 km/h | PASS |
| U06 | Limit 15 min, WSIiZ (Sucharskiego 2) | Komunikat o braku okolic zamiast kart | PASS |
| U07 | Limit 15 min, część budynków | 1 lub 2 karty zamiast 3 | PASS — zgodne z R4 („maksymalnie trzy”); patrz punkt 4 |
| U08 | Uszkodzony plik danych w uruchomionej aplikacji | Komunikat „Nie można wczytać danych projektu” | NOT RUN ręcznie; sprawdzone automatycznie przez asystenta AI (Streamlit AppTest, kopia z `services.json = []`): komunikat bez wyjątku |
| U09 | Eksport rankingu: przycisk „Pobierz ranking TOP 3 (CSV)” (WSIiZ, 3 wyniki) | Plik `studentfinder_top3.csv` otwiera się w programie Excel: 11 kolumn, 3 wiersze, poprawne polskie znaki | PASS — Valentyna Boksha, 23.11.2026, `653393e`, Excel: kolumny rozdzielone, nagłówki, wartości i polskie znaki poprawne. Format liczb: patrz punkt 7. Automatycznie (asystent AI): przycisk pojawia się tylko przy wynikach |
| U10 | Inne przeglądarki i szerokości ekranu | Czytelny układ | NOT RUN |
| U11 | Mniej niż 3 wyniki (limit 15 min) | Komunikat, że znaleziono mniej okolic | NOT RUN ręcznie. Automatycznie (asystent AI): komunikat jest wyświetlany. Uwaga: dla jednego wyniku tekst brzmi „tylko 1 okolice” |

## 3. Pomiar niefunkcjonalny

**PASS.** Kryterium ustalono przed pomiarem: mediana czasu obliczenia rankingu ≤ 100 ms przy 100 powtórzeniach, 25 obszarach mieszkalnych i 500 usługach. Pomiar wykonał Serhii Popovych, 24.11.2026, na `main` `ed0366c`, Apple M1 Max (10 rdzeni, 32 GB), macOS 27.2.1, Python 3.15.2.

| Miara | Wynik |
|---|---|
| Mediana | 16,000 ms |
| Minimum | 15,748 ms |
| Maksimum | 17,090 ms |
| Powtórzenia | 100 |

Polecenie `python scripts/benchmark_recommendation.py --repetitions 100` użyło lokalizacji `way/197227711`, limitu 30 min i wag 3/2/2/2. Mierzono wyłącznie `recommend()`, bez wczytywania plików. Obciążenie maszyny: średnia 7,40 (1 min). Szczegóły i pełne wyjście: `results/lab7/benchmark.md`.

## 4. Ocena danych, wyników i kodu

**Dane** (uruchomił asystent AI, 23.11.2026):

- `python scripts/check_data.py --test-invalid` — 500 usług i 28 miejsc zajęć, 0 naruszeń, 3/3 próby na błędnych kopiach.
- Znane braki w źródle OSM: 21 usług bez nazwy źródłowej, 387 usług bez pełnego adresu. Kontrole nie potwierdzają kompletności OSM ani zgodności obiektów ze stanem w terenie.

**Wyniki:** przy limicie 15 minut i wagach 2/2/2/2: 13 miejsc zajęć ma 3 wyniki, 11 ma 2, 3 mają 1, a 1 (WSIiZ) nie ma żadnego. Przy 30 i 45 minutach oraz bez limitu każde miejsce ma 3 wyniki.

**Miara z Lab 4** (uruchomił asystent AI, `653393e`):

| Miara | Lab 4 (zapisane w `results/lab4/`) | Obecna wersja | Warunki |
|---|---|---|---|
| Ranking Weighted Scoring | `ranking_proposed.csv`: TOP 3 = `krakowska-poludnie-1` 68,8049; `drabinianka-1` 61,8920; `krola-1` 58,7790 | `RecommendationEngine.recommend()`: ta sama kolejność wszystkich 25 obszarów, największa różnica oceny 0,0 | PRz, Budynek P (`way/197227711`), wagi 3/2/2/2, bez limitu czasu |
| Zgodność TOP 3 Weighted Scoring / KNN | 2 z 3 dla każdego z 3 profili; to samo pierwsze miejsce | 2 z 3; to samo pierwsze miejsce (`python scripts/compare_knn_weighted.py`) | 25 obszarów, profile `balanced`, `university_priority`, `services_priority` |

Różnica: zapisane pliki `results/lab4/*.csv` zawierają nazwy obszarów sprzed zmiany etykiet (np. „Krakowska-Południe”); identyfikatory i oceny są takie same. Ponowne uruchomienie `python scripts/compare_methods.py` zmienia w tych plikach tylko nazwy.

Nie sprawdzano: rozdziały 1–11 `docs/experiment.md` opisują porównanie Brute force / Bounding box, którego nie wykonuje żaden skrypt; polecenie `compare_methods.py --radius 1000 --repetitions 100` kończy się błędem `unrecognized arguments`.

**Kod:** przegląd `docs/architecture.md` względem kodu — wynik w Issue #8. Zmiany wprowadzone po przeglądzie: nowy moduł `scripts/data_validation.py`; w `scripts/recommendation_engine.py` wywołanie walidacji w `from_files()` i odrzucanie wag NaN/inf w `recommend()`.

Przegląd fragmentu kodu, którego nie jestem autorką — `generate_recommendations()` i `RecommendationEngine.from_files()` w `scripts/recommendation_engine.py` (autor: Serhii Popovych), wersja `e6db774` (kod bez zmian w `2539038`), wykonany z pomocą asystenta AI:

| Kryterium | Wynik |
|---|---|
| Podział funkcji | Walidacja żądania, wczytanie danych i obliczenia są rozdzielone; funkcja publiczna zwraca statusy zamiast wyjątków — zgodnie z kontraktem. |
| Nazwy | Pola żądania i odpowiedzi zgodne z `docs/architecture.md` (punkt 4). |
| Obsługa wyjątków | Błędy żądania → `VALIDATION_ERROR`, błędy danych i obliczeń → `DATA_ERROR`; potwierdzone testami T11–T14. |
| Zgodność z metodą | Wzór punktacji, limity i kolejność przy remisie zgodne z `docs/problem.md`; potwierdzone testami T18–T20. |
| Uwaga 1 | `load_json()` czyta pliki jako `utf-8`, a `scripts/check_data.py` jako `utf-8-sig`. Plik ze znacznikiem BOM przejdzie kontrolę jakości, ale aplikacja go odrzuci (`JSONDecodeError`, komunikat o błędzie danych). Pliki projektu nie mają BOM. Nie poprawiano. |
| Uwaga 2 | Konstruktor `RecommendationEngine(...)` nie sprawdza powtórzonych ID (punkt 7). Nie poprawiano. |

`python scripts/test_knn.py` — 3/3 PASS (uruchomił asystent AI).

## 5. Statusy wymagań

| Wymaganie | Status | Dowód | Czego brakuje |
|---|---|---|---|
| R1 — wybór budynku | PASS | U01, U02, T11, T15 | — |
| R2 — wagi kryteriów | PASS | T12, T13, T18, T20, U03 | — |
| R3 — limit czasu | PASS | T14, T15, U05, U06 | — |
| R4 — maksymalnie trzy okolice | PASS | T15, U01, U02, U07 | Zgodność środków kół z danymi sprawdzono tylko wzrokowo |
| R5 — uzasadnienie | częściowo | T15 (niepuste uzasadnienie), U05 | Zgodność treści uzasadnienia z punktacją: NOT RUN |
| R6 — zakres projektu | PASS | T01, T15 — ranking powstaje bez danych o cenach i ofertach | — |

Statusy dotyczą wersji `main` `653393e`. `docs/report.md` podaje te same statusy.

## 6. Sprawdzenie dokumentacji

| Dokument | Status | Uwagi |
|---|---|---|
| `docs/architecture.md` | sprawdzony | 8 niezgodności opisanych w Issue #8; wszystkie poprawione (commity `0aeab7e`, PR #18, `2539038`) |
| `docs/report.md` | niezgodności | Układ zgodny z Lab 8. Po PR #20 nieaktualne: „funkcja eksportu rankingu nie istnieje” (rozdziały 1 i 5). Nie podano nazwy taga ani commita prezentowanej wersji |
| `docs/presentation.md` | niezgodności | Oba scenariusze demonstracji są wykonalne. Po PR #20 nieaktualne: „brak eksportu rankingu” (część 4, pytanie 3, wynik próby) |
| `README.md` — instrukcja uruchomienia | PASS | Instalacja z `requirements.txt` i uruchomienie aplikacji wykonane przez Valentynę Bokshę |
| `docs/user-guide.md` | częściowo | Dokument dodany w PR #20. Przejście instrukcji przez drugą osobę w nowym katalogu: NOT RUN. Porównanie treści z aplikacją (asystent AI): kroki, nazwy pól i przycisków zgodne z `app.py`. Braki względem układu z Lab 7: nie ma rozdziału o komunikatach błędów („Nie znaleziono okolic…”, „Nie można wczytać danych projektu…”) ani listy dozwolonych limitów czasu (15 / 30 / 45 min) |
| `docs/problem.md` | sprawdzony | Podział zadań zaktualizowany w PR #18 |

## 7. Znane błędy i ograniczenia

1. Tag `lab8-demo` wskazuje commit `2539038`; zmiany połączone później (eksport CSV, instrukcja użytkownika, aktualizacje tego dokumentu) nie są nim objęte, dopóki tag nie zostanie przeniesiony.
2. Konstruktor `RecommendationEngine(...)` wywołany bezpośrednio (bez plików) nie sprawdza powtórzonych ID; walidacja działa przy wczytywaniu przez `from_files()`.
3. Eksport CSV: czas ma przecinek dziesiętny (`27,2`), a ocena i odległości kropkę (`69.2`, `2038.0`). Excel z polskimi ustawieniami wczytuje wartości z kropką jako tekst. Wartości w pliku są poprawne; zespół zdecydował nie zmieniać formatu. Obejście: zamienić kropki na przecinki w kolumnach F oraz H–K. Brak testu automatycznego eksportu w repozytorium.
4. Nazwy obszarów mogą być niezgodne z polem `district`; przynależność administracyjna nie została niezależnie sprawdzona.
5. Odległości są liczone w linii prostej od środka obszaru; czas nie uwzględnia rzeczywistych tras.
6. Pomiar niefunkcjonalny wykonano przy wysokim obciążeniu maszyny (średnia 7,40 na 10 rdzeni); podane czasy są górnym oszacowaniem (punkt 3).
7. Testy interfejsu nie są zautomatyzowane w repozytorium.
8. Plik danych ze znacznikiem BOM jest odrzucany przez aplikację, choć przechodzi `scripts/check_data.py` (punkt 4).
9. `docs/user-guide.md` nie opisuje komunikatów błędów; `docs/report.md` i `docs/presentation.md` nadal podają, że eksportu nie ma.
10. `docs/experiment.md` (rozdziały 1–11) opisuje eksperyment niezgodny ze skryptami; zapisane `results/lab4/*.csv` mają nieaktualne nazwy obszarów.
