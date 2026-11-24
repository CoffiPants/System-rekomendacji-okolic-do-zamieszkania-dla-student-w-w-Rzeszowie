# Raport końcowy projektu — Laboratorium 8

## 1. Problem i użytkownik
Studenci podejmujący naukę w Rzeszowie potrzebują narzędzia wspierającego wybór okolicy zamieszkania dopasowanej do miejsca zajęć (budynku lub kampusu uczelni), maksymalnego akceptowalnego czasu dojścia pieszo oraz indywidualnych wag preferencji dotyczących infrastruktury miejskiej: sklepów (`shop`), przystanków autobusowych (`bus_stop`) i terenów zielonych (`park`).

System został zaprojektowany jako lekka aplikacja analityczna w języku **Python** z interfejsem **Streamlit**, pracująca in-memory na plikach **JSON** i **CSV** (zgodnie z decyzją `./decisions/001-storage.md`). Szczegółowy opis wymagań funkcjonalnych (**R1–R6**) znajduje się w [Opisie problemu](./problem.md).

### Trzy najważniejsze stwierdzenia o projekcie
1. **System realizuje deterministyczne rekomendacje TOP 3 dla 25 obszarów w Rzeszowie:**  
   - *Dowód:* Funkcja `generate_recommendations()` w `scripts/recommendation_engine.py`, interfejs `../app.py` (wraz z eksportem rankingu TOP 3 do CSV) oraz wynik `51/51 PASS` w [Planie i wynikach testów](./tests.md), w tym testy punktacji (`tests/test_weight_scoring.py`) i walidacji żądań (`tests/test_request_validation.py`).  
   - *Granica wnioskowania:* Wyniki dotyczą wyłącznie 25 zdefiniowanych obszarów (promień `500 m`), odległości w linii prostej przy prędkości `4,5 km/h` (`75 m/min`) oraz statycznego zbioru danych bez aktualnych ofert czy cen najmu.
2. **Walidacja danych i żądań chroni aplikację przed błędnymi wejściami i brakami w plikach:**  
   - *Dowód:* Moduł `scripts/data_validation.py`, skrypty kontroli/audytu i powtarzalności (`scripts/check_data.py`, `scripts/audit_data.py`, `scripts/verify_repeatability.py`) oraz testy w `tests/test_data_validation.py` i `tests/test_request_validation.py` (`51/51 PASS`).  
   - *Granica wnioskowania:* Kontrole weryfikują schemat, współrzędne WGS84, unikalność `id`, wagi (`1–3`) i limity czasu (`15`, `30`, `45` lub brak limitu), ale nie gwarantują pełności opcjonalnych pól źródłowych OSM (np. braków adresów czy nazw źródłowych).
3. **Część obszarów weryfikacji jakości wymaga dalszych prac w zespole:**  
   - *Dowód:* Zapisy w [Planie i wynikach testów](./tests.md) oraz w [Audycie nazw obszarów](./area-name-audit.md) (pomiar niefunkcjonalny ma status `NOT RUN`, zgodność treści `justification` z punktacją w `R5` ma status `NOT RUN`, a etykiety nazw obszarów mają charakter orientacyjny).  
   - *Granica wnioskowania:* Brak pomiaru niefunkcjonalnego dla całego przepływu oznacza, że nie oceniono jeszcze czasu odpowiedzi pod obciążeniem ani na innych środowiskach niż testowane lokalnie.

---

## 2. Zakres wykonany
Prace zrealizowano w repozytorium GitHub z użyciem gałęzi tematycznych i przeglądów kodu (*Pull Requests*) w następujących etapach:
- **Lab 1–3 (Problem i dane):** Pozyskanie danych przestrzennych z Overpass API (OpenStreetMap), przetwarzanie danych (`scripts/prepare_data.py`), skrypt kontroli i audytu (`scripts/check_data.py`, `scripts/audit_data.py`) oraz weryfikacja powtarzalności (`scripts/verify_repeatability.py`).
- **Lab 4 (Eksperymenty):** Porównanie metod oceny obszarów — m.in. Weighted Scoring względem podejść sąsiedztwa i KNN (`scripts/compare_methods.py`, `scripts/knn_recommender.py`, `scripts/compare_knn_weighted.py`, `scripts/benchmark_knn_weighted.py`, `../results/lab4/`, opisane w [Eksperymentach](./experiment.md)).
- **Lab 5–8 (Architektura, MVP, testy i finalizacja):** Projekt architektury (`./architecture.md`), implementacja silnika rekomendacji (`scripts/recommendation_engine.py`), walidacji i testów automatycznych (`scripts/data_validation.py`, `tests/`), interfejsu Streamlit z eksportem CSV (`../app.py`, `../.streamlit/config.toml`), przewodnika użytkownika (`./user-guide.md`), audytu nazw obszarów (`./area-name-audit.md`), scenariusza prezentacji (`./presentation.md`) oraz niniejszego raportu końcowego.

Szczegóły wdrożenia i konfiguracji środowiska opisuje [Dokumentacja wdrożenia](./implementation.md), a bieżące zadania i uwagi są śledzone w otwartych *Issues* na GitHubie (m.in. w Issue #10).

Weryfikacja wymagań funkcjonalnych (**R1–R6**) na podstawie wyników z [Planu i wyników testów](./tests.md):

| Wymaganie | Opis wymagania | Sposób realizacji w systemie | Status |
|---|---|---|---|
| **R1** | Wybór budynku lub kampusu uczelni | Lista 28 lokalizacji uczelni w Rzeszowie (`../data/processed/universities.json`), wyszukiwanie i walidacja `location_id` w `generate_recommendations()`. | Spełnione |
| **R2** | Określenie wag preferencji otoczenia | Obsługa wag całkowitych z zakresu `1–3` dla 4 kryteriów (`university`, `shop`, `bus_stop`, `park`) z walidacją typów i zakresu. | Spełnione |
| **R3** | Czas dojścia pieszo i filtr maksymalnego czasu | Obliczanie odległości wzorem Haversine, przeliczanie na czas marszu przy prędkości `4,5 km/h` (`75 m/min`), filtrowanie wg `max_walk_time_minutes` (`15`, `30`, `45` min lub brak limitu) oraz zwracanie statusu `NO_MATCHES` bez błędu aplikacji. | Spełnione |
| **R4** | Ranking do 3 najlepszych okolic | Deterministyczne sortowanie kluczem `(-score, area_id)` i zwracanie maksymalnie `3` obszarów z punktacją `0–100` oraz prezentacja kół `500 m` na mapie. | Spełnione |
| **R5** | Uzasadnienie ocen i ograniczeń | Generowanie pola `justification` oraz stałego zastrzeżenia `disclaimer` o liczeniu odległości w linii prostej od środka koła `500 m` przy `4,5 km/h` (zgodność treści uzasadnienia z punktacją ma w `./tests.md` status `NOT RUN`). | Częściowo |
| **R6** | Zakres przestrzenny ograniczony do Rzeszowa | Zbiory danych przygotowano dla Rzeszowa; ranking nie wymaga danych o ofertach ani cenach najmu. | Spełnione |

---

## 3. Dane
System korzysta z danych geograficznych dla Rzeszowa pobranych z OpenStreetMap (Overpass API) oraz zdefiniowanych obszarów mieszkalnych:
- **Lokalizacje uczelni:** `28` rekordów w `../data/processed/universities.json` (m.in. Politechnika Rzeszowska, Uniwersytet Rzeszowski, WSIiZ, WSPiA; `26` budynków i `2` kampusy).
- **Punkty usługowe:** `500` rekordów w `../data/processed/services.json` w kategoriach `shop` (`274`), `bus_stop` (`185`) oraz `park` (`41`).
- **Obszary mieszkalne:** `25` obszarów o promieniu `500 m` w `20` osiedlach Rzeszowa zdefiniowanych w `../config/residential-areas.json`. Etykiety nazw obszarów mają charakter orientacyjny i mogą różnić się od pola `district` (szczegóły w [Audycie nazw obszarów](./area-name-audit.md)).

Szczegółowy opis zbiorów oraz procedur przetwarzania znajduje się w dokumentach:
- [Opis danych](./data.md)
- [Słownik danych](./data-dictionary.md)
- [Przetwarzanie, kontrole i powtarzalność](./processing.md)

---

## 4. Metoda i architektura
Aplikacja opiera się na metodzie **Weighted Scoring** (przyjętej jako wariant bazowy rekomendacji), oceniającej każdy obszar mieszkalny na podstawie odległości w linii prostej (wzór Haversine'a) od środka okręgu o promieniu `500 m` do wybranej lokalizacji uczelni oraz najbliższych obiektów kategorii `shop`, `bus_stop` i `park`, z uwzględnieniem wag `1–3` oraz limitu czasu marszu przy stałej prędkości `4,5 km/h` (`75 m/min`).

Architektura dzieli system na warstwę danych i konfiguracji (`../data/`, `../config/`), warstwę logiki analitycznej i walidacji (`scripts/recommendation_engine.py`, `scripts/data_validation.py`, `scripts/prepare_data.py`, `scripts/check_data.py`, `scripts/audit_data.py`, `scripts/verify_repeatability.py`) oraz interfejs użytkownika Streamlit (`../app.py`), komunikujące się poprzez publiczną funkcję `generate_recommendations(request, engine=None)`.

Szczegóły analizy porównawczej metod oraz wyboru rozwiązania opisują [Eksperymenty](./experiment.md), [ADR 001 — Wybór formatu plików JSON/CSV](./decisions/001-storage.md) oraz [Architektura systemu](./architecture.md).

---

## 5. Wyniki i ocena
- **Jakość i powtarzalność danych:** Skrypty `scripts/check_data.py` (w tym `--test-invalid`: `3/3` testy) oraz `scripts/verify_repeatability.py` potwierdziły zgodność schematu i współrzędnych oraz identyczność wyników względem zestawu referencyjnego w `../data/test/repeatability-reference/`.
- **Testy automatyczne:** W repozytorium znajduje się zestaw **51 testów automatycznych** (`tests/test_data_validation.py`, `tests/test_request_validation.py`, `tests/test_recommendation_engine.py`, `tests/test_weight_scoring.py`), które przeszły w komplecie (`51/51 PASS` — patrz [Plan i wyniki testów](./tests.md)).
- **Eksperymenty porównawcze (Lab 4):** Porównanie metod (w tym Weighted Scoring oraz KNN) opisane w [Eksperymentach](./experiment.md) wykazało zbieżność najlepszych wskazań dla analizowanych profili preferencji przy krótszym czasie wykonania Weighted Scoring w przeprowadzonym benchmarku.
- **Stan weryfikacji UI i wydajności:** Ręczne sprawdzenie interfejsu Streamlit potwierdziło działanie rankingu TOP 3, eksportu rankingu do CSV (`Pobierz ranking TOP 3 (CSV)`), mapy z okręgami `500 m` oraz obsłużenie przypadku braku dopasowań (`WSIiZ, Sucharskiego 2`, limit `15 min` → `NO_MATCHES`). Pomiar niefunkcjonalny całego przepływu ma w `./tests.md` status `NOT RUN` (w repozytorium znajduje się `scripts/benchmark_recommendation.py`).

---

## 6. Użycie i odtworzenie
- **Wersja prezentowana:** Aktualny stan gałęzi `main` po scaleniu PR #21 (`ed0366c`), z tagiem wersji `lab8-demo` (do aktualizacji po zakończeniu ostatnich prac zgodnie ze [Scenariuszem prezentacji](./presentation.md)).
- **Dokumentacja uruchomieniowa:** Instrukcja uruchomienia środowiska, skryptów i aplikacji Streamlit znajduje się w [README](../README.md), w [Przewodniku użytkownika](./user-guide.md) oraz w [Dokumentacji wdrożenia](./implementation.md).
- **Uruchomienie testów:**
  ```bash
  python -m unittest discover -s tests -v
  ```
---

## 7. Ograniczenia i kierunki rozwoju
- **Odległość w linii prostej i stała prędkość marszu:** System liczy dystans w linii prostej (Haversine) od środka koła `500 m` i przyjmuje `4,5 km/h` (`75 m/min`), pomijając rzeczywistą sieć chodników, przejścia dla pieszych oraz bariery terenowe (np. rzekę Wisłok czy linie kolejowe).
- **Uproszczona ocena usług i brak danych rynkowych:** Liczony jest najbliższy obiekt danej kategorii bez zagęszczenia usług, rozkładów jazdy komunikacji miejskiej ani aktualnych ofert i cen najmu.
- **Orientacyjne etykiety obszarów i statyczne dane OSM:** Etykiety obszarów względem pola `district` mają charakter orientacyjny (`./area-name-audit.md`), a dane z Overpass API wymagają ręcznego odświeżenia skryptem `scripts/prepare_data.py`.
- **Kierunki rozwoju:** Integracja z silnikiem wyznaczania tras pieszych (np. OSRM), uzupełnienie danych o ceny najmu i rozkłady jazdy, dodanie automatycznego testu zgodności treści `justification` z punktacją (`R5`), wykonanie uzgodnionego pomiaru niefunkcjonalnego oraz automatyzacja aktualizacji danych.

---

## 8. Wkład zespołu i źródła

### Podział prac i rezultaty członków zespołu

| Osoba | Główne rezultaty i PR / pliki |
|---|---|
| **Paulina Michalska** | Weryfikacja powtarzalności przetwarzania danych (`scripts/verify_repeatability.py`), dokumentacja architektoniczna i projektowa (`./architecture.md`, `./decisions/001-storage.md`, `./implementation.md`, `./report.md`, `./presentation.md`, aktualizacje `./problem.md` i `../README.md`) — m.in. PR #11, #14, #18. |
| **Serhii Popovych** | Przetwarzanie danych (`scripts/prepare_data.py`), silnik rekomendacji (`scripts/recommendation_engine.py`), testy silnika (`tests/test_recommendation_engine.py`), eksperymenty i benchmarki (`scripts/compare_methods.py`, `scripts/knn_recommender.py`, `scripts/compare_knn_weighted.py`, `scripts/benchmark_knn_weighted.py`, `./experiment.md`) oraz audyt nazw obszarów (`./area-name-audit.md`) — m.in. PR #16. |
| **Dana Stadnyk** | Skrypty kontroli i audytu danych (`scripts/check_data.py`, `scripts/audit_data.py`), benchmark rekomendacji (`scripts/benchmark_recommendation.py`), interfejs użytkownika w Streamlit (`../app.py`, `../.streamlit/config.toml`) z mapą i eksportem rankingu TOP 3 do CSV oraz [Przewodnik użytkownika](./user-guide.md) — m.in. PR #20. |
| **Valentyna Boksha** | Pozyskanie danych z Overpass API (Lab 1–3, `../data/processed/services.json`, `../data/processed/universities.json`, `./problem.md`, `./data.md`), walidacja i testy (`scripts/data_validation.py`, `tests/test_data_validation.py`, `tests/test_request_validation.py`, `tests/test_weight_scoring.py`, `./tests.md`), przegląd architektury (`Issue #8`) oraz przegląd kodu — m.in. PR #15, #17, #19, #21. |

Potwierdzeniem działania całości na prezentowanej wersji jest uruchomienie `python -m unittest discover -s tests -v` — `51/51 PASS` na gałęzi `main` (w tym `44` testy z zakresu walidacji, żądań i punktacji wag).

### Audyt gotowości Lab 1–8 (lista kontrolna)

| Element gotowości | Stan | Uwagi |
|---|---|---|
| Układ 8 rozdziałów raportu końcowego i linki względne | Gotowe | Zrealizowane w `./report.md` (z uzupełnieniem pomiaru po stronie Serhiego w kolejnym etapie). |
| Trzy główne stwierdzenia (dowód + granica wnioskowania) | Gotowe | Ujęte w rozdziale 1 `./report.md`. |
| Weryfikacja wymagań R1–R6 zgodna z `./tests.md` | Gotowe | R1–R4 i R6 spełnione; R5 częściowo (`justification` bez testu zgodności z punktacją). |
| Testy automatyczne na gałęzi `main` | Gotowe | `51/51 PASS` (`python3 -m unittest discover -s tests -v`). |
| Eksport wyników rankingu do CSV i instrukcja użytkownika | Gotowe | Przycisk eksportu CSV w `../app.py` oraz `./user-guide.md` dodane w PR #20. |
| Scenariusz prezentacji i tag wersji końcowej | Gotowe | `./presentation.md` zaktualizowany; tag `lab8-demo` |

### Źródła danych i licencje
- **OpenStreetMap Contributors** — *OpenStreetMap (Rzeszów, dane pobierane przez Overpass API)*, [https://www.openstreetmap.org/](https://www.openstreetmap.org/), dostęp: 2026-11; licencja: **Open Database License (ODbL)** (`© OpenStreetMap contributors`).
- **Streamlit** — *Streamlit Documentation*, [https://docs.streamlit.io/](https://docs.streamlit.io/), dostęp: 2026-11.
- **Folium** — *Folium Documentation*, [https://python-visualization.github.io/folium/](https://python-visualization.github.io/folium/), dostęp: 2026-11.
- **Metody analityczne i obliczanie odległości** — *Weighted scoring* (wielokryterialna średnia ważona znormalizowanych ocen `0–100`), *k-nearest neighbors (KNN)* w eksperymencie Lab 4 (`./experiment.md`) oraz formuła *Haversine* dla odległości sferycznej w linii prostej.

### Wykorzystanie narzędzi AI
Podczas prac nad dokumentacją, kodem i testami wykorzystywano asystentów AI (m.in. asystent konwersacyjny AI do porządkowania treści, sprawdzania spójności opisów oraz wsparcia przy pisaniu i przeglądzie dokumentacji i kodu). Wszystkie zmiany były weryfikowane przez zespół na podstawie kodu, danych wejściowych oraz wyników testów automatycznych i ręcznych.