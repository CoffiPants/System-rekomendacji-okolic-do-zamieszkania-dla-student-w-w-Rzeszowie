# System rekomendacji okolic do zamieszkania dla studentów w Rzeszowie

## Opis problemu
Celem projektu jest opracowanie systemu rekomendacji, który pomoże studentom znaleźć odpowiednie okolice do zamieszkania w Rzeszowie.

## Zespół
- Członkowie zespołu:
- Dana Stadnyk
- Valentyna Boksha
- Serhii Popovych
- Paulina Michalska

## Dokumentacja
- [Opis problemu](docs/problem.md)
- [Opis danych](docs/data.md)

## Przygotowanie danych — Lab 3

Wymagane środowisko: Python 3.10 lub nowszy. Skrypt korzysta tylko z biblioteki standardowej; nie wymaga instalowania pakietów ani dostępu do internetu.

Uruchomienie z katalogu repozytorium:

```shell
python scripts/prepare_data.py
```

Wejście: data/raw/sample.json, data/raw/universities.json, config/university-selection.json.
Wynik: data/processed/services.json i data/processed/universities.json.

Dla bieżącej próbki: 500 usług, w tym 21 bez nazwy źródłowej, oraz 28 wybranych miejsc zajęć. Brakującym nazwom usług przypisano etykiety kategorii z ID, zachowując oznaczenie name_missing. Reguły wyboru uczelni i źródła uzupełnień znajdują się w config/university-selection.json.

Skrypt nie zmienia plików raw. Nie pobiera aktualizacji API i nie oblicza jeszcze tras ani rankingu okolic. Nieprawidłowe identyfikatory, współrzędne lub reguły powodują zakończenie z komunikatem błędu.

---

## Struktura projektu

- `config/` — konfiguracja wyboru lokalizacji uczelni.
- `data/raw/` — oryginalne dane pobrane z OpenStreetMap.
- `data/processed/` — dane po przetworzeniu.
- `data/test/` — raporty kontroli jakości i audytu danych.
- `docs/` — dokumentacja projektu.
- `scripts/prepare_data.py` — skrypt przygotowania danych.
- `scripts/check_data.py` — skrypt automatycznej kontroli jakości danych.
- `scripts/audit_data.py` — skrypt szczegółowego audytu kompletności i spójności danych.

---

## Kontrola jakości danych — Lab 3

**Odpowiedzialna: Dana Stadnyk**

Przygotowano niezależny skrypt `scripts/check_data.py`, który automatycznie sprawdza poprawność danych po przetworzeniu.

### Zakres kontroli

Skrypt weryfikuje:

1. Poprawność formatu identyfikatorów OSM.
2. Unikalność identyfikatorów.
3. Poprawność współrzędnych geograficznych.
4. Obecność nazw obiektów.
5. Poprawność kategorii usług: `shop`, `bus_stop`, `park`.
6. Poprawność oznaczenia brakujących nazw (`name_missing`).
7. Zgodność `name_missing` z polem `source_name`.
8. Poprawność pola `coordinate_type`.
9. Obecność adresów lokalizacji uczelni.
10. Poprawność oznaczeń uczelni i typów lokalizacji.

### Uruchomienie kontroli

```bash
python scripts/check_data.py
```

Skrypt sprawdza pliki:

- `data/processed/services.json`
- `data/processed/universities.json`

Raport jest zapisywany w pliku:

`data/test/quality-report.json`

### Wyniki kontroli

| Zbiór danych | Liczba rekordów | Wykryte naruszenia |
|---|---:|---:|
| Usługi | 500 | 0 |
| Lokalizacje uczelni | 28 | 0 |
| **Łącznie** | **528** | **0** |

**Wynik: PASS — wszystkie dane przeszły zaimplementowane kontrole jakości.**

### Testowanie na celowo błędnych danych

Aby sprawdzić skuteczność walidacji, przygotowano testy z celowo wprowadzonymi błędami.

Uruchomienie:

```bash
python scripts/check_data.py --test-invalid
```

Skrypt tworzy trzy kopie danych zawierające błędy:

| Plik | Wprowadzony błąd | Wynik |
|---|---|---|
| `duplicate_service.json` | Powtórzony identyfikator OSM | Wykryto |
| `invalid_coordinate.json` | Nieprawidłowa szerokość geograficzna | Wykryto |
| `missing_university_address.json` | Brak adresu uczelni | Wykryto |

**Wynik: 3/3 testy zakończone pomyślnie.**

Raporty:

- `data/test/quality-report.json`
- `data/test/invalid-tests-report.json`

Testowanie nie modyfikuje danych źródłowych ani przetworzonych.

---

## Audyt kompletności i spójności danych — Lab 3

**Odpowiedzialna: Dana Stadnyk**

Dodatkowo przygotowano skrypt `scripts/audit_data.py`, który przeprowadza szczegółowy audyt kompletności, poprawności i spójności danych wynikowych.

### Zakres audytu

Skrypt sprawdza:

1. Zgodność struktury rekordów z przyjętym schematem.
2. Obecność wymaganych pól i brakujące wartości.
3. Poprawność identyfikatorów OSM.
4. Poprawność współrzędnych geograficznych.
5. Spójność typów współrzędnych.
6. Poprawność adresów URL obiektów OSM.
7. Zgodność kategorii usług i oznaczeń uczelni.
8. Poprawność oznaczeń brakujących nazw źródłowych.
9. Powtarzające się identyfikatory i współrzędne.
10. Spójność danych tekstowych.

### Uruchomienie audytu

```bash
python scripts/audit_data.py
```

### Wyniki audytu

Przeprowadzono analizę 528 rekordów.

| Wskaźnik | Wynik |
|---|---:|
| Liczba wszystkich rekordów | 528 |
| Usługi | 500 |
| Lokalizacje uczelni | 28 |
| Błędy | 0 |
| Ostrzeżenia | 0 |
| Informacje | 408 |
| Powtarzające się współrzędne | 0 |

**Wynik audytu: PASS — brak błędów krytycznych.**

### Struktura danych usługowych

| Kategoria | Liczba rekordów |
|---|---:|
| Sklepy (`shop`) | 274 |
| Przystanki autobusowe (`bus_stop`) | 185 |
| Parki (`park`) | 41 |
| **Łącznie** | **500** |

### Struktura danych uczelni

| Uczelnia | Liczba lokalizacji |
|---|---:|
| Uniwersytet Rzeszowski (UR) | 16 |
| Politechnika Rzeszowska (PRz) | 10 |
| Wyższa Szkoła Informatyki i Zarządzania (WSIiZ) | 1 |
| WSPiA Rzeszowska Szkoła Wyższa (WSPiA) | 1 |
| **Łącznie** | **28** |

Typy lokalizacji:

- 26 budynków (`building`),
- 2 kampusy (`campus`).

### Analiza kompletności danych

W trakcie audytu zidentyfikowano następujące brakujące wartości:

| Zbiór danych | Pole | Liczba braków |
|---|---|---:|
| Usługi | `address` | 387 |
| Usługi | `source_name` | 21 |
| Uczelnie | `source_name` | 1 |

Braki te dotyczą pól opcjonalnych i nie powodują niepowodzenia walidacji.

W przypadku usług bez nazwy źródłowej zastosowano nazwy zastępcze oraz zachowano informację w polu `name_missing`.

Brak adresu usługi nie oznacza automatycznie błędu, ponieważ nie wszystkie obiekty OpenStreetMap posiadają pełne dane adresowe.

Brakujące informacje mogą zostać poddane dodatkowej weryfikacji i uzupełnieniu.

### Klasyfikacja wyników audytu

Wyniki audytu podzielono na trzy poziomy:

- **Błąd** — naruszenie wymaganych reguł jakości danych.
- **Ostrzeżenie** — potencjalna niespójność wymagająca dodatkowej weryfikacji.
- **Informacja** — obserwacja dotycząca danych, która nie uniemożliwia ich wykorzystania.

Dla bieżącego zbioru danych uzyskano:

- 0 błędów,
- 0 ostrzeżeń,
- 408 informacji.

### Raport audytu

Szczegółowe wyniki analizy zapisywane są w pliku:

`data/test/audit-report.json`

Skrypt nie modyfikuje danych źródłowych ani przetworzonych.

---

## Podsumowanie przygotowania i kontroli danych — Lab 3

W ramach laboratorium 3:

1. Przygotowano skrypt przetwarzania danych źródłowych.
2. Utworzono dwa zbiory danych wynikowych w formacie JSON.
3. Przeprowadzono automatyczną kontrolę jakości 528 rekordów.
4. Sprawdzono poprawność identyfikatorów, współrzędnych, kategorii i wymaganych pól.
5. Przeprowadzono trzy testy na celowo błędnych kopiach danych.
6. Wykonano szczegółowy audyt kompletności i spójności danych.
7. Zidentyfikowano i udokumentowano brakujące wartości w polach opcjonalnych.
8. Zapisano raporty kontroli jakości i audytu w katalogu `data/test/`.

**Wszystkie przeprowadzone kontrole zakończyły się pomyślnie.**

Dane przeszły zaimplementowane kontrole automatyczne. Dodatkowa weryfikacja merytoryczna lokalizacji i brakujących informacji pozostaje kolejnym etapem prac.

---

## Wymagania techniczne

- Python 3.10 lub nowszy.
- Brak dodatkowych bibliotek.
- Brak konieczności połączenia z internetem podczas lokalnego przetwarzania danych.

### Kolejność uruchamiania skryptów

Wszystkie polecenia należy uruchamiać z katalogu głównego repozytorium.

**1. Przygotowanie danych:**

```bash
python scripts/prepare_data.py
```

**2. Automatyczna kontrola jakości:**

```bash
python scripts/check_data.py
```

**3. Testowanie na błędnych kopiach:**

```bash
python scripts/check_data.py --test-invalid
```

**4. Szczegółowy audyt danych:**

```bash
python scripts/audit_data.py
```

Wyniki kontroli i audytu są zapisywane w katalogu `data/test/`.

## Słownik danych i opis przetwarzania

- [Słownik danych](docs/data-dictionary.md)
- [Przetwarzanie, kontrole i powtarzalność](docs/processing.md)

## Lab 4 — porównanie metod rekomendacji

Eksperyment porównuje ranking bazowy (odległość wyłącznie od wybranej
uczelni) z rankingiem ważonym, który uwzględnia także sklepy, przystanki i
parki. Opis założeń znajduje się w [docs/experiment.md](docs/experiment.md).

Uruchomienie z katalogu głównego:

```shell
python scripts/compare_methods.py
```

Wyniki trafiają do `results/lab4/`. Identyfikator wybranej lokalizacji zajęć
można zmienić opcją `--university-id`; próbę wrażliwości zapisuje się do
osobnego katalogu:

```shell
python scripts/compare_methods.py --shop-limit 1500 \
  --output results/lab4/sensitivity
```

## Silnik rekomendacji — Lab 6 i Lab 7

Silnik znajduje się w `scripts/recommendation_engine.py`. Przyjmuje dane
przetworzone oraz środki 25 obszarów z `config/residential-areas.json`.
Ranking uwzględnia odległość od wybranej lokalizacji uczelni, sklepu,
przystanku i parku. Wagi można przekazać z aplikacji, a limit czasu dojścia
filtruje obszary przed utworzeniem rankingu.

Odległości są liczone w linii prostej wzorem Haversine'a. Czas dojścia jest
orientacyjny i przyjmuje prędkość 4,5 km/h (75 metrów na minutę). Aplikacja
wywołuje publiczne `generate_recommendations(request, engine=None)`, które
zwraca status, komunikat, zastrzeżenie oraz ranking TOP 3.

Testy silnika:

```shell
python -m unittest discover -s tests -v
```

Pomiar wydajności dla 100 powtórzeń:

```shell
python scripts/benchmark_recommendation.py
```

### Sprawdzenie powtarzalności

Python 3.10+, bez dodatkowych pakietów. Z katalogu głównego projektu:

```shell
python scripts/verify_repeatability.py
```

Skrypt dwukrotnie przygotowuje i sprawdza dane z tej samej zapisanej próbki. Zachowuje kopie odniesienia w data/test/repeatability-reference/, usuwa wyłącznie dwa wygenerowane pliki z data/processed/ i je odtwarza. Porównuje liczbę rekordów, pola, wartości i wyniki kontroli. Nie zmienia data/raw/ ani konfiguracji.

Raport: data/test/repeatability-report.json. Wynik jest również zapisywany w data/test/repeatability-result.md i sekcji 9 dokumentu docs/processing.md.


## Lab 4 — porównanie Weighted Scoring i KNN

W ramach drugiego eksperymentu porównano dwie techniki rekomendacji okolic mieszkalnych dla studentów w Rzeszowie:

1. **Weighted Scoring** — metoda oceniająca okolice na podstawie ważonej sumy punktów za bliskość uczelni, sklepów, przystanków autobusowych i parków.
2. **KNN (K-Nearest Neighbors)** — metoda wybierająca okolice najbardziej zbliżone do profilu preferencji studenta na podstawie ważonej odległości euklidesowej.

### Dane i metodyka

Wykorzystano 25 lokalizacji mieszkalnych zapisanych w `config/residential-areas.json` oraz dane o usługach i uczelniach z katalogu `data/processed/`.

Przeanalizowano trzy profile preferencji:

- `balanced` — zrównoważone preferencje,
- `university_priority` — priorytet bliskości uczelni,
- `services_priority` — priorytet dostępu do usług.

Dla każdego profilu porównano trzy najwyżej ocenione okolice.

### Wyniki porównania

| Profil | Najlepsza okolica — Weighted Scoring | Najlepsza okolica — KNN | Zgodność TOP 3 |
|---|---|---|---|
| balanced | Krakowska-Południe | Krakowska-Południe | 2/3 |
| university_priority | Krakowska-Południe | Krakowska-Południe | 2/3 |
| services_priority | Drabinianka 1 | Drabinianka 1 | 2/3 |

Obie metody wskazały tę samą najlepszą okolicę dla każdego z trzech profili, ale różniły się pozostałymi pozycjami w rankingach.

### Porównanie czasu wykonania

Przeprowadzono benchmark obejmujący 1000 powtórzeń dla 25 okolic.

| Metoda | Czas wykonania |
|---|---:|
| Weighted Scoring | 0,017700 ms |
| KNN | 0,037400 ms |

W przeprowadzonym pomiarze **Weighted Scoring działał szybciej niż KNN**.

### Testowanie

Przeprowadzono trzy testy automatyczne algorytmu KNN.

**Wynik: 3/3 testy zakończone pomyślnie.**

### Uruchamianie

Wszystkie polecenia należy wykonywać z głównego katalogu projektu.

**Rekomendacje KNN:**

```bash
py scripts/knn_recommender.py
```

**Porównanie Weighted Scoring i KNN:**

```bash
py scripts/compare_knn_weighted.py
```

**Testy automatyczne:**

```bash
py scripts/test_knn.py
```

**Benchmark:**

```bash
py scripts/benchmark_knn_weighted.py
```

### Pliki projektu

- `scripts/knn_recommender.py` — implementacja KNN.
- `scripts/compare_knn_weighted.py` — porównanie rankingów.
- `scripts/test_knn.py` — testy automatyczne.
- `scripts/benchmark_knn_weighted.py` — porównanie czasu wykonania.
- `results/lab4/knn/comparison.csv` — podsumowanie wyników.
- `results/lab4/knn/rankings.csv` — rankingi dla wszystkich profili.
- `docs/experiment.md` — szczegółowa dokumentacja eksperymentów.

### Wnioski

Obie techniki pozwalają rekomendować okolice zgodnie z preferencjami studentów.

Weighted Scoring okazał się szybszy w przeprowadzonym eksperymencie i umożliwia łatwą interpretację punktacji poszczególnych kryteriów.

KNN stanowi alternatywną metodę opartą na podobieństwie okolic do zadanego profilu preferencji.

**Do dalszego rozwoju systemu wybrano Weighted Scoring jako metodę podstawową.**


---

## Lab 6 — Implementacja MVP i interfejs użytkownika

**Interfejs: Dana Stadnyk. Integracja API silnika: Serhii Popovych.**

W ramach laboratorium 6 przygotowano działający prototyp
systemu StudentFinder Rzeszów z interfejsem graficznym
zrealizowanym w technologii Streamlit.

### Funkcjonalności aplikacji

- Wybór uczelni oraz budynku lub wydziału.
- Określenie maksymalnego czasu dojścia do uczelni.
- Ustawienie wag kryteriów w zakresie 1–3:
  - bliskość uczelni,
  - dostępność sklepów,
  - dostępność komunikacji miejskiej,
  - dostępność parków.
- Generowanie rankingu maksymalnie trzech rekomendowanych okolic.
- Prezentacja wyników w formie kart z oceną punktową.
- Wyświetlanie rekomendowanych lokalizacji na interaktywnej mapie.
- Obsługa sytuacji, w której nie znaleziono odpowiednich okolic.
- Obsługa statusów `SUCCESS`, `NO_MATCHES`, `VALIDATION_ERROR` i `DATA_ERROR`.

### Architektura rozwiązania

Aplikacja wykorzystuje dane przygotowane we wcześniejszych
etapach projektu.

Interfejs użytkownika znajduje się w pliku `app.py`.

Logika rekomendacji jest realizowana przez moduł
`scripts/recommendation_engine.py`.

System wykorzystuje metodę Weighted Scoring do oceny
okolic na podstawie preferencji użytkownika.

### Uruchomienie aplikacji

Wymagany jest Python 3.10 lub nowszy.

Instalacja zależności:

```bash
python -m pip install -r requirements.txt
```

Uruchomienie:

```bash
python -m streamlit run app.py
```

Po uruchomieniu aplikacja jest dostępna pod adresem
lokalnym wskazanym w terminalu.

### Testowanie

Testy automatyczne:

```bash
python -m unittest discover -s tests -v
```

Kontrola składni:

```bash
python -m py_compile app.py scripts/recommendation_engine.py
```

Benchmark:

```bash
python scripts/benchmark_recommendation.py
```

### Ograniczenia MVP

- Czas dojścia jest szacowany na podstawie odległości
  w linii prostej.
- System nie uwzględnia rzeczywistej sieci ulic,
  przejść dla pieszych ani warunków ruchu.
- Rekomendacje bazują na przygotowanym zbiorze danych,
  a nie na aktualnych ofertach wynajmu mieszkań.
- Wyniki dotyczą 25 zdefiniowanych obszarów mieszkalnych.

### Pliki

- `app.py` — interfejs użytkownika Streamlit.
- `scripts/recommendation_engine.py` — logika rekomendacji.
- `scripts/benchmark_recommendation.py` — pomiar wydajności.
- `tests/test_recommendation_engine.py` — testy automatyczne.
- `docs/implementation.md` — dokumentacja implementacji MVP.
- `docs/area-name-audit.md` — etykiety 25 obszarów i linki do sprawdzonych współrzędnych na mapie OSM.
