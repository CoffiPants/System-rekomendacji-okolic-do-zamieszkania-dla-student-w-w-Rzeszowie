# Laboratorium 4 — Porównanie metod wyszukiwania usług i rekomendacji okolic

## 1. Problem i pytanie badawcze

**Projekt:** System rekomendacji okolic do zamieszkania dla studentów w Rzeszowie.

**Pytanie badawcze:**

Czy wstępne filtrowanie przestrzenne przyspiesza wyszukiwanie usług znajdujących się w określonym promieniu od lokalizacji uczelni w porównaniu z pełnym przeszukiwaniem wszystkich obiektów?

**Cel eksperymentu:**

Porównanie wydajności dwóch algorytmów wyszukiwania pobliskich usług:

- M1 — brute force (metoda bazowa).
- M2 — bounding box (metoda alternatywna).

Eksperyment jest związany z funkcjonalnością systemu rekomendacji okolic, w którym dostępność sklepów, przystanków komunikacji miejskiej i parków stanowi jedno z kryteriów oceny lokalizacji.

Badanie dotyczy wydajności wyszukiwania usług, a nie jakości końcowego rankingu okolic mieszkalnych.

**Powiązanie z wymaganiami projektu:** dostępność usług w pobliżu analizowanej lokalizacji, zgodnie z opisem problemu w `docs/problem.md`.

## 2. Dane wejściowe

W eksperymencie wykorzystano dane przygotowane i zweryfikowane w ramach Laboratorium 3.

| Plik | Zawartość | Liczba rekordów |
|---|---|---:|
| `data/processed/services.json` | Sklepy, przystanki i parki | 500 |
| `data/processed/universities.json` | Lokalizacje uczelni | 28 |

Struktura zbioru usług:

| Kategoria | Liczba |
|---|---:|
| Sklepy | 274 |
| Przystanki autobusowe | 185 |
| Parki | 41 |
| **Razem** | **500** |

Każdy obiekt posiada współrzędne geograficzne umożliwiające obliczenie odległości.

Łącznie analizowano 28 lokalizacji uczelni i 500 obiektów usługowych.

Pliki wejściowe nie były modyfikowane podczas eksperymentu.

## 3. Porównywane metody

### 3.1. M1 — Brute force (baseline)

Metoda brute force polega na sprawdzeniu wszystkich obiektów usługowych dla każdej lokalizacji uczelni.

Algorytm:

1. Wybiera lokalizację uczelni.
2. Pobiera wszystkie 500 obiektów usługowych.
3. Oblicza odległość do każdego obiektu.
4. Sprawdza, czy odległość mieści się w zadanym promieniu.
5. Zwraca identyfikatory znalezionych obiektów.
6. Powtarza procedurę dla kolejnych lokalizacji.

Metoda nie stosuje wcześniejszego filtrowania.

Liczba obliczeń odległości:

28 × 500 = **14 000**

Zaletą metody jest prostota implementacji.

Wadą jest konieczność obliczania odległości do wszystkich obiektów, również tych znajdujących się daleko od analizowanej lokalizacji.

### 3.2. M2 — Bounding box

Metoda bounding box wykorzystuje wstępne filtrowanie przestrzenne.

Algorytm:

1. Wybiera lokalizację uczelni.
2. Wyznacza prostokątny obszar geograficzny obejmujący zadany promień.
3. Odrzuca obiekty znajdujące się poza wyznaczonym obszarem.
4. Oblicza dokładną odległość do pozostałych kandydatów.
5. Wybiera obiekty znajdujące się w zadanym promieniu.
6. Powtarza procedurę dla kolejnych lokalizacji.

Dzięki temu liczba dokładnych obliczeń odległości może być mniejsza.

Obie metody wykorzystują tę samą funkcję obliczania odległości na podstawie wzoru Haversine.

### 3.3. Warunek poprawności

Warunkiem porównania jest uzyskanie identycznych wyników wyszukiwania.

Program porównuje posortowane identyfikatory znalezionych usług dla każdej z 28 lokalizacji.

Jeżeli wyniki metod są różne, program zgłasza błąd.

Dzięki temu porównanie wydajności nie odbywa się kosztem poprawności wyszukiwania.

## 4. Metodyka eksperymentu

### 4.1. Parametry

| Parametr | Eksperyment podstawowy | Próba wrażliwości |
|---|---|---|
| Liczba lokalizacji | 28 | 28 |
| Liczba usług | 500 | 500 |
| Promień wyszukiwania | 1000 m | 1500 m |
| Liczba powtórzeń | 100 | 100 |
| Metody | Brute force, bounding box | Brute force, bounding box |

Jedynym zmienianym parametrem w próbie wrażliwości był promień wyszukiwania.

### 4.2. Pomiar czasu

Do pomiaru czasu wykorzystano funkcję:

`time.perf_counter_ns()`

Dla każdej metody wykonano 100 powtórzeń.

Mierzono czas wyszukiwania dla wszystkich 28 lokalizacji.

Pomiar nie obejmował:

- Wczytywania plików JSON.
- Zapisywania wyników do CSV.
- Wstępnej kontroli zgodności wyników.

Kolejność uruchamiania metod była zmieniana naprzemiennie między powtórzeniami.

Jako główną miarę czasu przyjęto medianę ze 100 pomiarów.

Dodatkowo zapisano minimalny i maksymalny czas wykonania.

### 4.3. Mierzone wskaźniki

W eksperymencie analizowano:

1. Medianę czasu wykonania w milisekundach.
2. Minimalny czas wykonania.
3. Maksymalny czas wykonania.
4. Liczbę obliczeń dokładnej odległości.
5. Liczbę znalezionych dopasowań.
6. Zgodność wyników obu metod.

### 4.4. Kryterium oceny

Metoda alternatywna jest uznawana za korzystniejszą w badanych warunkach, jeżeli:

- Zwraca identyczne wyniki jak metoda bazowa.
- Uzyskuje krótszy czas wykonania.
- Ogranicza liczbę dokładnych obliczeń odległości.

## 5. Implementacja i uruchomienie

Eksperyment zaimplementowano w języku Python.

**Plik programu:**

`scripts/compare_methods.py`

Program wykorzystuje standardową bibliotekę Pythona i nie wymaga instalowania dodatkowych pakietów.

Wymagana wersja: Python 3.10 lub nowszy.

### 5.1. Eksperyment podstawowy

W katalogu głównym repozytorium należy uruchomić:

```bash
py scripts/compare_methods.py --radius 1000 --repetitions 100
```

### 5.2. Próba wrażliwości

```bash
py scripts/compare_methods.py --radius 1500 --repetitions 100 --sensitivity
```

Na systemach, na których polecenie `py` nie jest dostępne, można użyć `python`.

## 6. Pliki wynikowe

Wyniki eksperymentu zostały zapisane w katalogu:

`results/lab4/`

Struktura:

```text
results/
└── lab4/
    ├── observations.csv
    ├── comparison.csv
    └── sensitivity/
        ├── observations.csv
        └── comparison.csv
```

Opis plików:

| Plik | Zawartość |
|---|---|
| `observations.csv` | Pojedyncze pomiary czasu |
| `comparison.csv` | Zestawienie wyników eksperymentu podstawowego |
| `sensitivity/observations.csv` | Pomiary dla promienia 1500 m |
| `sensitivity/comparison.csv` | Zestawienie wyników próby wrażliwości |

Dane wejściowe i wyniki eksperymentu są przechowywane oddzielnie.

## 7. Kontrola poprawności

### 7.1. Kontrola automatyczna

Program automatycznie porównuje identyfikatory obiektów znalezionych przez obie metody.

Dla obu promieni wyszukiwania uzyskano:

**Zgodność wyników: TAK**

Oznacza to, że w przeprowadzonych eksperymentach obie metody zwróciły identyczne zestawy obiektów.

### 7.2. Ręczna kontrola liczby obliczeń

Dla metody brute force można niezależnie wyznaczyć liczbę obliczeń odległości.

Liczba lokalizacji uczelni: **28**

Liczba obiektów usługowych: **500**

Obliczenie:

28 × 500 = **14 000**

Wynik programu: **14 000**

Wynik obliczony ręcznie jest zgodny z wynikiem programu.

### 7.3. Kontrola liczby dopasowań

Dla promienia 1000 m:

- Brute force: 1084 dopasowania.
- Bounding box: 1084 dopasowania.

Dla promienia 1500 m:

- Brute force: 2182 dopasowania.
- Bounding box: 2182 dopasowania.

Liczba dopasowań oznacza łączną liczbę par lokalizacja–usługa spełniających warunek odległości dla wszystkich 28 lokalizacji. Ta sama usługa może zostać uwzględniona przy więcej niż jednej lokalizacji uczelni.

Zgodność liczby dopasowań stanowi dodatkowe potwierdzenie spójności wyników.

Sama zgodność liczby dopasowań nie gwarantuje jednak zgodności identyfikatorów, dlatego program sprawdza również pełne zestawy wyników.

### 7.4. Ograniczenie kontroli ręcznej

Przeprowadzona ręczna kontrola potwierdza poprawność liczby operacji w metodzie brute force.

Nie stanowi ona niezależnej weryfikacji wartości odległości obliczonej wzorem Haversine.

Dodatkowa kontrola konkretnej pary lokalizacja–usługa może zostać przeprowadzona poprzez niezależne obliczenie odległości na podstawie współrzędnych zapisanych w plikach wejściowych.

## 8. Wyniki i interpretacja

### 8.1. Eksperyment podstawowy — promień 1000 m

Eksperyment przeprowadzono na zbiorze 500 obiektów usługowych oraz 28 lokalizacji uczelni.

Każdą metodę uruchomiono 100 razy.

| Metryka | Brute force | Bounding box |
|---|---:|---:|
| Mediana czasu wykonania | 8,836900 ms | 1,807050 ms |
| Minimalny czas | 8,405000 ms | 1,718500 ms |
| Maksymalny czas | 12,890300 ms | 2,884200 ms |
| Liczba obliczeń odległości | 14 000 | 1 370 |
| Liczba dopasowań | 1 084 | 1 084 |
| Zgodność wyników | TAK | TAK |

**Porównanie wydajności:**

Stosunek median czasu:

8,836900 / 1,807050 ≈ **4,89**

Metoda bounding box była około **4,89 razy szybsza** od metody brute force.

Zmniejszenie liczby obliczeń odległości:

(14 000 − 1 370) / 14 000 × 100% ≈ **90,2%**

Wstępne filtrowanie ograniczyło liczbę dokładnych obliczeń odległości o około **90,2%**.

Obie metody zwróciły identyczne wyniki.

### 8.2. Próba wrażliwości — promień 1500 m

W drugim eksperymencie zmieniono promień wyszukiwania z 1000 m na 1500 m.

Liczba lokalizacji, zbiór usług i liczba powtórzeń pozostały bez zmian.

| Metryka | Brute force | Bounding box |
|---|---:|---:|
| Mediana czasu wykonania | 8,726450 ms | 2,761850 ms |
| Minimalny czas | 8,483100 ms | 2,662300 ms |
| Maksymalny czas | 12,309400 ms | 3,465400 ms |
| Liczba obliczeń odległości | 14 000 | 2 783 |
| Liczba dopasowań | 2 182 | 2 182 |
| Zgodność wyników | TAK | TAK |

**Porównanie wydajności:**

Stosunek median czasu:

8,726450 / 2,761850 ≈ **3,16**

Metoda bounding box była około **3,16 razy szybsza** od metody brute force.

Zmniejszenie liczby obliczeń odległości:

(14 000 − 2 783) / 14 000 × 100% ≈ **80,1%**

Wstępne filtrowanie ograniczyło liczbę dokładnych obliczeń odległości o około **80,1%**.

Obie metody ponownie zwróciły identyczne wyniki.

### 8.3. Porównanie obu eksperymentów

| Wskaźnik | Promień 1000 m | Promień 1500 m |
|---|---:|---:|
| Mediana brute force | 8,836900 ms | 8,726450 ms |
| Mediana bounding box | 1,807050 ms | 2,761850 ms |
| Przyspieszenie bounding box | 4,89× | 3,16× |
| Obliczenia odległości — brute force | 14 000 | 14 000 |
| Obliczenia odległości — bounding box | 1 370 | 2 783 |
| Liczba dopasowań | 1 084 | 2 182 |

Zwiększenie promienia wyszukiwania spowodowało wzrost liczby obiektów znajdujących się w badanym obszarze.

W metodzie brute force liczba obliczeń odległości pozostała niezmieniona i wynosiła 14 000.

W metodzie bounding box liczba dokładnych obliczeń wzrosła z 1370 do 2783.

W rezultacie przewaga czasowa metody bounding box zmniejszyła się.

### 8.4. Wnioski

Na podstawie przeprowadzonych eksperymentów stwierdzono, że:

1. Metoda bounding box była szybsza od metody brute force w obu badanych wariantach.
2. Obie metody zwróciły identyczne wyniki wyszukiwania.
3. Wstępne filtrowanie przestrzenne znacząco ograniczyło liczbę dokładnych obliczeń odległości.
4. Zwiększenie promienia wyszukiwania zmniejszyło przewagę wydajnościową metody bounding box.
5. W badanym zbiorze danych bounding box jest korzystniejszym rozwiązaniem do wyszukiwania usług w określonym promieniu.

Eksperyment potwierdza, że zastosowanie prostego filtrowania przestrzennego może poprawić wydajność wyszukiwania obiektów w systemie rekomendacji okolic.

## 9. Ograniczenia eksperymentu

Eksperyment posiada następujące ograniczenia:

- Wykorzystano stosunkowo niewielki zbiór 500 usług i 28 lokalizacji.
- Czasy wykonania zależą od wydajności komputera i obciążenia systemu.
- Porównano dwa promienie wyszukiwania: 1000 m i 1500 m.
- Odległość obliczana wzorem Haversine nie uwzględnia rzeczywistej sieci dróg i tras pieszych.
- Współrzędne obiektów OpenStreetMap mogą wskazywać środek geometrii, a nie dokładne wejście do obiektu.
- Badanie dotyczy wyszukiwania usług w pobliżu uczelni, a nie pełnego rankingu okolic mieszkalnych.
- Wyniki nie muszą być identyczne dla znacznie większych baz danych.

W przyszłości możliwe jest porównanie metody bounding box z rozwiązaniami wykorzystującymi indeksy przestrzenne.

## 10. Źródła i uzasadnienie metod

### Źródło 1 — dokumentacja Python

Python Software Foundation, *time — Time access and conversions*, dokumentacja języka Python.

Adres: https://docs.python.org/3/library/time.html#time.perf_counter_ns

Dostęp: 03.11.2026.

**Zastosowanie:**

Dokumentacja opisuje funkcję `time.perf_counter_ns()`, która umożliwia pomiar krótkich odcinków czasu z wysoką rozdzielczością.

Na tej podstawie zastosowano ją do pomiaru czasu wykonywania obu algorytmów.

### Źródło 2 — obliczanie odległości geograficznej

Sinnott R. W., *Virtues of the Haversine*, Sky & Telescope, 1984, tom 68, nr 2, s. 159.

**Zastosowanie:**

Publikacja dotyczy wykorzystania funkcji Haversine w obliczeniach odległości na powierzchni kuli.

Na tej podstawie wykorzystano wzór Haversine do obliczania odległości pomiędzy współrzędnymi geograficznymi.

### Uzasadnienie wyboru metod

Metoda brute force została wybrana jako punkt odniesienia ze względu na prostotę i możliwość pełnego sprawdzenia wszystkich obiektów.

Metoda bounding box została wybrana jako alternatywa umożliwiająca ograniczenie liczby dokładnych obliczeń odległości.

W eksperymencie nie wykorzystano zaawansowanych indeksów przestrzennych, ponieważ celem było porównanie dwóch prostych metod możliwych do implementacji bez dodatkowych bibliotek.

## 11. Odpowiedzialność i odtwarzalność

**Osoba odpowiedzialna za eksperyment:** Dana Stadnyk.

Zakres wykonanej pracy:

- Przygotowanie eksperymentu porównawczego.
- Implementacja metod wyszukiwania.
- Przeprowadzenie pomiarów czasu.
- Weryfikacja zgodności wyników.
- Wykonanie próby wrażliwości.
- Analiza wyników.
- Przygotowanie dokumentacji.

Eksperyment można odtworzyć za pomocą poleceń podanych w sekcji 5.

Niezależna weryfikacja przez drugiego członka zespołu pozostaje do wykonania.

Wyniki czasowe mogą różnić się pomiędzy komputerami, natomiast liczba znalezionych obiektów i zgodność wyników powinny pozostać takie same przy wykorzystaniu identycznych danych i parametrów.

## 12. Porównanie dwóch technik rekomendacji okolic mieszkalnych

### 12.1. Cel eksperymentu

Celem eksperymentu było porównanie dwóch różnych technik rozwiązywania problemu rekomendacji okolic do zamieszkania dla studentów w Rzeszowie.

Porównano:

1. **Weighted Scoring** — metodę punktową opartą na ważonej sumie ocen poszczególnych kryteriów.
2. **KNN (k-Nearest Neighbors)** — metodę opartą na podobieństwie charakterystyk okolic do profilu preferencji studenta.

Eksperyment miał umożliwić wybór techniki do dalszej implementacji systemu.

### 12.2. Dane wejściowe

Wykorzystano dane przygotowane w poprzednich etapach projektu:

- 25 lokalizacji mieszkalnych w Rzeszowie;
- 500 obiektów usługowych;
- 28 lokalizacji uczelni.

Dla każdej okolicy wyznaczono oceny w skali 0–100 dotyczące czterech kryteriów:

- bliskości uczelni;
- dostępności sklepów;
- dostępności przystanków autobusowych;
- dostępności parków.

Oceny obliczono na podstawie odległości geograficznych między lokalizacjami.

### 12.3. Technika 1 — Weighted Scoring

Weighted Scoring polega na obliczeniu łącznej oceny okolicy na podstawie ocen poszczególnych kryteriów oraz przypisanych im wag.

Wzór:

**S = (w₁x₁ + w₂x₂ + w₃x₃ + w₄x₄) / (w₁ + w₂ + w₃ + w₄)**

gdzie:

- S — końcowa ocena okolicy;
- x₁, x₂, x₃, x₄ — oceny czterech kryteriów;
- w₁, w₂, w₃, w₄ — wagi określające znaczenie kryteriów.

Okolice są sortowane malejąco według końcowej oceny. Najwyższy wynik oznacza najlepszą rekomendację według przyjętych wag.

**Zalety:** prostota, przejrzystość wyników, możliwość personalizacji wag.

**Ograniczenia:** wynik zależy od przyjętych wag i sposobu punktowania kryteriów.

### 12.4. Technika 2 — KNN

W projekcie zastosowano podejście oparte na wyszukiwaniu najbliższych sąsiadów w przestrzeni cech.

Każda okolica jest reprezentowana przez cztery oceny, a profil studenta określa pożądane wartości tych ocen.

Dla każdej okolicy obliczana jest ważona odległość euklidesowa od profilu studenta:

**d = √[Σ wᵢ((xᵢ − pᵢ)/100)²]**

gdzie:

- d — odległość między okolicą a profilem studenta;
- xᵢ — ocena danego kryterium dla okolicy;
- pᵢ — oczekiwana ocena kryterium;
- wᵢ — waga kryterium.

Następnie wybierane są trzy okolice o najmniejszej odległości.

W tym wariancie KNN nie wymaga trenowania klasyfikatora. Jest wykorzystywany do wyszukiwania lokalizacji najbardziej podobnych do określonego profilu preferencji.

**Zalety:** możliwość wyszukiwania okolic podobnych do indywidualnego profilu studenta.

**Ograniczenia:** wyniki zależą od sposobu określenia profilu, skalowania cech i przyjętej miary odległości.

### 12.5. Scenariusze eksperymentalne

Przeprowadzono porównanie dla trzech profili preferencji:

| Profil | Charakterystyka |
|---|---|
| Balanced | Zrównoważone uwzględnienie różnych potrzeb studenta |
| University priority | Większy nacisk na bliskość uczelni |
| Services priority | Większy nacisk na dostępność usług |

Dla każdego profilu porównano trzy najwyżej ocenione okolice uzyskane obiema metodami.

### 12.6. Wyniki porównania

| Profil | TOP 1 Weighted Scoring | TOP 1 KNN | Zgodność TOP 3 |
|---|---|---|---|
| Balanced | Krakowska-Południe | Krakowska-Południe | 2/3 |
| University priority | Krakowska-Południe | Krakowska-Południe | 2/3 |
| Services priority | Drabinianka 1 | Drabinianka 1 | 2/3 |

W każdym scenariuszu obie techniki wskazały tę samą okolicę na pierwszym miejscu.

Jednocześnie wśród trzech najlepszych rekomendacji występowały różnice. Dla każdego profilu dwie z trzech rekomendowanych okolic były wspólne.

Wyniki potwierdzają, że obie techniki mogą generować podobne rekomendacje, ale wykorzystują odmienne zasady wyznaczania rankingu.

### 12.7. Porównanie wydajności

Przeprowadzono dodatkowy eksperyment mierzący czas wykonania obu metod.

**Parametry:**

- liczba analizowanych okolic: 25;
- liczba powtórzeń: 1000;
- miara czasu: mediana;
- jednostka: milisekundy.

| Metoda | Mediana czasu |
|---|---:|
| Weighted Scoring | 0,017700 ms |
| KNN | 0,037400 ms |

Stosunek czasów wykonania:

0,037400 / 0,017700 ≈ **2,11**

Weighted Scoring był około 2,11 razy szybszy od KNN w przeprowadzonym pomiarze.

Pomiar obejmował wyłącznie obliczanie rankingów na przygotowanych danych. Nie uwzględniał czasu pobierania danych ani wyznaczania odległości geograficznych.

Ze względu na niewielki zbiór danych i bardzo krótkie czasy wykonania wynik ten należy interpretować jako porównanie wydajności w konkretnym środowisku testowym, a nie uniwersalną przewagę jednej metody.

### 12.8. Kontrola poprawności

Przygotowano trzy automatyczne testy dla implementacji KNN.

Wynik uruchomienia:

**Ran 3 tests — OK**

Wszystkie trzy testy zakończyły się pomyślnie.

Dodatkowo porównano wyniki obu technik dla trzech profili preferencji studentów.

Zgodność pierwszej rekomendacji wyniosła 3/3, natomiast zgodność zbiorów TOP 3 wyniosła 2/3 dla każdego profilu.

Zgodność rankingów nie stanowi jednak niezależnego potwierdzenia jakości rekomendacji. Do takiej oceny potrzebne byłyby dodatkowe dane, np. opinie studentów.

### 12.9. Wybór techniki do dalszej implementacji

Na podstawie przeprowadzonego porównania wybrano **Weighted Scoring** jako technikę do dalszej implementacji systemu rekomendacji.

Uzasadnienie:

1. Krótszy czas obliczania rankingu w przeprowadzonym eksperymencie.
2. Przejrzysty sposób obliczania końcowej oceny.
3. Możliwość łatwego wyjaśnienia użytkownikowi, dlaczego dana okolica otrzymała określoną liczbę punktów.
4. Możliwość personalizacji rekomendacji poprzez zmianę wag kryteriów.
5. Brak konieczności przygotowania danych treningowych.

KNN pozostaje alternatywną techniką, którą można rozwijać w przyszłości.

### 12.10. Ograniczenia

- Eksperyment przeprowadzono dla 25 lokalizacji mieszkalnych.
- Wykorzystano trzy przykładowe profile preferencji.
- Wyniki zależą od przyjętych ocen, wag i profili.
- Nie przeprowadzono badania satysfakcji użytkowników.
- Nie wykorzystano danych o rzeczywistych wyborach mieszkaniowych studentów.
- Porównanie czasu obejmowało tylko etap obliczania rankingów.

### 12.11. Implementacja i odtwarzalność

Implementacja została przygotowana w języku Python.

Wykorzystane skrypty:

- `scripts/compare_methods.py` — przygotowanie ocen okolic i wcześniejsze porównanie rankingów;
- `scripts/knn_recommender.py` — implementacja KNN;
- `scripts/compare_knn_weighted.py` — porównanie Weighted Scoring i KNN;
- `scripts/test_knn.py` — automatyczne testy KNN;
- `scripts/benchmark_knn_weighted.py` — pomiar czasu wykonania obu technik.

Polecenia uruchomienia:

`py scripts/compare_methods.py`

`py scripts/compare_knn_weighted.py`

`py scripts/test_knn.py`

`py scripts/benchmark_knn_weighted.py`

Wyniki porównania rankingów zapisano w katalogu:

`results/lab4/knn/`

Znajdują się tam pliki `comparison.csv` i `rankings.csv`.

### 12.12. Wniosek końcowy

Przeprowadzony eksperyment pozwolił porównać dwie różne techniki rekomendacji okolic mieszkalnych dla studentów.

Obie techniki wskazały identyczne najlepsze okolice dla trzech badanych profili, jednak różniły się pozostałymi pozycjami w rankingach.

Weighted Scoring uzyskał krótszy czas wykonania i zapewnia prostszą interpretację wyników.

Dlatego został wybrany jako podstawowa technika do dalszego rozwoju systemu rekomendacji okolic do zamieszkania dla studentów w Rzeszowie.