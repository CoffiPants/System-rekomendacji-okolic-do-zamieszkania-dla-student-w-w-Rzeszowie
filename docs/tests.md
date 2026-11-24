# Testy — Laboratorium 7

Autorka: Valentyna Boksha (dane i testowanie). Stan na 24.11.2026.

Statusy: **PASS** — sprawdzono, wynik zgodny z oczekiwanym; **FAIL** — sprawdzono, wynik niezgodny; **NOT RUN** — nie sprawdzano (z przyczyną).

## 1. Zakres oraz wersja kodu i danych

| Element | Wartość |
|---|---|
| Gałąź | `main`, commit `a8f2e18` (po połączeniu PR #14–#26). Kod i dane są identyczne z commitem `653393e`; PR #21–#24 zmieniają tylko dokumentację i dodają `results/lab7/`; PR #25 zmienia w `app.py` jeden komunikat (liczba pojedyncza „1 okolicę”) oraz dodaje slajdy; PR #22 i #26 zmieniają tylko dokumentację |
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

| ID | Wymaganie | Rodzaj | Przypadek (wejście) | Oczekiwany wynik | Podstawa oczekiwania | Test |
|---|---|---|---|---|---|---|
| T01 | R6 | poprawny | Pliki projektu | Wczytane 500 / 28 / 25 rekordów | `docs/data.md` | `test_project_files_are_loaded` |
| T02 | UC-01, krok 3 | błędny | Brak pliku | Błąd `OSError`, który aplikacja zamienia na komunikat | architektura 4.3 | `test_missing_file_is_reported` |
| T03 | UC-01, krok 3 | błędny | Uszkodzony JSON | Błąd `ValueError` | architektura 4.3 | `test_damaged_json_is_reported` |
| T04 | UC-01, krok 3 | błędny | `[]` zamiast obiektu JSON | Odrzucenie z komunikatem „musi być obiektem JSON” | struktura plików, architektura 5.2 | `test_top_level_list_is_rejected` |
| T05 | UC-01, krok 3 | pusty | Pusta lista rekordów | Odrzucenie „Lista … jest pusta” | silnik wymaga niepustych zbiorów | `test_empty_record_list_is_rejected` |
| T06 | UC-01, krok 3 | błędny | Powtórzony `id` | Odrzucenie „powtórzony identyfikator” | `id` jest kluczem (architektura 5.2) | `test_duplicate_id_is_rejected` |
| T07 | UC-01, krok 3 | błędny | Współrzędne 200, −91, 181, tekst, brak, NaN | Odrzucenie | zakres WGS84 | `test_invalid_coordinates_are_rejected`, `test_missing_coordinate_is_rejected`, `test_nan_coordinate_is_rejected` |
| T08 | UC-01, krok 3 | graniczny | Współrzędne 90 i −180 | Przyjęte | zakres WGS84 włącznie | `test_boundary_coordinates_are_accepted` |
| T09 | UC-01, krok 3 | błędny | Nieznana lub brakująca kategoria; kategoria bez usług | Odrzucenie | kategorie `shop`, `bus_stop`, `park` | `test_unknown_category_is_rejected`, `test_missing_category_is_rejected`, `test_category_without_any_service_is_rejected` |
| T10 | UC-01, krok 3; R1 | błędny | Brak `university`, `name`, `address` miejsca zajęć; brak `name`, `district` obszaru | Odrzucenie „brak pola …” | pola używane przez `app.py` i odpowiedź silnika | `test_location_fields_used_by_interface_are_required`, `test_area_fields_used_in_results_are_required` |
| T11 | R1 | błędny | Nieznane `location_id`, zły typ | `VALIDATION_ERROR` | architektura 4.3 | `test_unknown_location_is_rejected`, `test_invalid_location_type_is_rejected` |
| T12 | R2 | graniczny | Wagi 1 i 3 | `SUCCESS` | wagi 1–3 | `test_boundary_weights_are_accepted` |
| T13 | R2 | błędny | Wagi 0, 4, −1, 2.0, tekst, NaN, inf, niepełny zestaw | `VALIDATION_ERROR` | wagi całkowite 1–3 | `test_weights_outside_range_are_rejected`, `test_invalid_weight_type_is_rejected`, `test_incomplete_or_extended_weights_are_rejected` |
| T14 | R3 | poprawny / błędny | Limit 15, 30, 45, brak; inne wartości | Dozwolone: `SUCCESS` lub `NO_MATCHES`; pozostałe: `VALIDATION_ERROR` | architektura 4.1 | `test_allowed_time_limits_are_accepted`, `test_other_time_limits_are_rejected` |
| T15 | R3, R4, R5 | integracyjny | 28 miejsc zajęć × 4 limity na danych projektu | Do 3 wyników, malejąco według oceny, remis według `area_id`, czas ≤ limit, ocena 0–100, promień 500 m, niepuste uzasadnienie i zastrzeżenie | kryteria odbioru UC-01 | `test_every_location_and_limit_gives_a_consistent_response` |
| T16 | R4 | integracyjny | To samo żądanie dwa razy | Identyczna odpowiedź | determinizm rankingu | `test_same_request_gives_same_response` |
| T17 | R3 | integracyjny | Czas a odległość | czas = odległość / 75 m/min | prędkość 4,5 km/h | `test_walk_time_matches_distance_at_4_5_kmh` |
| T18 | R2 | poprawny | R2: jeden obszar o znanych odległościach (1500 / 250 / 300 / 1200 m), siedem ustawień wag | Oceny kryteriów 50 / 75 / 50 / 20; ocena końcowa równa obliczeniu ręcznemu, np. wagi 1/1/1/1 → 48,75, sklep 3 → 57,50, park 3 → 39,17 | wzór punktacji z `docs/problem.md`; obliczenia zapisane w teście | `tests/test_weight_scoring.py`: `test_distances_and_criterion_scores`, `test_final_score_for_each_weight_setting`, `test_higher_weight_moves_score_towards_that_criterion` |
| T19 | R2 | graniczny | Usługa dalej niż limit punktacji (park 2000 m) | Ocena kryterium 0, obszar pozostaje w rankingu (43,75) | limit punktacji nie wyklucza obszaru | `test_service_beyond_scoring_limit_gives_zero_but_keeps_area` |
| T20 | R2, R4 | poprawny | R2 i R4: dwa obszary, zmiana wagi zmienia kolejność | Równe wagi: remis 50 / 50, pierwszy `a` (według ID); uczelnia 3 → `a` 60, `b` 40; sklep 3 → `b` 60, `a` 40 | wzór punktacji, kryterium odbioru 3 UC-01 | `test_equal_weights_give_a_tie_resolved_by_area_id`, `test_university_weight_puts_area_near_university_first`, `test_shop_weight_puts_area_near_shop_first` |

Dziennik uruchomień:

| Data | Wersja | Kto uruchomił | Wynik |
|---|---|---|---|
| 23.11.2026 | `1d9e312` + nowe testy, bez zmian w silniku | Valentyna Boksha, lokalnie | 44 testy: 29 niepowodzeń, 3 błędy. Część niepowodzeń wynika tylko z innej treści komunikatu; faktycznie niewykrywane były: powtórzone ID, `[]` zamiast obiektu (`AttributeError`), nieznana kategoria, brak `university`/`address`, waga NaN/inf w `recommend()`. |
| 23.11.2026 | `0df4f8b` | Valentyna Boksha, lokalnie | **44/44 PASS** (`Ran 44 tests in 4.564s`, `OK`) |
| 23.11.2026 | `27c0438` + `tests/test_weight_scoring.py` | Valentyna Boksha, lokalnie | **51/51 PASS** (`Ran 51 tests in 4.856s`, `OK`) |
| 23.11.2026 | `main` `d3aa845` (bez `test_weight_scoring.py`) | Valentyna Boksha, lokalnie | 44/44 PASS; `check_data.py --test-invalid`: 0 naruszeń, 3/3; `test_knn.py`: OK; Streamlit AppTest: brak wyjątków, 3 karty |
| 23.11.2026 | `main` `d3aa845` + `tests/test_weight_scoring.py` (commit `de8b08a`) | Valentyna Boksha, lokalnie | **51/51 PASS** (`Ran 51 tests in 2.348s`, `OK`) |
| 23.11.2026 | `main` `e6db774` | Valentyna Boksha, lokalnie | **51/51 PASS** (`Ran 51 tests in 2.380s`, `OK`) |
| 23.11.2026 | `main` `e6db774` | Valentyna Boksha, lokalnie | `check_data.py --test-invalid`: 0 naruszeń, 3/3; `verify_repeatability.py`: PASS; `audit_data.py`: PASS; `test_knn.py`: OK; Streamlit AppTest: brak wyjątków, 3 karty |
| 23.11.2026 | `main` `2539038` (tag `lab8-demo`) | Valentyna Boksha, lokalnie | **51/51 PASS** (`Ran 51 tests in 2.437s`, `OK`) |
| 23.11.2026 | `main` `2539038` (tag `lab8-demo`) | Valentyna Boksha, lokalnie | `check_data.py --test-invalid`: 0 naruszeń, 3/3; `verify_repeatability.py`: PASS; `audit_data.py`: PASS; `test_knn.py`: OK; Streamlit AppTest: scenariusz 1 — 3 karty, scenariusz 2 (WSIiZ, 15 min) — komunikat o braku okolic, brak wyjątków |
| 23.11.2026 | `main` `653393e` | Valentyna Boksha, lokalnie | **51/51 PASS** (`Ran 51 tests in 2.362s`, `OK`) |
| 23.11.2026 | `main` `653393e` | Valentyna Boksha, lokalnie | `check_data.py --test-invalid`: 0 naruszeń, 3/3; `test_knn.py`: OK; Streamlit AppTest: 3 karty i przycisk eksportu; przy 2 wynikach komunikat informacyjny i przycisk eksportu; WSIiZ / 15 min — komunikat o braku okolic, bez przycisku eksportu; brak wyjątków |
| 24.11.2026 | `main` `ed0366c` | Valentyna Boksha, lokalnie | 51/51 PASS (`Ran 51 tests in 2.325s`, `OK`) |
| 24.11.2026 | `main` `ed0366c`, nowy katalog i nowe środowisko `.venv` | Valentyna Boksha, lokalnie | 51/51 PASS (`Ran 51 tests in 2.671s`, `OK`) |
| 24.11.2026 | `main` `2672012` | Valentyna Boksha, lokalnie | 51/51 PASS (`Ran 51 tests in 3.042s`, `OK`); `check_data.py --test-invalid`: 0 naruszeń, 3/3 |
| 24.11.2026 | `main` `632c6cc`, nowy katalog i środowisko `.venv` | Valentyna Boksha, lokalnie | 51/51 PASS (`Ran 51 tests in 2.343s`, `OK`); Streamlit AppTest: przy 1 wyniku „tylko 1 okolicę spełniającą”, przy 2 „2 okolice spełniające”, WSIiZ / 15 min — komunikat o braku okolic; brak wyjątków |

T01–T20: **PASS** na `main` `632c6cc`; w `a8f2e18` kod i dane są bez zmian. Dowód: wynik polecenia z punktu 2.1; raport w pliku nie jest zapisywany. Nowe testy T18–T20 nie wymagały zmian w kodzie silnika.

### 2.2. Ręczne sprawdzenie interfejsu

Polecenie: `python -m streamlit run app.py`. U01–U07 wykonała Valentyna Boksha 23.11.2026 na wersji `0df4f8b`. Po zmianie `app.py` w PR #20 te same kroki (wybór uczelni i budynku, limit, wagi, generowanie, mapa, eksport, brak okolic dla WSIiZ przy 15 min) powtórzyła 24.11.2026 na wersji `ed0366c` w ramach sprawdzenia instrukcji użytkownika (punkt 6) — bez niezgodności.

| ID | Przypadek | Oczekiwany wynik | Status |
|---|---|---|---|
| U01 | Wybór uczelni UR i budynku, „Generuj rekomendacje” | Karty z oceną, czasem i odległością | PASS |
| U02 | Mapa po wygenerowaniu | Koła, numery 1–3, znacznik uczelni, podkład mapy | PASS |
| U03 | Zmiana suwaka po wygenerowaniu | Stare wyniki znikają | PASS |
| U04 | „Bez limitu” | Trzy wyniki | PASS |
| U05 | Zastrzeżenie pod wynikami | Tekst o linii prostej i 4,5 km/h | PASS |
| U06 | Limit 15 min, WSIiZ (Sucharskiego 2) | Komunikat o braku okolic zamiast kart | PASS |
| U07 | Limit 15 min, część budynków | 1 lub 2 karty zamiast 3 | PASS — zgodne z R4 („maksymalnie trzy”); patrz punkt 4 |
| U08 | Uszkodzony plik danych w uruchomionej aplikacji | Komunikat „Nie można wczytać danych projektu” | NOT RUN ręcznie; sprawdzone automatycznie (Streamlit AppTest, kopia z `services.json = []`): komunikat bez wyjątku |
| U09 | Eksport rankingu: przycisk „Pobierz ranking TOP 3 (CSV)” (WSIiZ, 3 wyniki) | Plik `studentfinder_top3.csv` otwiera się w programie Excel: 11 kolumn, 3 wiersze, poprawne polskie znaki | PASS — Valentyna Boksha, 23.11.2026, `653393e`, Excel: kolumny rozdzielone, nagłówki, wartości i polskie znaki poprawne. Format liczb: patrz punkt 7. Automatycznie (Streamlit AppTest): przycisk pojawia się tylko przy wynikach |
| U10 | Inne przeglądarki i szerokości ekranu | Czytelny układ | NOT RUN |
| U11 | Mniej niż 3 wyniki (limit 15 min) | Komunikat, że znaleziono mniej okolic | PASS — Valentyna Boksha, 24.11.2026, `632c6cc`, w ramach sprawdzenia instrukcji. Automatycznie (Streamlit AppTest): „tylko 1 okolicę spełniającą” / „2 okolice spełniające” — forma poprawiona w PR #25 |

## 3. Pomiar niefunkcjonalny

**PASS.** Kryterium ustalono przed pomiarem: mediana czasu obliczenia rankingu ≤ 100 ms przy 100 powtórzeniach, 25 obszarach mieszkalnych i 500 usługach. Pomiar wykonał Serhii Popovych, 24.11.2026, na `main` `ed0366c`, Apple M1 Max (10 rdzeni, 32 GB), macOS 27.2.1, Python 3.15.2.

| Miara | Wynik |
|---|---|
| Mediana | 16,000 ms |
| Minimum | 15,748 ms |
| Maksimum | 17,090 ms |
| Powtórzenia | 100 |

Polecenie `python scripts/benchmark_recommendation.py --repetitions 100` użyło lokalizacji `way/197227711`, limitu 30 min i wag 3/2/2/2. Mierzono wyłącznie `recommend()`, bez wczytywania plików. Obciążenie maszyny: średnia 7,40 (1 min). Szczegóły i pełne wyjście: `results/lab7/benchmark.md`.

Niezależne powtórzenie (Valentyna Boksha, 24.11.2026, `main` `2672012`, Windows 11, Python 3.12.6, to samo polecenie): mediana 18,126 ms, minimum 16,531 ms, maksimum 31,465 ms, 100 powtórzeń, ten sam ranking TOP 3. Kryterium ≤ 100 ms jest spełnione także na drugim stanowisku.

## 4. Ocena danych, wyników i kodu

**Dane** (23.11.2026):

- `python scripts/check_data.py --test-invalid` — 500 usług i 28 miejsc zajęć, 0 naruszeń, 3/3 próby na błędnych kopiach.
- Znane braki w źródle OSM: 21 usług bez nazwy źródłowej, 387 usług bez pełnego adresu. Kontrole nie potwierdzają kompletności OSM ani zgodności obiektów ze stanem w terenie.

**Wyniki:** przy limicie 15 minut i wagach 2/2/2/2: 13 miejsc zajęć ma 3 wyniki, 11 ma 2, 3 mają 1, a 1 (WSIiZ) nie ma żadnego. Przy 30 i 45 minutach oraz bez limitu każde miejsce ma 3 wyniki.

**Miara z Lab 4** (wersja `653393e`):

| Miara | Lab 4 (zapisane w `results/lab4/`) | Obecna wersja | Warunki |
|---|---|---|---|
| Ranking Weighted Scoring | `ranking_proposed.csv`: TOP 3 = `krakowska-poludnie-1` 68,8049; `drabinianka-1` 61,8920; `krola-1` 58,7790 | `RecommendationEngine.recommend()`: ta sama kolejność wszystkich 25 obszarów, największa różnica oceny 0,0 | PRz, Budynek P (`way/197227711`), wagi 3/2/2/2, bez limitu czasu |
| Zgodność TOP 3 Weighted Scoring / KNN | 2 z 3 dla każdego z 3 profili; to samo pierwsze miejsce | 2 z 3; to samo pierwsze miejsce (`python scripts/compare_knn_weighted.py`) | 25 obszarów, profile `balanced`, `university_priority`, `services_priority` |

Różnica: zapisane pliki `results/lab4/*.csv` zawierają nazwy obszarów sprzed zmiany etykiet (np. „Krakowska-Południe”); identyfikatory i oceny są takie same. Ponowne uruchomienie `python scripts/compare_methods.py` zmienia w tych plikach tylko nazwy.

Nie sprawdzano: rozdziały 1–11 `docs/experiment.md` opisują porównanie Brute force / Bounding box, którego nie wykonuje żaden skrypt; polecenie `compare_methods.py --radius 1000 --repetitions 100` kończy się błędem `unrecognized arguments`.

**Kod:** przegląd `docs/architecture.md` względem kodu — wynik w Issue #8. Zmiany wprowadzone po przeglądzie: nowy moduł `scripts/data_validation.py`; w `scripts/recommendation_engine.py` wywołanie walidacji w `from_files()` i odrzucanie wag NaN/inf w `recommend()`.

Przegląd fragmentu kodu, którego nie jestem autorką (zapisany także w opisie [PR #19](https://github.com/CoffiPants/System-rekomendacji-okolic-do-zamieszkania-dla-student-w-w-Rzeszowie/pull/19)) — `generate_recommendations()` i `RecommendationEngine.from_files()` w `scripts/recommendation_engine.py` (autor: Serhii Popovych), wersja `e6db774` (kod bez zmian w `2539038`):

| Kryterium | Wynik |
|---|---|
| Podział funkcji | Walidacja żądania, wczytanie danych i obliczenia są rozdzielone; funkcja publiczna zwraca statusy zamiast wyjątków — zgodnie z kontraktem. |
| Nazwy | Pola żądania i odpowiedzi zgodne z `docs/architecture.md` (punkt 4). |
| Obsługa wyjątków | Błędy żądania → `VALIDATION_ERROR`, błędy danych i obliczeń → `DATA_ERROR`; potwierdzone testami T11–T14. |
| Zgodność z metodą | Wzór punktacji, limity i kolejność przy remisie zgodne z `docs/problem.md`; potwierdzone testami T18–T20. |
| Uwaga 1 | `load_json()` czyta pliki jako `utf-8`, a `scripts/check_data.py` jako `utf-8-sig`. Plik ze znacznikiem BOM przejdzie kontrolę jakości, ale aplikacja go odrzuci (`JSONDecodeError`, komunikat o błędzie danych). Pliki projektu nie mają BOM. Nie poprawiano. |
| Uwaga 2 | Konstruktor `RecommendationEngine(...)` nie sprawdza powtórzonych ID (punkt 7). Nie poprawiano. |

`python scripts/test_knn.py` — 3/3 PASS.

## 5. Statusy wymagań

| Wymaganie | Status | Dowód | Czego brakuje |
|---|---|---|---|
| R1 — wybór budynku | spełnione | U01, U02, T11, T15 | — |
| R2 — wagi kryteriów | spełnione | T12, T13, T18, T20, U03 | — |
| R3 — limit czasu | spełnione | T14, T15, U05, U06 | — |
| R4 — maksymalnie trzy okolice | spełnione | T15, U01, U02, U07 | Zgodność środków kół z danymi sprawdzono tylko wzrokowo |
| R5 — uzasadnienie | spełnione częściowo; zgodność treści niesprawdzona | T15 (niepuste uzasadnienie), U05 | Zgodność treści uzasadnienia z punktacją: NOT RUN |
| R6 — zakres projektu | spełnione | T01, T15 — ranking powstaje bez danych o cenach i ofertach | — |

Statusy: spełnione / niespełnione / niesprawdzone. Dotyczą wersji `main` `a8f2e18` (kod i dane jak w `632c6cc`). `docs/report.md` podaje te same statusy.

## 6. Sprawdzenie dokumentacji

| Dokument | Status | Uwagi |
|---|---|---|
| `docs/architecture.md` | sprawdzony | 8 niezgodności opisanych w Issue #8; wszystkie poprawione (commity `0aeab7e`, PR #18, `2539038`). Komunikat błędu danych i dekorator buforowania w ADR poprawione w PR #24 |
| `docs/report.md` | niezgodności | Układ zgodny z Lab 8; eksport, instrukcja, R6 i wkład zespołu poprawione w PR #24. Otwarte: w trzech miejscach pomiar niefunkcjonalny ma nadal status `NOT RUN` (wykonany w PR #23); rozdział 4 nazywa Weighted Scoring „wariantem bazowym”, a w Lab 4 wariantem bazowym była sama odległość do uczelni; skrypty KNN przypisano Serhiiowi, w historii jedyną autorką jest Dana; audyt gotowości podaje tag `lab8-demo` jako gotowy, choć wskazuje commit `2539038` |
| `docs/presentation.md` | niezgodności | Oba scenariusze demonstracji są wykonalne; eksport opisany poprawnie (PR #24). Otwarte: pomiar niefunkcjonalny ma nadal status `NOT RUN` (część 4 i pytanie 3). Sekcja „Wynik próby” została w PR #26 zastąpiona pustymi polami — próba jeszcze się nie odbyła |
| `README.md` — instrukcja uruchomienia | PASS | 23.11.2026, Valentyna Boksha, wersja `0df4f8b`: instalacja z `requirements.txt`, uruchomienie aplikacji, testy. 24.11.2026, wersja `ed0366c`: `git clone` do nowego pustego katalogu, nowe środowisko `.venv`, `python -m pip install -r requirements.txt` bez błędów, 51/51 testów PASS, aplikacja uruchomiona. Uwaga: w bardzo głęboko zagnieżdżonym katalogu instalacja nie powiodła się przez limit długości ścieżki w systemie Windows (pakiet `streamlit`); w katalogu o krótszej ścieżce przebiegła poprawnie |
| `docs/user-guide.md` | PASS | Wersja po PR #25 (układ z Lab 7: dane wejściowe, kroki, interpretacja, komunikaty błędów). 24.11.2026, Valentyna Boksha (nie jest autorką instrukcji), `main` `632c6cc`, aplikacja uruchomiona z nowego katalogu i nowego środowiska. Wykonane: tabela parametrów (1.2), kroki 2.2–2.7 (uczelnia, budynek, limit, wagi, generowanie, zniknięcie wyników po zmianie ustawień, mapa, pobranie CSV), interpretacja (3), komunikaty z rozdziału 4: brak okolic (WSIiZ, 15 min) i mniej niż trzy okolice. Wynik: kroki wykonalne, opisy zgodne z ekranem. Znaleziona niezgodność: w punktach 1.2 i 2.2 pola były opisane bez nazw z ekranu („Budynek lub wydział” zamiast „Wybierz budynek / wydział”). Wprowadzona poprawka: w PR #27 dopisano w instrukcji dokładne nazwy pól z aplikacji („Wybierz uczelnię”, „Wybierz budynek / wydział”, „Maksymalny czas dojścia do uczelni”). Komunikat „Nie można wczytać danych projektu…” sprawdzony tylko automatycznie na uszkodzonej kopii danych (wersja `0df4f8b`). Wcześniejsze przejście (23–24.11, wersja `ed0366c`) dotyczyło poprzedniego układu instrukcji |
| `docs/problem.md` | sprawdzony | Podział ról i odwołanie do `docs/tests.md` poprawione w PR #24. Scenariusz prezentacji (`docs/presentation.md`) jest przypisany Danie, a w `docs/report.md` Paulinie |
| `docs/implementation.md` | sprawdzony | Przepisany w PR #23: 51 testów, moduł walidacji, eksport CSV, sprawdzona wersja i osoba weryfikująca, ocena usprawnienia (przed/po), pomiar z warunkami. Otwarte: punkty 6.4 i 6.5 podają status `DATA_ERROR` dla błędu wczytania danych w aplikacji — aplikacja pokazuje komunikat z `load_engine()`; poprawka jest w gałęzi `serhii-lab7-lab6` (commit `f771de8`), jeszcze niepołączona |

## 7. Znane błędy i ograniczenia

1. Tag `lab8-demo` wskazuje commit `2539038`; zmiany połączone później (eksport CSV, instrukcja użytkownika, aktualizacje tego dokumentu) nie są nim objęte, dopóki tag nie zostanie przeniesiony.
2. Konstruktor `RecommendationEngine(...)` wywołany bezpośrednio (bez plików) nie sprawdza powtórzonych ID; walidacja działa przy wczytywaniu przez `from_files()`.
3. Eksport CSV: czas ma przecinek dziesiętny (`27,2`), a ocena i odległości kropkę (`69.2`, `2038.0`). Excel z polskimi ustawieniami wczytuje wartości z kropką jako tekst. Wartości w pliku są poprawne; zespół zdecydował nie zmieniać formatu. Obejście: zamienić kropki na przecinki w kolumnach F oraz H–K. Brak testu automatycznego eksportu w repozytorium.
4. Nazwy obszarów mogą być niezgodne z polem `district`; przynależność administracyjna nie została niezależnie sprawdzona.
5. Odległości są liczone w linii prostej od środka obszaru; czas nie uwzględnia rzeczywistych tras.
6. Pomiar niefunkcjonalny wykonano przy wysokim obciążeniu maszyny (średnia 7,40 na 10 rdzeni); podane czasy są górnym oszacowaniem (punkt 3).
7. Testy interfejsu nie są zautomatyzowane w repozytorium.
8. Plik danych ze znacznikiem BOM jest odrzucany przez aplikację, choć przechodzi `scripts/check_data.py` (punkt 4).
9. `docs/report.md` i `docs/presentation.md` nadal podają pomiar niefunkcjonalny jako `NOT RUN`; slajd 10 w `presentation/slides.pptx` i `slides.pdf` również („Pełny benchmark: NOT RUN”).
10. `docs/experiment.md` (rozdziały 1–11) opisuje eksperyment niezgodny ze skryptami; zapisane `results/lab4/*.csv` mają nieaktualne nazwy obszarów.
11. `docs/implementation.md`: status `DATA_ERROR` przy błędzie wczytania danych w aplikacji (punkt 6) — poprawka niepołączona.
12. Spośród PR #1–#25 zapisany przegląd (review) innej osoby mają tylko PR #1 i PR #25 (stan dla PR #1–#26); przegląd kodu z punktu 4 jest zapisany w opisie PR #19.
