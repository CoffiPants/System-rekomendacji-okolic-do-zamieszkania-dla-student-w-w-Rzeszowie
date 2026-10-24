# Przygotowanie i przetwarzanie danych — Lab 3

## 1. Cel przetwarzania

Celem etapu jest przygotowanie spójnych danych o lokalizacjach uczelni oraz usługach dostępnych w Rzeszowie na potrzeby systemu rekomendacji okolic do zamieszkania dla studentów.

Przetwarzanie odbywa się automatycznie za pomocą skryptu `scripts/prepare_data.py`. Kontrola jakości i audyt danych są realizowane przez osobne skrypty.

## 2. Dane wejściowe

W procesie wykorzystywane są trzy pliki:

| Plik                               | Zawartość                                                                          |
| ---------------------------------- | ---------------------------------------------------------------------------------- |
| `data/raw/sample.json`             | Surowe dane OSM dotyczące sklepów, przystanków autobusowych i parków.              |
| `data/raw/universities.json`       | Surowe dane OSM dotyczące obiektów uczelnianych.                                   |
| `config/university-selection.json` | Reguły wyboru lokalizacji uczelni oraz udokumentowane uzupełnienia nazw i adresów. |

Dane pochodzą z OpenStreetMap i zostały pobrane przez Overpass API.

Pliki źródłowe pozostają niezmienione podczas przetwarzania.

## 3. Operacje czyszczenia i transformacji

### 3.1. Weryfikacja struktury danych wejściowych

Skrypt sprawdza, czy odpowiedź OSM zawiera niepustą listę `elements` oraz czy nie występuje komunikat błędu w polu `remark`.

Każdy obiekt musi posiadać poprawny typ (`node`, `way` lub `relation`) oraz całkowitoliczbowy identyfikator.

Powtórzenie identyfikatora złożonego z typu i ID powoduje zakończenie przetwarzania z błędem.

### 3.2. Filtrowanie usług

Z danych źródłowych wybierane są wyłącznie obiekty należące do kategorii:

* `shop` — sklepy typu `supermarket` i `convenience`;
* `bus_stop` — węzły OSM oznaczone `highway=bus_stop`;
* `park` — obiekty oznaczone `leisure=park`.

Pozostałe obiekty są pomijane.

W bieżącej próbce wszystkie 500 obiektów spełniają warunki filtrowania.

### 3.3. Normalizacja wartości tekstowych

Funkcja `text()` usuwa nadmiarowe białe znaki z wartości tekstowych.

Operacja obejmuje między innymi nazwy obiektów, nazwy uzupełnione w konfiguracji oraz elementy adresów.

Dzięki temu wartości wykorzystywane w aplikacji mają jednolity zapis.

### 3.4. Obsługa brakujących nazw usług

Jeżeli obiekt usługowy nie posiada nazwy źródłowej, skrypt tworzy nazwę zastępczą na podstawie kategorii i identyfikatora OSM.

Przykładowy format:

`Przystanek (node/123456)`

Dodatkowo zapisywane są:

* `name_missing = true` — informacja o braku nazwy źródłowej;
* `source_name` — oryginalna wartość nazwy.

W bieżącym zbiorze 21 usług nie posiada nazwy źródłowej.

Nazwy zastępcze służą wyłącznie do identyfikacji obiektów w aplikacji i nie są traktowane jako zweryfikowane nazwy własne.

### 3.5. Standaryzacja adresów

Adres jest tworzony z pól OSM:

* `addr:street`;
* `addr:housenumber`;
* `addr:city`.

Jeżeli ulica lub numer budynku nie są dostępne, funkcja `address()` zwraca `None`.

Jeżeli dostępne są ulica i numer budynku, ale nie podano miasta, skrypt stosuje wartość `Rzeszów`.

Brak adresu usługi nie powoduje jej usunięcia, ponieważ do obliczania odległości wykorzystywane są współrzędne.

### 3.6. Weryfikacja i standaryzacja współrzędnych

Skrypt sprawdza, czy szerokość i długość geograficzna:

* mają typ liczbowy;
* nie są wartościami logicznymi;
* są liczbami skończonymi;
* mieszczą się w zakresach od −90 do 90 oraz od −180 do 180.

Dla obiektów typu `node` wykorzystywane są współrzędne `lat` i `lon`.

Dla obiektów `way` oraz `relation` wykorzystywane są współrzędne z pola `center`.

Pochodzenie współrzędnych jest zapisywane w polu `coordinate_type` jako `osm_node` lub `osm_bounding_box_center`.

Środek obwiedni obiektu nie musi odpowiadać wejściu do budynku ani parku.

### 3.7. Wybór i uzupełnianie lokalizacji uczelni

Lokalizacje uczelni wybierane są na podstawie pliku `config/university-selection.json`.

Skrypt sprawdza, czy:

* wybrany identyfikator istnieje w surowych danych;
* reguły wyboru nie powtarzają się;
* uczelnia należy do zbioru `UR`, `PRz`, `WSIiZ`, `WSPiA`;
* typ lokalizacji to `building` lub `campus`;
* lokalizacja posiada nazwę, adres i poprawne współrzędne;
* każde uzupełnienie nazwy lub adresu ma wskazane źródło.

Dopuszczalne uzupełnienia dotyczą wyłącznie pól `name` i `address`.

Z 105 obiektów uczelnianych wybrano 28 lokalizacji.

### 3.8. Ujednolicenie struktury i sortowanie

Każdy rekord wynikowy otrzymuje zestaw pól opisujących jego identyfikator, kategorię lub uczelnię, nazwę, adres, współrzędne oraz pochodzenie danych.

Rekordy są sortowane rosnąco według identyfikatora `id`.

Sortowanie zapewnia stabilną kolejność danych wynikowych dla tej samej próbki wejściowej.

## 4. Dane wynikowe

Skrypt zapisuje dwa pliki:

| Plik                               | Liczba rekordów | Zawartość                              |
| ---------------------------------- | --------------: | -------------------------------------- |
| `data/processed/services.json`     |             500 | Sklepy, przystanki autobusowe i parki  |
| `data/processed/universities.json` |              28 | Wybrane miejsca zajęć czterech uczelni |
| **Łącznie**                        |         **528** |                                        |

Struktura usług:

* 274 sklepy;
* 185 przystanków autobusowych;
* 41 parków.

Struktura lokalizacji uczelni:

* UR — 16;
* PRz — 10;
* WSIiZ — 1;
* WSPiA — 1.

Pliki wynikowe zawierają informację o źródle danych i licencji OpenStreetMap.

## 5. Uruchomienie przetwarzania

Wymagania:

* Python 3.10 lub nowszy;
* brak dodatkowych bibliotek;
* brak konieczności połączenia z internetem.

Z katalogu głównego repozytorium należy uruchomić:

```bash
python scripts/prepare_data.py
```

W systemie Windows można również użyć:

```bash
py scripts/prepare_data.py
```

Skrypt odczytuje zapisane dane źródłowe i generuje pliki wynikowe.

Przy nieprawidłowych danych wejściowych kończy działanie z komunikatem błędu.

## 6. Automatyczna kontrola jakości

Za przygotowanie dodatkowych kontroli jakości odpowiada Dana Stadnyk.

Kontrole wykonywane są na danych wynikowych.

Uruchomienie:

```bash
python scripts/check_data.py
```

Sprawdzane są między innymi:

* format i unikalność identyfikatorów;
* poprawność współrzędnych;
* obecność wymaganych nazw i adresów uczelni;
* poprawność kategorii usług;
* spójność oznaczeń brakujących nazw;
* poprawność typów lokalizacji.

Raport jest zapisywany w pliku:

`data/test/quality-report.json`

Dla bieżącej próbki:

| Zbiór       | Rekordy | Naruszenia |
| ----------- | ------: | ---------: |
| Usługi      |     500 |          0 |
| Uczelnie    |      28 |          0 |
| **Łącznie** | **528** |      **0** |

Wynik: **PASS**.

## 7. Testowanie na celowo błędnych danych

W celu sprawdzenia działania walidacji zastosowano trzy kopie danych z celowo wprowadzonymi błędami.

Uruchomienie:

```bash
python scripts/check_data.py --test-invalid
```

| Plik                                        | Wprowadzony błąd                     | Oczekiwany wynik                |
| ------------------------------------------- | ------------------------------------ | ------------------------------- |
| `data/test/duplicate_service.json`          | Powtórzony identyfikator OSM         | Wykrycie duplikatu              |
| `data/test/invalid_coordinate.json`         | Nieprawidłowa szerokość geograficzna | Wykrycie błędnych współrzędnych |
| `data/test/missing_university_address.json` | Brak adresu lokalizacji uczelni      | Wykrycie brakującego pola       |

Wszystkie trzy błędy zostały wykryte.

Wynik: **3/3 testy zakończone pomyślnie**.

Raport: `data/test/invalid-tests-report.json`.

Testy nie modyfikują danych źródłowych ani wynikowych.

## 8. Dodatkowy audyt danych

Skrypt `scripts/audit_data.py` wykonuje rozszerzoną kontrolę kompletności i spójności danych.

Uruchomienie:

```bash
python scripts/audit_data.py
```

Audyt obejmuje między innymi:

* strukturę rekordów;
* brakujące wartości;
* identyfikatory i współrzędne;
* adresy URL obiektów OSM;
* kategorie i typy lokalizacji;
* duplikaty identyfikatorów i współrzędnych;
* spójność pól tekstowych.

Wyniki dla bieżącej próbki:

| Wskaźnik                     | Wynik |
| ---------------------------- | ----: |
| Sprawdzone rekordy           |   528 |
| Błędy                        |     0 |
| Ostrzeżenia                  |     0 |
| Informacje                   |   408 |
| Powtarzające się współrzędne |     0 |

Wykryte braki:

| Zbiór    | Pole          | Liczba braków |
| -------- | ------------- | ------------: |
| Usługi   | `address`     |           387 |
| Usługi   | `source_name` |            21 |
| Uczelnie | `source_name` |             1 |

Wskazane braki dotyczą pól opcjonalnych i nie powodują odrzucenia danych.

Wynik audytu: **PASS**.

Raport: `data/test/audit-report.json`.

## 9. Powtarzalność procesu

Porównano dwa uruchomienia procedury na tej samej próbce i konfiguracji. Po pierwszym uruchomieniu zachowano kopie w data/test/repeatability-reference/, usunięto wyłącznie dwa wygenerowane pliki z data/processed/ i odtworzono je skryptem.

| Plik | Pierwszy wynik | Drugi wynik | Te same pola i wartości |
|---|---:|---:|---|
| services.json | 500 | 500 | tak |
| universities.json | 28 | 28 | tak |

Pliki porównano po uporządkowaniu rekordów według ID, bez tolerancji liczbowej: nie wprowadzamy obliczeń przybliżonych.

Dane wejściowe i konfiguracja niezmienione: tak. Wyniki kontroli jakości identyczne: tak.

Wynik: **PASS**. Raport: data/test/repeatability-report.json.


## 10. Ograniczenia

Automatyczne kontrole potwierdzają zgodność danych z zaimplementowanymi regułami, ale nie gwarantują pełnej zgodności z aktualnym stanem miasta.

W szczególności:

* część obiektów nie posiada nazw lub adresów;
* współrzędne nie zawsze wskazują wejścia do budynków;
* dane OSM mogą być niekompletne lub nieaktualne;
* nie przeprowadzono pełnej terenowej weryfikacji wszystkich obiektów;
* przygotowanie 25 obszarów mieszkalnych stanowi odrębny etap projektu.

Przed końcową prezentacją należy zweryfikować aktualność i kompletność danych istotnych dla działania systemu.

## 11. Odpowiedzialność

* **Valentyna Boksha** — pozyskanie danych OSM oraz przygotowanie konfiguracji wyboru lokalizacji.
* **Serhii Popovych** — przygotowanie skryptu przetwarzania danych.
* **Dana Stadnyk** — automatyczne kontrole jakości, testy na błędnych danych i dodatkowy audyt.
* **Paulina Michalska** — niezależna weryfikacja powtarzalności procesu, zgodnie z podziałem zadań zespołu.

## 12. Dobór narzędzi i decyzje

- Źródło i format danych: zapisane odpowiedzi Overpass API w JSON UTF-8 oraz konfiguracja wyboru miejsc zajęć.
- Narzędzie główne: Python 3.10+ z biblioteką standardową.
- Dlaczego pasuje: obsługuje zagnieżdżony JSON i pozwala zapisać odczyt, transformacje i kontrole jako procedurę uruchamianą ponownie bez internetu i instalowania pakietów.
- Narzędzie pomocnicze: VS Code do odczytu plików i uruchamiania poleceń w terminalu.
- Wynik w repozytorium: skrypty, przetworzone pliki, raporty i dokumentacja.

| Krok | Operacja | Powód | Wpływ na dane |
|---|---|---|---|
| 1 | Spłaszczenie tagów i wybór kategorii usług | Prosta struktura do aplikacji | 500 obiektów wejściowych i 500 usług wynikowych. |
| 2 | Normalizacja tekstu i etykiety dla brakujących nazw | Czytelne nazwy bez ukrywania braków | 21 usług otrzymuje etykietę; source_name i name_missing zachowują pochodzenie. |
| 3 | Wybór miejsc zajęć według konfiguracji | Ograniczenie do przyjętego zakresu | 105 obiektów uczelnianych przekształcono w 28 wybranych lokalizacji. |
| 4 | Uzupełnienie E4 i WSPiA ze źródłami | Nazwa i adres potrzebne w formularzu | Uzupełniono nazwę E4 i adres WSPiA; dane raw pozostają bez zmian. |
| 5 | Sortowanie według ID | Stabilne porównanie wyników | Zmienia kolejność, nie wartości rekordów. |

Decyzja analityczna: zachowujemy usługi bez adresów, ponieważ do obliczania odległości służą współrzędne. Nie przypisujemy fikcyjnych nazw własnych.

Nie można jeszcze wskazać rzeczywistego czasu dojścia ani porównać docelowych okolic: brakuje wybranych środków obszarów i zweryfikowanych tras pieszych. Kontrole zakresów współrzędnych nie potwierdzają przebiegu trasy.

Nie przygotowano wykresu: na tym etapie nie analizujemy rozkładu pomiaru ilościowego. Zamiast niego wykonano kontrole kompletności, kategorii i współrzędnych opisane w audycie.
