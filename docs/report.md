# Raport końcowy projektu — Laboratorium 8

## 1. Podsumowanie celu i zakresu systemu
Celem projektu było zaprojektowanie, zaimplementowanie i przetestowanie **systemu rekomendacji okolic zamieszkania dla studentów w Rzeszowie**. Aplikacja wspiera studentów w wyborze lokalizacji mieszkania dopasowanej do miejsca odbywania zajęć oraz indywidualnych preferencji dotyczących infrastruktury miejskiej (sklepów, przystanków autobusowych oraz terenów zielonych), przy jednoczesnym uwzględnieniu maksymalnego akceptowalnego czasu dojścia pieszo na uczelnię.

System zrealizowano w języku **Python** jako modułową aplikację analityczną połączoną z interaktywnym interfejsem użytkownika w bibliotece **Streamlit**, pracującą bezpośrednio na ustrukturyzowanych plikach **JSON** i **CSV** (zgodnie z decyzją architektoniczną `docs/decisions/001-storage.md`).

---

## 2. Przebieg prac projektowych i podział ról w zespole

Prace podzielono na spójne etapy inżynierskie realizowane w repozytorium GitHub z wykorzystaniem gałęzi tematycznych i przeglądów kodu (*Pull Requests*):

1. **Analiza problemu i danych (Lab 1–3):**
  - Zdefiniowano wymagania funkcjonalne (**R1–R6**) i kryteria jakości w `docs/problem.md`.
  - Pobrano dane przestrzenne z Overpass API (OpenStreetMap) oraz przygotowano potok przetwarzania (`scripts/prepare_data.py`), uzyskując oczyszczone zbiory: **28 lokalizacji uczelni** (`data/processed/universities.json`), **500 punktów usługowych** (`data/processed/services.json`) oraz **25 obszarów mieszkalnych** o promieniu 500 m w 20 osiedlach Rzeszowa (`config/residential-areas.json`).
  - Potwierdzono jakość, kompletność i determinizm przetwarzania (`scripts/check_data.py`, `scripts/audit_data.py`, `scripts/verify_repeatability.py`).
2. **Eksperymenty badawcze (Lab 4):**
  - Porównano metody oceny obszarów (Weighted Scoring oraz podejścia sąsiedztwa) pod kątem stabilności rankingów i wrażliwości na zmianę wag preferencji (`scripts/compare_methods.py`, `results/lab4/`).
3. **Projekt architektury, implementacja i testy (Lab 5–8):**
  - **Paulina Michalska:** Opracowanie dokumentacji architektury (`docs/architecture.md`), kontraktu interfejsu, modelu logicznego/fizycznego danych, dokumentacji wdrożeniowej (`docs/implementation.md`), raportu końcowego (`docs/report.md`), scenariusza prezentacji (`docs/presentation.md`) oraz aktualizacja `docs/problem.md` i `README.md`.
  - **Serhii Popovych:** Implementacja silnika rekomendacji (`scripts/recommendation_engine.py`), testów jednostkowych (`tests/test_recommendation_engine.py`), skryptu pomiaru wydajności (`scripts/benchmark_recommendation.py`) oraz weryfikacji etykiet obszarów (`docs/area-name-audit.md`).
  - **Dana Stadnyk:** Budowa interaktywnego interfejsu użytkownika w Streamlit (`app.py`, `.streamlit/config.toml`), wizualizacja mapy Rzeszowa oraz skrypty kontroli i audytu danych (`scripts/check_data.py`, `scripts/audit_data.py`).
  - **Valentyna Boksha:** Walidacja danych wejściowych (`scripts/data_validation.py`), testy automatyczne i punktacji (`tests/test_weight_scoring.py`), przegląd architektury (`Issue #8`) oraz dokumentacja testów (`docs/tests.md` na gałęzi `valentyna-data-validation`).

---

## 3. Weryfikacja spełnienia wymagań funkcjonalnych (R1–R6)

Statusy na podstawie wyników z `docs/tests.md` po scaleniu wszystkich gałęzi roboczych do `main` (`8923c80`):

| Wymaganie | Opis wymagania | Sposób realizacji w systemie | Status |
|---|---|---|---|
| **R1** | Wybór budynku lub kampusu uczelni | Lista 28 lokalizacji uczelni w Rzeszowie (`universities.json`), wyszukiwanie i walidacja `location_id` w `generate_recommendations()`. | Spełnione |
| **R2** | Określenie wag preferencji otoczenia | Obsługa całkowitych wag z zakresu `1–3` dla 4 kryteriów (`university`, `shop`, `bus_stop`, `park`) z walidacją typów i zakresu (`VALIDATION_ERROR` dla błędnych wag). | Spełnione |
| **R3** | Czas dojścia pieszo i filtr maksymalnego czasu | Obliczanie odległości wzorem Haversine, przeliczanie na czas marszu przy prędkości `4,5 km/h` (`75 m/min`), odrzucanie obszarów powyżej `max_walk_time_minutes` (`15`, `30`, `45` min lub brak limitu) oraz zwracanie statusu `NO_MATCHES` bez błędu aplikacji. | Spełnione |
| **R4** | Ranking do 3 najlepszych okolic | Deterministyczne sortowanie kluczem `(-score, area_id)` i zwracanie maksymalnie `3` obszarów z punktacją `0–100` oraz prezentacja kół 500 m na mapie (zgodność środków kół z danymi sprawdzono wzrokowo). | Spełnione |
| **R5** | Uzasadnienie ocen i ograniczeń | Generowanie pola `justification` oraz stałego zastrzeżenia `disclaimer` o liczeniu odległości w linii prostej od środka koła `500 m` przy `4,5 km/h` (zgodność samej treści uzasadnienia z punktacją ma w `docs/tests.md` status `NOT RUN`). | Częściowo |
| **R6** | Zakres przestrzenny ograniczony do Rzeszowa | Walidacja współrzędnych WGS84 i ograniczenie zbiorów uczelni, usług oraz 25 obszarów wyłącznie do Rzeszowa, bez wymagania danych o ofertach i cenach najmu. | Spełnione |

---

## 4. Wyniki testów, wydajności i jakości

- **Jakość i powtarzalność danych:** Skrypty `check_data.py` (w tym `--test-invalid`: `3/3` próby na błędnych kopiach) oraz `verify_repeatability.py` potwierdziły zgodność schematu oraz identyczność wygenerowanych plików z zestawem referencyjnym w `data/test/repeatability-reference/` (`500` usług i `28` lokalizacji uczelni).
- **Testy automatyczne logiki i walidacji (`docs/tests.md`):** Po scaleniu wszystkich gałęzi roboczych do `main` uruchomiono pełen zestaw **51 testów automatycznych (`51/51 PASS`)**, obejmujących wczytywanie i walidację plików JSON, odrzucanie niepoprawnych współrzędnych, zduplikowanych `id`, błędnych wag spoza zakresu `1–3` i nieobsługiwanych limitów czasu, determinizm rankingu, czas marszu dla `4,5 km/h` (`75 m/min`) oraz zgodność wzoru punktacji z obliczeniami ręcznymi (`tests/test_weight_scoring.py`).
- **Ręczne sprawdzenie interfejsu Streamlit:** Weryfikacja działania `app.py` potwierdziła poprawne generowanie kart rankingu TOP 3, wyświetlanie mapy z kołami o promieniu `500 m`, czyszczenie wyników przy zmianie parametrów, wyświetlanie zastrzeżenia o linii prostej oraz komunikat o braku dopasowań (np. dla WSIiZ przy limicie `15` minut). Funkcja eksportu rankingu do pliku nie istnieje (`U09: NOT RUN`).
- **Pomiar niefunkcjonalny:** **NOT RUN** — w zespole nie uzgodniono jeszcze docelowego kryterium akceptacji czasu odpowiedzi dla całego przepływu; w repozytorium znajduje się skrypt `scripts/benchmark_recommendation.py` przeznaczony do pomiaru wydajności silnika.

---

## 5. Ograniczenia obecnego rozwiązania i kierunki rozwoju

### Zidentyfikowane ograniczenia
1. **Odległość w linii prostej (Haversine):** System mierzy odległość w linii prostej od środka okręgu o promieniu `500 m` i szacuje czas marszu przy stałej prędkości `4,5 km/h` (`75 m/min`), bez uwzględniania rzeczywistej sieci chodników, przejść dla pieszych ani barier terenowych (np. Wisłok, tory kolejowe).
2. **Nazwy obszarów a pole `district`:** Etykiety `name` w `config/residential-areas.json` zostały sprawdzone w OpenStreetMap przez odwrotne geokodowanie środków obszarów (`docs/area-name-audit.md`), natomiast `id`, `district` i współrzędne pozostały bez zmian. Etykiety mają charakter orientacyjny (nie wyznaczają granic osiedla ani koła `500 m`) i w części przypadków nie pokrywają się z nazwą w polu `district` (np. etykieta *Lubicz (Staromieście)* przy `district: Miłocin`).
3. **Uproszczona agregacja usług i brak danych rynkowych:** Ocena każdego kryterium bazuje na odległości do **najbliższego** pojedynczego obiektu danej kategorii, bez uwzględniania zagęszczenia usług, rozkładów jazdy komunikacji miejskiej czy aktualnych ofert i cen najmu.
4. **Statyczny zrzut danych OSM:** Dane pochodzą z pobrania z Overpass API (licencja ODbL), zawierają znane braki w polach opcjonalnych (`21` usług bez nazwy źródłowej, `387` usług bez pełnego adresu) i wymagają ręcznego uruchomienia `scripts/prepare_data.py` w celu aktualizacji.

### Proponowane kierunki dalszego rozwoju
- Integracja z silnikiem wyznaczania tras pieszych (np. OSRM / OpenRouteService) w celu liczenia rzeczywistego czasu przejścia chodnikami.
- Rozstrzygnięcie w zespole ujednolicenia pola `district` względem etykiet z `docs/area-name-audit.md` oraz dodanie automatycznego testu zgodności treści `justification` z punktacją (`R5`).
- Rozszerzenie modelu danych o średnie ceny najmu pokoi i kawalerek w poszczególnych osiedlach Rzeszowa oraz rozkład jazdy komunikacji miejskiej (ZTM Rzeszów).

---

## 6. Wnioski końcowe
Zrealizowany system w pełni odpowiada na zdefiniowany problem decyzyjny studentów poszukujących mieszkania w Rzeszowie w zakresie analizy odległości w linii prostej i wielokryterialnej oceny otoczenia. Zastosowanie lekkiej architektury opartej na plikach JSON, bibliotece standardowej Pythona w silniku obliczeniowym oraz interfejsie Streamlit pozwoliło osiągnąć pełną powtarzalność wyników oraz przejrzystość prezentacji rekomendacji, przy jednoczesnym zachowaniu jawnie udokumentowanych uproszczeń i ograniczeń.
