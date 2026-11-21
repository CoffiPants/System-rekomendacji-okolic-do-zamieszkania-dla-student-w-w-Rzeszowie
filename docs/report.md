# Raport końcowy projektu — Laboratorium 8

## 1. Podsumowanie celu i zakresu systemu
Celem projektu było zaprojektowanie, zaimplementowanie i przetestowanie **systemu rekomendacji okolic zamieszkania dla studentów w Rzeszowie**. Aplikacja wspiera studentów w wyborze lokalizacji mieszkania dopasowanej do miejsca odbywania zajęć oraz indywidualnych preferencji dotyczących infrastruktury miejskiej (sklepów, przystanków autobusowych oraz terenów zielonych), przy jednoczesnym uwzględnieniu maksymalnego akceptowalnego czasu dojścia pieszo na uczelnię.

System zrealizowano w języku **Python** jako modułową aplikację analityczną połączoną z interaktywnym interfejsem użytkownika w bibliotece **Streamlit**, pracującą bezpośrednio na ustrukturyzowanych plikach **JSON** i **CSV** (zgodnie z decyzją architektoniczną `docs/decisions/001-storage.md`).

---

## 2. Przebieg prac projektowych i podział ról w zespole

Prace podzielono na spójne etapy inżynierskie realizowane w repozytorium GitHub z wykorzystaniem gałęzi tematycznych i przeglądów kodu (*Pull Requests*):

1. **Analiza problemu i danych (Lab 1–3):**
   * Zdefiniowano wymagania funkcjonalne (**R1–R6**) i kryteria jakości w `docs/problem.md`.
   * Pobrano dane przestrzenne z Overpass API (OpenStreetMap) oraz przygotowano potok przetwarzania (`scripts/prepare_data.py`), uzyskując oczyszczone zbiory: **28 lokalizacji uczelni** (`data/processed/universities.json`), **500 punktów usługowych** (`data/processed/services.json`) oraz **25 obszarów mieszkalnych** o promieniu 500 m w 20 osiedlach Rzeszowa (`config/residential-areas.json`).
   * Potwierdzono jakość, kompletność i determinizm przetwarzania (`scripts/check_data.py`, `scripts/audit_data.py`, `scripts/verify_repeatability.py`).
2. **Eksperymenty badawcze (Lab 4):**
   * Porównano metody oceny obszarów (Weighted Scoring oraz podejścia sąsiedztwa) pod kątem stabilności rankingów i wrażliwości na zmianę wag preferencji (`scripts/compare_methods.py`, `results/lab4/`).
3. **Projekt architektury i implementacja (Lab 5–6):**
   * **Paulina Michalska:** Opracowanie dokumentacji architektury (`docs/architecture.md`), kontraktu interfejsu, modelu logicznego/fizycznego danych, dokumentacji wdrożeniowej (`docs/implementation.md`) oraz raportu końcowego (`docs/report.md`).
   * **Serhii:** Implementacja silnika rekomendacji (`scripts/recommendation_engine.py`), testów jednostkowych (`tests/test_recommendation_engine.py`) oraz skryptu pomiaru wydajności (`scripts/benchmark_recommendation.py`).
   * **Dana:** Budowa interaktywnego interfejsu użytkownika w Streamlit (`app.py`), wizualizacja mapy Rzeszowa oraz eksport wyników.
   * **Valentyna:** Walidacja danych wejściowych, testy integracyjne i przypadków brzegowych oraz dokumentacja testów (`docs/tests.md`).

---

## 3. Weryfikacja spełnienia wymagań funkcjonalnych (R1–R6)

| Wymaganie | Opis wymagania | Sposób realizacji w systemie | Status |
|---|---|---|---|
| **R1** | Wybór budynku lub kampusu uczelni | Lista 28 lokalizacji uczelni w Rzeszowie (`universities.json`), wyszukiwanie po `id` w `RecommendationEngine._location()`. | Spełnione |
| **R2** | Określenie wag preferencji otoczenia | Obsługa wag dla 4 kryteriów (`university`, `shop`, `bus_stop`, `park`) z walidacją typów i zakresu. | Spełnione |
| **R3** | Czas dojścia pieszo i filtr maksymalnego czasu | Obliczanie odległości wzorem Haversine, przeliczanie na czas marszu (`80 m/min`), odrzucanie obszarów powyżej `max_walk_minutes` oraz zwracanie pustej listy / statusu braku dopasowań bez błędu aplikacji. | Spełnione |
| **R4** | Ranking do 3 najlepszych okolic | Deterministyczne sortowanie kluczem `(-score, area_id)` i zwracanie maksymalnie `top_n = 3` obszarów z punktacją `0–100`. | Spełnione |
| **R5** | Uzasadnienie ocen i ograniczeń | Generowanie pola `reason` wskazującego 2 najmocniejsze atuty obszaru (odległości w metrach) oraz informacja o liczeniu odległości w linii prostej od środka koła 500 m. | Spełnione |
| **R6** | Zakres przestrzenny ograniczony do Rzeszowa | Walidacja współrzędnych WGS84 i ograniczenie zbiorów uczelni, usług oraz 25 obszarów wyłącznie do granic Rzeszowa. | Spełnione |

---

## 4. Wyniki testów, wydajności i jakości

* **Jakość i powtarzalność danych:** Skrypty `check_data.py` oraz `verify_repeatability.py` potwierdziły `100%` zgodności schematu oraz identyczność wygenerowanych plików z zestawem referencyjnym w `data/test/repeatability-reference/`.
* **Poprawność logiki rekomendacji:** Testy w `tests/test_recommendation_engine.py` zweryfikowały poprawność obliczania odległości Haversine, odrzucanie niepoprawnych danych wejściowych (`ValueError`), działanie filtra `max_walk_minutes` (w tym poprawne zachowanie przy braku dopasowań), deterministyczne rozstrzyganie remisów po `area_id` oraz generowanie uzasadnień.
* **Wydajność obliczeń:** Pomiary wykonane skryptem `scripts/benchmark_recommendation.py` wykazały, że pełna inicjalizacja silnika oraz wygenerowanie rankingu TOP 3 dla 25 obszarów i 500 usług realizowane są w pamięci operacyjnej w czasie pojedynczych milisekund, zapewniając płynną pracę interfejsu Streamlit.
* **Testy interfejsu i integracji:** `[DO UZUPEŁNIENIA PO MERGU UI: wpisać wynik testów end-to-end UI Dany oraz podsumowanie z docs/tests.md Valentyny]`.

---

## 5. Ograniczenia obecnego rozwiązania i kierunki rozwoju

### Zidentyfikowane ograniczenia
1. **Odległość w linii prostej (Euklidesowa / Haversine):** System mierzy odległość w linii prostej od środka okręgu o promieniu 500 m zamiast rzeczywistej długości trasy po sieci chodników i przejść dla pieszych, co w przypadku przeszkód terenowych (np. Wisłok, tory kolejowe) może zaniżać rzeczywisty czas dojścia.
2. **Uproszczona agregacja usług:** Ocena każdego kryterium bazuje na odległości do **najbliższego** pojedynczego obiektu danej kategorii, bez uwzględniania zagęszczenia usług czy różnic cenowych najmu w poszczególnych osiedlach.
3. **Statyczny zrzut danych OSM:** Dane pochodzą z jednorazowego pobrania z Overpass API i wymagają ręcznego uruchomienia `scripts/prepare_data.py` w celu aktualizacji.

### Proponowane kierunki dalszego rozwoju
* Integracja z silnikiem wyznaczania tras pieszych (np. OSRM / OpenRouteService) w celu liczenia rzeczywistego czasu przejścia chodnikami.
* Rozszerzenie modelu danych o średnie ceny najmu pokoi i kawalerek w poszczególnych osiedlach Rzeszowa oraz rozkład jazdy komunikacji miejskiej (ZTM Rzeszów).
* Automatyzacja okresowego odświeżania danych z Overpass API za pomocą harmonogramu GitHub Actions.

---

## 6. Wnioski końcowe
Zrealizowany system w pełni odpowiada na zdefiniowany problem decyzyjny studentów poszukujących mieszkania w Rzeszowie. Zastosowanie lekkiej architektury opartej na plikach JSON, bibliotece standardowej Pythona w silniku obliczeniowym oraz interfejsie Streamlit pozwoliło osiągnąć wysoką szybkość działania, pełną powtarzalność wyników oraz przejrzystość prezentacji rekomendacji.