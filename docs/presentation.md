# Scenariusz prezentacji i demonstracji systemu (Demo Script)

**Czas trwania prezentacji:** ok. 7–10 minut  
**Cel:** Przedstawienie problemu, architektury, działania aplikacji na żywo oraz wniosków z testów i eksperymentów.

---

## Część 1: Wprowadzenie do problemu i danych (ok. 1,5 min — Paulina)
* **Problem:** Studenci przyjeżdżający do Rzeszowa mają trudność z wyborem osiedla, które łączy szybki dojazd na konkretny wydział z dobrym dostępem do sklepów, przystanków i terenów zielonych.
* **Dane:** Wykorzystaliśmy rzeczywiste dane z OpenStreetMap (Overpass API) dla Rzeszowa:
  * **28 lokalizacji uczelni** (Politechnika Rzeszowska, Uniwersytet Rzeszowski, WSIiZ i inne),
  * **500 punktów usługowych** w 3 kategoriach (`shop`, `bus_stop`, `park`),
  * **25 zdefiniowanych obszarów mieszkalnych** o promieniu 500 m w 20 osiedlach Rzeszowa.
* **Gwarancja jakości:** Dane przeszły automatyczną walidację schematu, współrzędnych WGS84 i test powtarzalności (`check_data.py`, `verify_repeatability.py`).

---

## Część 2: Architektura i kontrakt systemu (ok. 1,5 min — Paulina)
* **Decyzja architektoniczna:** Lekka aplikacja analityczna w Pythonie z interfejsem **Streamlit** działająca na plikach **JSON/CSV** (`docs/decisions/001-storage.md`). Przy 528 obiektach obliczenia in-memory wykonują się w milisekundach bez narzutu bazy SQL.
* **Podział na warstwy:**
  1. Warstwa danych (`data/`, `config/`),
  2. Bezstanowy silnik rekomendacji (`scripts/recommendation_engine.py`),
  3. Interfejs użytkownika Streamlit (`app.py`).

---

## Część 3: Demonstracja działania aplikacji na żywo (ok. 3 min — Dana / Serhii)

### Scenariusz 1 — Standardowe wyszukiwanie studenta (Przypadek pozytywny)
1. Wybór uczelni z listy rozwijanej (np. główny kampus Politechniki Rzeszowskiej lub budynek Uniwersytetu Rzeszowskiego — wymaganie **R1**).
2. Ustawienie wag preferencji: wysoki priorytet dla uczelni i przystanków, niższy dla parku (wymaganie **R2**).
3. Wybór maksymalnego czasu dojścia: **30 minut** (wymaganie **R3**).
4. **Pokazanie wyniku:**
   * Aplikacja wyświetla **TOP 3 rekomendowane okolice** posortowane malejąco według oceny punktowej `0–100` (wymaganie **R4**).
   * Wskazanie wygenerowanego **uzasadnienia** (konkretne odległości w metrach do najważniejszych usług) oraz adnotacji o liczeniu odległości w linii prostej od środka koła 500 m (wymaganie **R5**).
   * Prezentacja okręgów o promieniu 500 m na interaktywnej mapie Rzeszowa.

### Scenariusz 2 — Przypadek brzegowy: Zbyt restrykcyjny limit czasu (Wymaganie R3)
1. Zmiana maksymalnego czasu dojścia na bardzo restrykcyjną wartość (np. **5 minut** lub **1 minuta**).
2. **Pokazanie wyniku:** System nie zgłasza błędu technicznego, lecz poprawnie filtruje wszystkie 25 obszarów i wyświetla czytelny komunikat o braku dopasowań w zadanym czasie.

---

## Część 4: Testy, wydajność i podsumowanie (ok. 1,5 min — Valentyna / Paulina)
* **Testy automatyczne:** Pokazanie uruchomienia zestawu testów jednostkowych (`python3 -m unittest discover -s tests`) oraz skryptu wydajności (`scripts/benchmark_recommendation.py`).
* **Ograniczenia i rozwój:** Odległości liczone są w linii prostej (prędkość 80 m/min = 4,8 km/h); w przyszłości system można rozbudować o routing po sieci chodników (OSRM) oraz dane o cenach najmu.