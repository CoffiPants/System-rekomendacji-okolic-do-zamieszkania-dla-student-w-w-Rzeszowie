# Dokumentacja implementacji — Laboratorium 6

## 1. Cel etapu i zakres wdrożenia

Celem Laboratorium 6 było przeniesienie projektu architektonicznego (`docs/architecture.md`) do działającej implementacji systemu rekomendacji okolic mieszkalnych dla studentów w Rzeszowie.

System realizuje warstwę analityczną i walidacyjną w języku **Python** w oparciu o przetworzone zbiory **JSON** oraz konfigurację obszarów mieszkalnych, a także zintegrowany interfejs użytkownika w technologii **Streamlit**.

---

## 2. Struktura kodu i organizacja modułów

Projekt zachowuje wyraźny podział na warstwę danych, warstwę przetwarzania i audytu oraz warstwę silnika rekomendacji i testów:

- `config/residential-areas.json` – konfiguracja 25 środków obszarów o promieniu 500 m; etykiety `name` wskazują ulicę lub nazwane miejsce najbliższe zapisanym współrzędnym.
- `docs/area-name-audit.md` – lista etykiet i mapy do kontroli każdego z 25 środków.
- `config/university-selection.json` – definicja i kryteria wyboru budynków oraz kampusów uczelni.
- `data/raw/` – surowe zbiory pobrane z Overpass API (`universities.json`, `sample.json`).
- `data/processed/` – oczyszczone zbiory wejściowe (`universities.json` – 28 lokalizacji, `services.json` – 500 punktów usługowych).
- `data/test/` – raporty walidacji jakości, testów błędnych danych i powtarzalności (`quality-report.json`, `audit-report.json`, `invalid-tests-report.json`, `repeatability-report.json`).
- `scripts/prepare_data.py` – czyszczenie, normalizacja i sortowanie danych OSM do `data/processed/`.
- `scripts/check_data.py` oraz `scripts/audit_data.py` – walidacja spójności schematu, współrzędnych WGS84 i pokrycia przestrzennego.
- `scripts/verify_repeatability.py` – weryfikacja determinizmu przetwarzania względem wzorca w `data/test/repeatability-reference/`.
- `scripts/compare_methods.py` – eksperyment porównawczy metod oceny obszarów z Laboratorium 4 (`results/lab4/`).
- `scripts/recommendation_engine.py` – silnik rekomendacji (`RecommendationEngine`) oraz publiczne API `generate_recommendations(request, engine=None)` używane przez aplikację.
- `scripts/benchmark_recommendation.py` – skrypt pomiaru wydajności i czasu wykonania silnika rekomendacji.
- `tests/test_recommendation_engine.py` – zestaw testów jednostkowych i brzegowych weryfikujących silnik rekomendacji.
- `docs/` – dokumentacja projektowa.

---

## 3. Realizacja wymagań funkcjonalnych (R1–R6) w kodzie

Każde z wymagań specyfikacji problemu (`docs/problem.md`) jest realizowane przez `scripts/recommendation_engine.py`. Aplikacja wywołuje publiczną funkcję `generate_recommendations`; metoda `RecommendationEngine.recommend` pozostaje warstwą obliczeniową.

### R1 — Wybór budynku lub kampusu uczelni

Metoda `RecommendationEngine._location(location_id)` wyszukuje wybraną lokalizację po kluczu `id` w zbiorze `data/processed/universities.json` (28 lokalizacji w Rzeszowie).

Warstwa obliczeniowa zgłasza `ValueError` dla nieznanego identyfikatora, a publiczne API zamienia go na odpowiedź `VALIDATION_ERROR` z czytelnym komunikatem.

### R2 — Wagi preferencji otoczenia

Publiczne API `generate_recommendations(request, engine=None)` przyjmuje żądanie ze słownikiem wag dla czterech kryteriów:

- `university`
- `shop`
- `bus_stop`
- `park`

Domyślne wartości dla bezpośredniego wywołania metody obliczeniowej `recommend()`:

`DEFAULT_WEIGHTS = {"university": 3.0, "shop": 2.0, "bus_stop": 2.0, "park": 2.0}`

Interfejs i publiczne API przyjmują wartości całkowite od `1` do `3`. Niższy poziom `RecommendationEngine.recommend` sprawdza typ i nieujemność wag.

### R3 — Obliczanie czasu dojścia i filtr maksymalnego czasu

Funkcja `distance_m(a_lat, a_lon, b_lat, b_lon)` oblicza odległość w linii prostej wzorem Haversine (w metrach, przy promieniu Ziemi `6 371 000 m`).

Szacowany czas marszu do uczelni wyliczany jest przy stałej prędkości pieszego:

`WALKING_SPEED_M_PER_MINUTE = 75.0`

Odpowiada to prędkości `4,5 km/h`.

Obliczenie:

`walk_minutes = distances["university"] / 75.0`

Parametr `max_walk_minutes` odrzuca każdy obszar, dla którego `walk_minutes > max_walk_minutes`.

Gdy żaden obszar nie spełnia limitu czasu, metoda `recommend()` zwraca pustą listę. Publiczne API zamienia ten wynik na odpowiedź ze statusem `NO_MATCHES` i komunikatem dla interfejsu.

### R4 — Ranking do 3 najlepszych okolic

Zakwalifikowane obszary są sortowane deterministycznie kluczem:

`(-row["score"], row["area_id"])`

Sortowanie odbywa się malejąco według oceny punktowej `0–100`, a przy identycznym wyniku rosnąco według identyfikatora `area_id`.

Następnie zwracanych jest maksymalnie `top_n = 3` najlepszych obszarów z przypisanymi pozycjami `rank` (`1..3`).

### R5 — Uzasadnienie ocen i ograniczeń

Każdy element rankingu zawiera pole `justification` generowane na podstawie 2 najwyżej ocenionych kryteriów o dodatniej wadze wraz z konkretnymi odległościami w metrach.

Przykład:

`przystanek: 140 m; sklep: 210 m`

Moduł dokumentuje orientacyjny charakter pomiaru w linii prostej od środka obszaru.

### R6 — Zakres przestrzenny ograniczony do Rzeszowa

Dane wejściowe oraz siatka 25 obszarów w `config/residential-areas.json` obejmują wyłącznie granice administracyjne Rzeszowa.

---

## 4. Szczegóły implementacji silnika RecommendationEngine

### 4.1. Inicjalizacja i walidacja danych wejściowych

Klasa `RecommendationEngine` może zostać utworzona bezpośrednio z list w pamięci:

`__init__(services, locations, areas)`

Może również zostać wczytana z dysku metodą klasową:

`RecommendationEngine.from_files(services_path, locations_path, areas_path)`

Metoda `_validate_records()` weryfikuje, czy przekazane zbiory:

- są niepustymi listami słowników;
- posiadają wymagane klucze (`latitude`, `longitude`, oraz odpowiednio `category`, `id`, `name`, `district`);
- zawierają współrzędne w poprawnym zakresie geograficznym WGS84;
- zawierają skończone wartości liczbowe współrzędnych.

Poprawne zakresy współrzędnych:

- szerokość geograficzna: `-90..90`;
- długość geograficzna: `-180..180`.

Podczas inicjalizacji usługi są indeksowane według kategorii:

`CATEGORIES = ("shop", "bus_stop", "park")`

Przyspiesza to wyszukiwanie najbliższego punktu z każdej kategorii dla każdego obszaru.

### 4.2. Normalizacja odległości i obliczanie punktacji

Odległości w metrach do uczelni oraz najbliższych usług w kategoriach `shop`, `bus_stop` i `park` są przeliczane na ocenę cząstkową `0–100 pkt` przez funkcję:

`score(d, L) = 100.0 * max(0.0, 1.0 - d / L)`

Zastosowane progi odniesienia (`DEFAULT_LIMITS_M`) wynoszą:

- `university`: **3000.0 m**
- `shop`: **1000.0 m**
- `bus_stop`: **600.0 m**
- `park`: **1500.0 m**

Wynik końcowy `total_score` jest średnią ważoną ocen cząstkowych zaokrągloną do 4 miejsc po przecinku.

### 4.3. Struktura pojedynczego rekordu wyjściowego

Metoda obliczeniowa `recommend()` zwraca listę słowników, którą publiczne API umieszcza w polu `recommendations` odpowiedzi. Każdy rekord zawiera:

- `rank` (`int`) – pozycja w rankingu (`1`, `2` lub `3`);
- `area_id` (`str`) – identyfikator obszaru;
- `area_name` (`str`) – nazwa obszaru;
- `district` (`str`) – nazwa osiedla;
- `center_lat` i `center_lon` (`float`) – środek obszaru w stopniach WGS84;
- `radius_m` (`int`) – promień obszaru przekazany z konfiguracji (500 m);
- `score` (`float`) – końcowy wynik punktowy (`0.0–100.0`);
- `walk_distance_m` (`float`) – odległość w linii prostej do uczelni w metrach;
- `walk_time_to_univ_min` (`float`) – szacowany czas dojścia w minutach;
- `distances_m` (`dict[str, float]`) – odległości dla kryteriów `university`, `shop`, `bus_stop`, `park`;
- `scores` (`dict[str, float]`) – oceny cząstkowe (`0–100`) dla każdego kryterium;
- `justification` (`str`) – tekstowe uzasadnienie wskazujące 2 najmocniejsze kryteria lokalizacji.

Publiczna odpowiedź zawiera `status` (`SUCCESS`, `NO_MATCHES`, `VALIDATION_ERROR` lub `DATA_ERROR`), `message`, `disclaimer` oraz `recommendations` (maksymalnie 3 rekordy). Konfiguracja obszarów zachowuje klucz `id`; API udostępnia go w wyniku jako `area_id`.

---

## 5. Wymagania środowiskowe i uruchomienie projektu

### Wymagania wstępne

**Python 3.10** lub nowszy.

Silnik rekomendacji korzysta z biblioteki standardowej Pythona.

Do uruchomienia interfejsu potrzebne są zależności z `requirements.txt`.

Instalacja:

`python -m pip install -r requirements.txt`

### Instrukcja uruchomienia krok po kroku

**1. Sklonowanie repozytorium i przejście do katalogu projektu:**

`git clone https://github.com/CoffiPants/System-rekomendacji-okolic-do-zamieszkania-dla-student-w-w-Rzeszowie.git`

`cd System-rekomendacji-okolic-do-zamieszkania-dla-student-w-w-Rzeszowie`

**2. Opcjonalne ponowne wygenerowanie i weryfikacja danych przetworzonych:**

`python scripts/prepare_data.py`

`python scripts/check_data.py`

**3. Uruchomienie testów jednostkowych silnika rekomendacji:**

`python -m unittest discover -s tests`

**4. Uruchomienie pomiaru wydajności (benchmarku):**

`python scripts/benchmark_recommendation.py`

**5. Uruchomienie aplikacji Streamlit:**

`python -m streamlit run app.py`

**6. Przykładowe wywołanie publicznego API w kodzie Pythona:**

```python
from scripts.recommendation_engine import RecommendationEngine, generate_recommendations

engine = RecommendationEngine.from_files(
    "data/processed/services.json",
    "data/processed/universities.json",
    "config/residential-areas.json",
)

response = generate_recommendations(
    {
        "location_id": "way/208515700",
        "weights": {
            "university": 3,
            "shop": 2,
            "bus_stop": 3,
            "park": 1,
        },
        "max_walk_time_minutes": 30,
    },
    engine=engine,
)
top3 = response["recommendations"] if response["status"] == "SUCCESS" else []
```

---

## 6. Weryfikacja poprawności implementacji (Testy i Benchmark)

### Testy automatyczne

Plik: `tests/test_recommendation_engine.py`

Uruchomiono **7 testów**, wszystkie zakończyły się wynikiem `OK`.

Testy obejmują m.in. sprawdzenie filtrowania obszarów według limitu czasu dojścia.

Szczegółowy zakres testów określa plik testowy.

**Wynik: 7/7 PASS.**

### Testy wydajności

Plik: `scripts/benchmark_recommendation.py`

Benchmark wykonano 100 razy.

Uzyskane wyniki:

- **Powtórzenia:** 100
- **Mediana:** 20,060 ms
- **Minimum:** 19,785 ms
- **Maksimum:** 21,651 ms

Wyniki dotyczą zmierzonej operacji w skrypcie i zależą od środowiska uruchomieniowego.

### Status integracji

Silnik rekomendacji jest połączony z interfejsem Streamlit (`app.py`) przez `generate_recommendations`. Formularz przyjmuje wagi 1–3 oraz limit 15, 30, 45 minut lub brak limitu. UI odczytuje status odpowiedzi i renderuje pola `justification`, `walk_time_to_univ_min`, środek i promień obszaru.

Użytkownik może ustawić preferencje, wygenerować ranking TOP 3 oraz zobaczyć rekomendowane lokalizacje na interaktywnej mapie.

---

## 7. Interfejs użytkownika i wizualizacja (Streamlit)

Plik `app.py` udostępnia działający prototyp **StudentFinder Rzeszów**.

Użytkownik może:

- wybrać uczelnię oraz konkretny budynek lub lokalizację;
- określić maksymalny czas dojścia do uczelni;
- ustawić wagi czterech kryteriów: bliskości uczelni, sklepów, przystanków komunikacji miejskiej i parków;
- wygenerować ranking maksymalnie trzech rekomendowanych okolic;
- zobaczyć wynik punktowy, szacowany czas dojścia, odległość i informacje o usługach;
- obejrzeć rekomendowane lokalizacje na interaktywnej mapie.

Interfejs wywołuje silnik `scripts/recommendation_engine.py`.

Podstawową metodą oceny jest **Weighted Scoring**.

---

## 8. Dane wejściowe i wyjściowe

### Dane wejściowe

System wykorzystuje:

- lokalizacje uczelni;
- obiekty usługowe;
- konfigurację obszarów mieszkalnych;
- preferencje użytkownika.

### Dane wyjściowe

Wynikiem działania systemu jest ranking maksymalnie trzech najwyżej ocenionych okolic spełniających ograniczenie czasu dojścia.

Ranking zawiera wyniki punktowe i jest prezentowany na interaktywnej mapie.

Jeżeli odpowiednich okolic jest mniej niż trzy, aplikacja prezentuje dostępne wyniki.

---

## 9. Obsługa sytuacji wyjątkowych

W interfejsie przewidziano komunikaty dla sytuacji, w których:

- żadna okolica nie spełnia limitu czasu dojścia;
- wszystkie wagi kryteriów są ustawione na zero;
- liczba pasujących okolic jest mniejsza niż trzy.

System obsługuje sytuacje wyjątkowe bez konieczności przerywania działania aplikacji.

---

## 10. Testowanie aplikacji

Przeprowadzono testy automatyczne silnika rekomendacji:

**7 testów, 7 zaliczonych (`OK`).**

Wykonano również benchmark:

**100 powtórzeń, mediana 20,060 ms.**

Sprawdzono poprawność składni plików:

- `app.py`
- `scripts/recommendation_engine.py`
- `scripts/benchmark_recommendation.py`

Wykorzystano polecenie:

`python -m py_compile app.py scripts/recommendation_engine.py scripts/benchmark_recommendation.py`

W ramach ręcznej weryfikacji aplikacji należy sprawdzić:

1. Generowanie rekomendacji.
2. Reakcję na zmianę preferencji.
3. Obsługę braku wyników.
4. Obsługę zerowych wag.
5. Wyświetlanie mapy.

---

## 11. Ograniczenia

Czas dojścia jest szacowany na podstawie odległości geograficznej w linii prostej i przyjętej prędkości marszu.

System nie wyznacza rzeczywistych tras pieszych ani nie uwzględnia aktualnych ofert wynajmu mieszkań.

---

## 12. Podsumowanie

Zrealizowano działający prototyp MVP łączący dane przestrzenne, silnik rekomendacji Weighted Scoring oraz interfejs Streamlit z interaktywną mapą.

Rozwiązanie można rozwijać o dokładniejsze dane dotyczące tras pieszych i ofert mieszkaniowych.

**Interfejs: Dana Stadnyk. Integracja publicznego API silnika z interfejsem: Serhii Popovych.**

**Dokumentacja:** połączono opisy techniczne i interfejsu przygotowane w dwóch gałęziach projektu.
