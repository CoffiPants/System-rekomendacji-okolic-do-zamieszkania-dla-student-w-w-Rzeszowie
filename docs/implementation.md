# Dokumentacja implementacji — Laboratorium 6

## 1. Cel etapu i zakres wdrożenia
Celem Laboratorium 6 było przeniesienie projektu architektonicznego (`docs/architecture.md`) do działającej implementacji systemu rekomendacji okolic mieszkalnych dla studentów w Rzeszowie. System realizuje warstwę analityczną i walidacyjną w języku **Python** w oparciu o przetworzone zbiory **JSON** oraz konfigurację obszarów mieszkalnych, przygotowując kompletny silnik rekomendacji do integracji z warstwą prezentacji (**Streamlit**).

---

## 2. Struktura kodu i organizacja modułów

Projekt zachowuje wyraźny podział na warstwę danych, warstwę przetwarzania i audytu oraz warstwę silnika rekomendacji i testów:

* `config/residential-areas.json` – konfiguracja 25 obszarów mieszkalnych o promieniu 500 m w 20 osiedlach Rzeszowa.
* `config/university-selection.json` – definicja i kryteria wyboru budynków oraz kampusów uczelni.
* `data/raw/` – surowe zbiory pobrane z Overpass API (`universities.json`, `sample.json`).
* `data/processed/` – oczyszczone zbiory wejściowe (`universities.json` – 28 lokalizacji, `services.json` – 500 punktów usługowych).
* `data/test/` – raporty walidacji jakości, testów błędnych danych i powtarzalności (`quality-report.json`, `audit-report.json`, `invalid-tests-report.json`, `repeatability-report.json`).
* `scripts/prepare_data.py` – czyszczenie, normalizacja i sortowanie danych OSM do `data/processed/`.
* `scripts/check_data.py` oraz `scripts/audit_data.py` – walidacja spójności schematu, współrzędnych WGS84 i pokrycia przestrzennego.
* `scripts/verify_repeatability.py` – weryfikacja determinizmu przetwarzania względem wzorca w `data/test/repeatability-reference/`.
* `scripts/compare_methods.py` – eksperyment porównawczy metod oceny obszarów z Laboratorium 4 (`results/lab4/`).
* `scripts/recommendation_engine.py` – główny silnik rekomendacji (klasa `RecommendationEngine`, obliczenia odległości Haversine, filtrowanie czasu dojścia, normalizacja punktacji i generowanie uzasadnień).
* `scripts/benchmark_recommendation.py` – skrypt pomiaru wydajności i czasu wykonania silnika rekomendacji.
* `tests/test_recommendation_engine.py` – zestaw testów jednostkowych i brzegowych weryfikujących silnik rekomendacji.
* `docs/` – kompletna dokumentacja projektowa (Lab 1 – Lab 8).

---

## 3. Realizacja wymagań funkcjonalnych (R1–R6) w kodzie

Każde z wymagań specyfikacji problemu (`docs/problem.md`) zostało zaimplementowane w module `scripts/recommendation_engine.py`:

1. **R1 — Wybór budynku lub kampusu uczelni:**
   * Metoda `RecommendationEngine._location(location_id)` wyszukuje wybraną lokalizację po kluczu `id` w zbiorze `data/processed/universities.json` (28 lokalizacji w Rzeszowie). W przypadku podania nieistniejącego identyfikatora zgłaszany jest wyjątek `ValueError` z czytelnym komunikatem.
2. **R2 — Wagi preferencji otoczenia:**
   * Metoda `recommend(..., weights=...)` przyjmuje słownik wag dla czterech kryteriów: `"university"`, `"shop"`, `"bus_stop"`, `"park"` (domyślnie `DEFAULT_WEIGHTS = {"university": 3.0, "shop": 2.0, "bus_stop": 2.0, "park": 2.0}`). Walidacja odrzuca nieznane klucze, wartości ujemne, typy logiczne oraz sytuację, gdy suma wszystkich wag wynosi `0`.
3. **R3 — Obliczanie czasu dojścia i filtr maksymalnego czasu:**
   * Funkcja `distance_m(a_lat, a_lon, b_lat, b_lon)` oblicza odległość w linii prostej wzorem Haversine (w metrach, przy promieniu Ziemi `6 371 000 m`).
   * Szacowany czas marszu do uczelni wyliczany jest przy stałej prędkości pieszego `WALKING_SPEED_M_PER_MINUTE = 80.0` m/min (`4,8 km/h`): `walk_minutes = distances["university"] / 80.0`.
   * Parametr `max_walk_minutes` odrzuca każdy obszar, dla którego `walk_minutes > max_walk_minutes`. Gdy żaden obszar nie spełnia limitu czasu, metoda `recommend()` zwraca pustą listę `[]` bez przerywania działania programu.
4. **R4 — Ranking do 3 najlepszych okolic:**
   * Zakwalifikowane obszary są sortowane deterministycznie kluczem `(-row["score"], row["area_id"])` (malejąco według oceny punktowej `0–100`, a przy identycznym wyniku rosnąco według identyfikatora `area_id`), po czym zwracanych jest maksymalnie `top_n = 3` najlepszych obszarów z przypisanymi pozycjami `rank` (`1..3`).
5. **R5 — Uzasadnienie ocen i ograniczeń:**
   * Każdy element rankingu zawiera pole `reason` generowane na podstawie 2 najwyżej ocenionych kryteriów o dodatniej wadze wraz z konkretnymi odległościami w metrach (np. `"przystanek: 140 m; sklep: 210 m"`), a moduł dokumentuje orientacyjny charakter pomiaru w linii prostej od środka obszaru.
6. **R6 — Zakres przestrzenny ograniczony do Rzeszowa:**
   * Dane wejściowe oraz siatka 25 obszarów w `config/residential-areas.json` obejmują wyłącznie granice administracyjne Rzeszowa.
---

## 4. Szczegóły implementacji silnika `RecommendationEngine`

### 4.1. Inicjalizacja i walidacja danych wejściowych
* Klasa `RecommendationEngine` może zostać utworzona bezpośrednio z list w pamięci (`__init__(services, locations, areas)`) lub wczytana z dysku metodą klasową `RecommendationEngine.from_files(services_path, locations_path, areas_path)`.
* Metoda `_validate_records()` weryfikuje, czy przekazane zbiory są niepustymi listami słowników, posiadają wymagane klucze (`latitude`, `longitude`, oraz odpowiednio `category`, `id`, `name`, `district`), a wszystkie współrzędne mieszczą się w poprawnym zakresie geograficznym WGS84 (`-90..90` dla szerokości oraz `-180..180` dla długości) i są skończonymi liczbami.
* Podczas inicjalizacji usługi są indeksowane według kategorii (`CATEGORIES = ("shop", "bus_stop", "park")`), co przyspiesza wyszukiwanie najbliższego punktu z każdej kategorii dla każdego obszaru.

### 4.2. Normalizacja odległości i obliczanie punktacji
* Odległości w metrach do uczelni oraz najbliższych usług w kategoriach `shop`, `bus_stop` i `park` są przeliczane na ocenę cząstkową `0–100 pkt` przez funkcję `score(distance, limit)`:
  $$\text{score}(d, L) = 100.0 \cdot \max\left(0.0,\; 1.0 - \frac{d}{L}\right)$$
* Zastosowane progi odniesienia (`DEFAULT_LIMITS_M`) wynoszą:
  * `university`: **3000.0 m**,
  * `shop`: **1000.0 m**,
  * `bus_stop`: **600.0 m**,
  * `park`: **1500.0 m**.
* Wynik końcowy `total_score` jest średnią ważoną ocen cząstkowych zaokrągloną do 4 miejsc po przecinku.

### 4.3. Struktura pojedynczego rekordu wyjściowego
Metoda `recommend()` zwraca listę słowników, gdzie każdy rekord zawiera:
* `rank` (`int`): pozycja w rankingu (`1`, `2` lub `3`),
* `area_id` (`str`), `area_name` (`str`), `district` (`str`): identyfikator i nazwa obszaru oraz osiedla,
* `score` (`float`): końcowy wynik punktowy (`0.0–100.0`),
* `walk_distance_m` (`float`): odległość w linii prostej do uczelni w metrach,
* `walk_time_minutes` (`float`): szacowany czas dojścia w minutach (`80 m/min`),
* `distances_m` (`dict[str, float]`): odległości w metrach dla kluczy `university`, `shop`, `bus_stop`, `park`,
* `scores` (`dict[str, float]`): oceny cząstkowe (`0–100`) dla każdego z 4 kryteriów,
* `reason` (`str`): tekstowe uzasadnienie wskazujące 2 najmocniejsze kryteria lokalizacji.

---

## 5. Wymagania środowiskowe i uruchomienie projektu

### Wymagania wstępne
* **Python 3.10** lub nowszy (wykorzystywana jest wyłącznie biblioteka standardowa Pythona: `json`, `math`, `pathlib`, `unittest` — brak zewnętrznych zależności dla silnika rekomendacji).

### Instrukcja uruchomienia krok po kroku
1. Sklonowanie repozytorium i przejście do katalogu projektu:
   * `git clone https://github.com/CoffiPants/System-rekomendacji-okolic-do-zamieszkania-dla-student-w-w-Rzeszowie.git`
   * `cd System-rekomendacji-okolic-do-zamieszkania-dla-student-w-w-Rzeszowie`
2. Opcjonalne ponowne wygenerowanie i weryfikacja danych przetworzonych:
   * `python3 scripts/prepare_data.py`
   * `python3 scripts/check_data.py`
3. Uruchomienie testów jednostkowych silnika rekomendacji:
   * `python3 -m unittest discover -s tests`
4. Uruchomienie pomiaru wydajności (benchmarku):
   * `python3 scripts/benchmark_recommendation.py`
5. Przykładowe wywołanie silnika w kodzie Pythona:
   ```python
   from scripts.recommendation_engine import RecommendationEngine

   engine = RecommendationEngine.from_files(
       "data/processed/services.json",
       "data/processed/universities.json",
       "config/residential-areas.json",
   )
   top3 = engine.recommend(
       location_id="way/208515700",
       weights={"university": 3, "shop": 2, "bus_stop": 3, "park": 1},
       max_walk_minutes=30,
   )
    ```

---

## 6. Weryfikacja poprawności implementacji (Testy i Benchmark)
* **Testy jednostkowe i brzegowe (`tests/test_recommendation_engine.py`):** Weryfikują poprawność wzoru Haversine, obsługę błędnych współrzędnych i nieistniejących uczelni (`ValueError`), działanie filtra `max_walk_minutes` (w tym zwrot pustej listy `[]` przy zbyt restrykcyjnym limicie), deterministyczne rozstrzyganie remisów po `area_id` oraz generowanie pola `reason`.
* **Testy wydajności (`scripts/benchmark_recommendation.py`):** Mierzą czas inicjalizacji silnika z plików JSON oraz czas pojedynczego zapytania `recommend()` dla 25 obszarów i 500 usług, potwierdzając natychmiastową pracę obliczeń in-memory.
* **Status integracji:** Warstwa analityczna i testy silnika są w pełni zaimplementowane; moduł interfejsu graficznego Streamlit (`app.py`) oczekuje na finalne scalenie gałęzi UI z gałęzią główną `main`.