# Dokumentacja implementacji. Laboratorium 6

## 1. Cel etapu i zakres wdrożenia

Celem Laboratorium 6 było przeniesienie projektu architektonicznego (`docs/architecture.md`) do działającej implementacji systemu rekomendacji okolic mieszkalnych dla studentów w Rzeszowie.

System realizuje warstwę analityczną i walidacyjną w języku **Python** w oparciu o przetworzone zbiory **JSON** oraz konfigurację obszarów mieszkalnych, a także zintegrowany interfejs użytkownika w technologii **Streamlit**.

---

## 2. Struktura kodu i organizacja modułów

Projekt dzieli się na warstwę danych, warstwę przetwarzania i audytu, warstwę silnika rekomendacji oraz testy:

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
- `scripts/data_validation.py` – walidacja trzech dokumentów JSON przed utworzeniem silnika. Moduł `validate_documents()` nie wczytuje plików i zgłasza `DataValidationError` (podklasa `ValueError`) z listą naruszeń.
- `scripts/recommendation_engine.py` – silnik rekomendacji (`RecommendationEngine`) oraz publiczne API `generate_recommendations(request, engine=None)` używane przez aplikację.
- `scripts/benchmark_recommendation.py` – pomiar czasu wywołania `recommend()` (wynik w `results/lab7/`).
- `app.py` – interfejs Streamlit: wybór uczelni i budynku, wagi, limit czasu, karty wyników, mapa oraz eksport rankingu TOP 3 do CSV.
- `tests/test_recommendation_engine.py` – testy jednostkowe i brzegowe silnika.
- `tests/test_data_validation.py` – wczytywanie plików, uszkodzony JSON, puste listy, powtórzone identyfikatory, współrzędne, wymagane pola i kategorie.
- `tests/test_request_validation.py` – parametry żądania publicznego API oraz test integracyjny na danych projektu.
- `tests/test_weight_scoring.py` – wpływ wag na oceny cząstkowe i końcowe, z ręcznym obliczeniem.
- `docs/` – dokumentacja projektowa; `results/lab7/` – kryterium, wynik pomiaru i surowe wyjście skryptu.

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

Interfejs i publiczne API przyjmują wartości całkowite od `1` do `3`. Niższy poziom `RecommendationEngine.recommend` sprawdza typ i nieujemność wag oraz odrzuca wartości `NaN` i nieskończone.

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

Odpowiedź API zawiera stałe pole `disclaimer` o pomiarze w linii prostej od środka obszaru i szacowanym czasie przy 4,5 km/h.

### R6 — Zakres przestrzenny ograniczony do Rzeszowa

Dane wejściowe oraz siatka 25 obszarów w `config/residential-areas.json` obejmują wyłącznie granice administracyjne Rzeszowa.

---

## 4. Szczegóły implementacji silnika RecommendationEngine

### 4.1. Inicjalizacja i walidacja danych wejściowych

Klasa `RecommendationEngine` może zostać utworzona bezpośrednio z list w pamięci:

`__init__(services, locations, areas)`

Może również zostać wczytana z dysku metodą klasową:

`RecommendationEngine.from_files(services_path, locations_path, areas_path)`

Przy wczytywaniu z plików `from_files()` wywołuje `validate_documents()` z `scripts/data_validation.py` przed utworzeniem silnika. Walidacja sprawdza:

- czy dokumenty są obiektami JSON z listami `services`, `locations` i `areas`;
- czy listy nie są puste;
- czy każdy rekord jest obiektem i ma tekstowy identyfikator `id` bez powtórzeń;
- czy współrzędne są skończonymi liczbami w zakresie WGS84;
- czy usługa ma kategorię `shop`, `bus_stop` lub `park`, a lokalizacja pola `university`, `name`, `address`, obszar pola `name` i `district`.

Metoda `_validate_records()` sprawdza, czy przekazane zbiory są listami słowników, mają wymagane klucze (`latitude`, `longitude`, oraz odpowiednio `category`, `id`, `name`, `district`) i poprawne współrzędne. Nie sprawdza, czy listy są niepuste. Pustość zbiorów sprawdza konstruktor klasy po walidacji rekordów, a przy wczytywaniu z plików także `validate_documents()`.

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

**3. Uruchomienie testów automatycznych:**

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

## 6. Weryfikacja i ocena implementacji

### 6.1. Testy automatyczne

Polecenie:

`python -m unittest discover -s tests`

Testy są podzielone na cztery pliki:

- `tests/test_recommendation_engine.py` – filtrowanie po czasie, ranking, remisy, uzasadnienie, walidacja wag;
- `tests/test_data_validation.py` – wczytywanie plików, brak pliku, uszkodzony JSON, `[]` zamiast obiektu, pusta lista, powtórzone `id`, współrzędne, wymagane pola, kategorie;
- `tests/test_request_validation.py` – pola i typy żądania, dozwolone limity 15/30/45/brak, wagi 1–3, `NaN` i `inf`, test integracyjny dla 28 lokalizacji × 4 limity oraz determinizm;
- `tests/test_weight_scoring.py` – oceny cząstkowe i końcowe dla siedmiu zestawów wag, ręcznie policzone oczekiwania, próg punktacji.

**Wynik: 51/51 PASS** (`Ran 51 tests in 1.952s`, `OK`), Python 3.15.2, commit `ed0366c`. Zakres i dziennik uruchomień opisuje `docs/tests.md` (punkty 2.1 i 4).

### 6.2. Pomiar wydajności

Plik: `scripts/benchmark_recommendation.py`, wynik: `results/lab7/benchmark.md`.

Kryterium ustalono przed pomiarem: mediana czasu obliczenia rankingu ≤ 100 ms przy 100 powtórzeniach, 25 obszarach mieszkalnych i 500 usługach.

Polecenie:

`python scripts/benchmark_recommendation.py --repetitions 100`

Parametry: lokalizacja `way/197227711` (PRz, Budynek P), limit 30 min, wagi uczelnia 3 / sklep 2 / przystanek 2 / park 2.

| Miara | Wynik |
|---|---|
| Mediana | 16,000 ms |
| Minimum | 15,748 ms |
| Maksimum | 17,090 ms |
| Powtórzenia | 100 |

Warunki: Apple M1 Max (10 rdzeni, 32 GB), macOS 27.2.1, Python 3.15.2, obciążenie 7,40 (średnia 1 min). Mierzono wyłącznie `recommend()`, bez wczytywania plików. Kryterium jest spełnione z zapasem.

### 6.3. Sprawdzona wersja i osoba weryfikująca

| Element | Wartość |
|---|---|
| Sprawdzona wersja | `main` `653393e` (PR #21); pomiar Lab 7 na `ed0366c` |
| Osoba weryfikująca | Valentyna Boksha |
| Zakres weryfikacji | 51/51 testów (`653393e`), ręczne sprawdzenie interfejsu (`0df4f8b`), przegląd kodu w Issue #8 i `docs/tests.md` (punkt 4) |
| Autor pomiaru i tego dokumentu | Serhii Popovych |

Zmiany z tego PR (pomiar Lab 7, poprawki dokumentacji) wymagają zatwierdzenia przez drugą osobę w PR.

### 6.4. Ocena usprawnienia implementacji

Porównanie stanu przed walidacją i po jej dodaniu. Dane pochodzą z `docs/tests.md` (dziennik uruchomień i punkt 4).

| Przypadek | Przed (`1d9e312` + nowe testy) | Po (`0df4f8b`, obecnie `ed0366c`) |
|---|---|---|
| Powtórzony `id` | przyjmowany | odrzucany przez `validate_documents()` |
| Dokument `[]` zamiast obiektu | `AttributeError`, aplikacja bez komunikatu | `DataValidationError`, odpowiedź `DATA_ERROR` z komunikatem |
| Nieznana kategoria usługi | przyjmowana | odrzucana |
| Brak `university` lub `address` | niewykryty | odrzucany |
| Waga `NaN` lub `inf` w `recommend()` | wynik `nan` | `ValueError`, publiczne API zwraca `VALIDATION_ERROR` |
| Testy | 29 niepowodzeń i 3 błędy | **51/51 PASS** |

Uzasadnienie: pięć rzeczywistych luk walidacji zamknięto bez zmiany wzoru punktacji, progów i kolejności rankingu. Benchmark po zmianie (16,000 ms mediany) mieści się w kryterium 100 ms. Dodatkowy koszt walidacji ponoszony jest tylko przy wczytywaniu plików, nie w mierzonym `recommend()`.

### 6.5. Integracja z interfejsem i obsługa sytuacji wyjątkowych

Silnik jest połączony z `app.py` przez `generate_recommendations`. Formularz przyjmuje wagi 1–3 oraz limit 15, 30, 45 minut lub brak limitu. UI odczytuje status odpowiedzi i renderuje `justification`, `walk_time_to_univ_min`, środek i promień obszaru, a wyniki pokazuje na mapie.

Po wygenerowaniu rankingu dostępny jest przycisk „Pobierz ranking TOP 3 (CSV)”. Plik `studentfinder_top3.csv` ma 11 kolumn, separator `;` i znacznik BOM, więc polskie znaki są czytelne w Excelu.

Interfejs przewiduje komunikaty, gdy:

- żadna okolica nie spełnia limitu czasu (`NO_MATCHES`);
- pasujących okolic jest mniej niż trzy (wyświetla dostępne wyniki);
- nie można wczytać danych projektu (`DATA_ERROR`).

Aplikacja nie przerywa działania w tych sytuacjach.

### 6.6. Ograniczenia

Czas dojścia jest szacowany na podstawie odległości w linii prostej i prędkości 4,5 km/h. System nie wyznacza rzeczywistych tras pieszych ani nie uwzględnia ofert wynajmu mieszkań. Dane OSM mogą nie obejmować wszystkich usług w mieście. Eksport CSV zapisuje czas z przecinkiem dziesiętnym, a ocenę i odległości z kropką (`docs/tests.md`, punkt 7). Testy interfejsu nie są zautomatyzowane w repozytorium.

---

**Interfejs: Dana Stadnyk. Integracja publicznego API silnika z interfejsem: Serhii Popovych.**

**Dokumentacja:** połączono opisy techniczne i interfejsu przygotowane w dwóch gałęziach projektu.
