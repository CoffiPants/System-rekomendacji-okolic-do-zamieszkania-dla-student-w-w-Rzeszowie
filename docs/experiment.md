# Laboratorium 4 — Porównanie dwóch metod wyszukiwania usług

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