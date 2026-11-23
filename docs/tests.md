# Testy — Laboratorium 7

Autorka: Valentyna Boksha (dane i testowanie). Stan na 23.11.2026.

Statusy: **PASS** — sprawdzono, wynik zgodny z oczekiwanym; **FAIL** — sprawdzono, wynik niezgodny; **NOT RUN** — nie sprawdzano (z przyczyną).

## 1. Zakres oraz wersja kodu i danych

| Element | Wartość |
|---|---|
| Gałąź | `main`, commit `e6db774` (po połączeniu PR #14–#18) |
| Commit kodu | Kod aplikacji i silnika (`app.py`, `scripts/`) w `e6db774` jest identyczny z commitem `0df4f8b`, na którym wykonano pierwsze uruchomienia |
| Dane | `data/processed/services.json` (500), `data/processed/universities.json` (28), `config/residential-areas.json` (25) — bez zmian od commita `1d9e312` |
| Środowisko | Windows 11, Python 3.12.6, streamlit 1.67.0, folium 1.0.0, streamlit-folium 0.27.4 |

Zakres: wczytywanie i walidacja plików danych, parametry żądania, przebieg dane → silnik → odpowiedź, ręczne sprawdzenie interfejsu.

Poza zakresem: eksport rankingu i instrukcja użytkownika (jeszcze nie istnieją).

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

T01–T20: **PASS** na `main` `e6db774`. Nowe testy T18–T20 nie wymagały zmian w kodzie silnika.

### 2.2. Ręczne sprawdzenie interfejsu

Polecenie: `python -m streamlit run app.py`. Wykonała Valentyna Boksha, 23.11.2026, wersja `0df4f8b` (ten sam kod aplikacji co w `main` `e6db774`; po połączeniu sprawdzenia w przeglądarce nie powtarzano).

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
| U09 | Eksport rankingu | Plik z TOP 3 | NOT RUN — funkcja nie istnieje |
| U10 | Inne przeglądarki i szerokości ekranu | Czytelny układ | NOT RUN |

## 3. Pomiar niefunkcjonalny

**NOT RUN.** Kryterium akceptacji czasu odpowiedzi nie zostało jeszcze uzgodnione w zespole, a katalog `results/lab7/` nie istnieje. Skrypt `scripts/benchmark_recommendation.py` uruchamia się poprawnie na `e6db774`, ale bez kryterium wynik nie jest oceniany. Pomiar należy do części Serhiia Popovycha.

## 4. Ocena danych, wyników i kodu

**Dane** (uruchomił asystent AI, 23.11.2026):

- `python scripts/check_data.py --test-invalid` — 500 usług i 28 miejsc zajęć, 0 naruszeń, 3/3 próby na błędnych kopiach.
- Znane braki w źródle OSM: 21 usług bez nazwy źródłowej, 387 usług bez pełnego adresu. Kontrole nie potwierdzają kompletności OSM ani zgodności obiektów ze stanem w terenie.

**Wyniki:** przy limicie 15 minut i wagach 2/2/2/2: 13 miejsc zajęć ma 3 wyniki, 11 ma 2, 3 mają 1, a 1 (WSIiZ) nie ma żadnego. Przy 30 i 45 minutach oraz bez limitu każde miejsce ma 3 wyniki.

**Miara z Lab 4:** porównanie wyniku obecnej wersji z miarą z `docs/experiment.md` — **NOT RUN** (należy do części Dany Stadnyk i Serhiia Popovycha).

**Kod:** przegląd `docs/architecture.md` względem kodu — wynik w Issue #8. Zmiany wprowadzone po przeglądzie: nowy moduł `scripts/data_validation.py`; w `scripts/recommendation_engine.py` wywołanie walidacji w `from_files()` i odrzucanie wag NaN/inf w `recommend()`.

Przegląd fragmentu kodu, którego nie jestem autorką — `generate_recommendations()` i `RecommendationEngine.from_files()` w `scripts/recommendation_engine.py` (autor: Serhii Popovych), wersja `e6db774`, wykonany z pomocą asystenta AI:

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

Statusy dotyczą wersji `main` `e6db774`. `docs/report.md` podaje te same statusy.

## 6. Sprawdzenie dokumentacji

| Dokument | Status | Uwagi |
|---|---|---|
| `docs/architecture.md` | sprawdzony | 8 niezgodności opisanych w Issue #8; sześć poprawionych. Otwarte: diagram sekwencji pokazuje osobne wywołania walidacji i silnika; punkt 5.2 wymienia nieistniejący katalog `results/lab6/` |
| `docs/report.md` | sprawdzony | Prędkość, pole `justification`, brak eksportu i statusy wymagań poprawione w PR #18 i commicie `e6db774` |
| `docs/presentation.md` | niezgodności | Scenariusz 2 podaje limit 5 min lub 1 min, którego nie ma w formularzu (dostępne: 15 / 30 / 45 min / bez limitu; brak okolic daje WSIiZ przy 15 min); prędkość 80 m/min (4,8 km/h) zamiast 75 m/min (4,5 km/h) |
| `README.md` — instrukcja uruchomienia | PASS | Instalacja z `requirements.txt` i uruchomienie aplikacji wykonane przez Valentynę Bokshę |
| `docs/user-guide.md` | NOT RUN | Dokument nie istnieje; sprawdzenie instrukcji przez drugą osobę niewykonane |
| `docs/problem.md` | sprawdzony | Podział zadań zaktualizowany w PR #18 |

## 7. Znane błędy i ograniczenia

1. `docs/presentation.md` zawiera scenariusz, którego nie da się wykonać w aplikacji, i nieaktualną prędkość (punkt 6).
2. Konstruktor `RecommendationEngine(...)` wywołany bezpośrednio (bez plików) nie sprawdza powtórzonych ID; walidacja działa przy wczytywaniu przez `from_files()`.
3. Brak eksportu rankingu.
4. Nazwy obszarów mogą być niezgodne z polem `district`; przynależność administracyjna nie została niezależnie sprawdzona.
5. Odległości są liczone w linii prostej od środka obszaru; czas nie uwzględnia rzeczywistych tras.
6. Brak pomiaru niefunkcjonalnego (punkt 3).
7. Testy interfejsu nie są zautomatyzowane w repozytorium.
8. Plik danych ze znacznikiem BOM jest odrzucany przez aplikację, choć przechodzi `scripts/check_data.py` (punkt 4).
9. Brak `docs/user-guide.md` i porównania z miarą z Lab 4.
