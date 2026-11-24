# Pomiar niefunkcjonalny — czas generowania rankingu (Lab 7)

Kryterium akceptacji ustalono **przed** pomiarem:

> Mediana czasu obliczenia rankingu wynosi **≤ 100 ms** przy 100 powtórzeniach,
> 25 obszarach mieszkalnych i 500 usługach.

Mierzony jest wyłącznie czas wywołania `RecommendationEngine.recommend()`.
Wczytywanie plików JSON, walidacja dokumentów i budowa silnika odbywają się
przed pomiarem i nie wchodzą do wyniku.

## Wynik

| Miara | Wartość |
|---|---|
| Mediana | **16,000 ms** |
| Minimum | 15,748 ms |
| Maksimum | 17,090 ms |
| Liczba powtórzeń | 100 |
| Kryterium (mediana ≤ 100 ms) | **SPEŁNIONE** |

TOP 3 dla przyjętych parametrów: Tadeusza Boya-Żeleńskiego (Staroniwa),
Strażacka (Drabinianka), Stanisława Staszica (Podpromie).

Pełne wyjście skryptu: `results/lab7/benchmark-output.txt`.

## Warunki pomiaru

| Element | Wartość |
|---|---|
| Data | 24.11.2026 |
| Commit badanego kodu | `ed0366c` (`main`); gałąź `serhii-lab7-lab6` bez zmian w silniku |
| Polecenie | `/opt/homebrew/bin/python3 scripts/benchmark_recommendation.py --repetitions 100` |
| Sprzęt | Apple M1 Max, 10 rdzeni CPU, 32 GB RAM |
| System | macOS 27.2.1, build 26B131 |
| Python | 3.15.2 (`/opt/homebrew/bin/python3`) |
| Obciążenie | średnia 1/5/15 min: 7,40 / 9,43 / 9,88 (przed i po pomiarze) |
| Parametry | lokalizacja `way/197227711` (PRz, Budynek P), limit 30 min, wagi uczelnia 3 / sklep 2 / przystanek 2 / park 2 |
| Dane | 500 usług, 28 lokalizacji uczelni, 25 obszarów o promieniu 500 m |
| Zakres pomiaru | tylko `recommend()`; bez wczytywania i walidacji plików |

Obciążenie maszyny było wysokie (ok. 7 na 10 rdzeni), więc czasy są górnym
oszacowaniem dla tego sprzętu. Nawet w tych warunkach mediana jest ponad
sześciokrotnie niższa od kryterium.

## Powtarzalność

Pomiar obejmuje 100 kolejnych wywołań na jednym obiekcie silnika. Skrypt podaje
medianę, minimum i maksimum; rozrzut wyniósł 1,342 ms. Powtórzenie pomiaru
o 9:51 (obciążenie 4,22) dało medianę 15,728 ms, minimum 15,671 ms, maksimum
16,155 ms i ten sam ranking TOP 3.
