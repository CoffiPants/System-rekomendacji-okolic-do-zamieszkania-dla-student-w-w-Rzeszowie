# Scenariusz prezentacji i demonstracji systemu (Demo Script)

**Czas trwania prezentacji:** ok. 7–10 minut  
**Cel:** Przedstawienie problemu, architektury, działania aplikacji na żywo oraz wniosków z testów i eksperymentów.

---

## Część 1: Wprowadzenie do problemu i danych
- **Problem:** Studenci przyjeżdżający do Rzeszowa mają trudność z wyborem osiedla, które łączy szybki dojazd na konkretny wydział z dobrym dostępem do sklepów, przystanków i terenów zielonych.
- **Dane:** Wykorzystaliśmy rzeczywiste dane z OpenStreetMap (Overpass API) dla Rzeszowa:
  - **28 lokalizacji uczelni** (Politechnika Rzeszowska, Uniwersytet Rzeszowski, WSIiZ i inne),
  - **500 punktów usługowych** w 3 kategoriach (`shop`, `bus_stop`, `park`),
  - **25 zdefiniowanych obszarów mieszkalnych** o promieniu 500 m w 20 osiedlach Rzeszowa (etykiety nazw mają charakter orientacyjny — patrz `./area-name-audit.md`).
- **Gwarancja jakości:** Dane przeszły automatyczną kontrolę schematu, współrzędnych WGS84 i sprawdzenie powtarzalności (`scripts/check_data.py`, `scripts/verify_repeatability.py`) — kontrole te nie weryfikują kompletności opcjonalnych pól źródłowych OSM (np. braków nazw czy adresów).

---

## Część 2: Architektura i kontrakt systemu 
- **Decyzja architektoniczna:** Lekka aplikacja analityczna w Pythonie z interfejsem **Streamlit** działająca na plikach **JSON/CSV** (`./decisions/001-storage.md`). Przy 528 obiektach obliczenia in-memory wykonują się w milisekundach bez narzutu bazy SQL.
- **Podział na warstwy:**
  1. Warstwa danych (`data/`, `config/`),
  2. Bezstanowy silnik rekomendacji (`scripts/recommendation_engine.py`, publiczna funkcja `generate_recommendations()`),
  3. Interfejs użytkownika Streamlit (`app.py`, w tym eksport rankingu TOP 3 do pliku CSV).

---

## Część 3: Demonstracja działania aplikacji na żywo 

### Scenariusz 1 — Standardowe wyszukiwanie studenta (Przypadek pozytywny)
1. Wybór uczelni z listy rozwijanej (np. główny kampus Politechniki Rzeszowskiej lub budynek Uniwersytetu Rzeszowskiego — wymaganie **R1**).
2. Ustawienie wag preferencji w skali 1–3: wyższy priorytet dla uczelni i przystanków, niższy dla parku (wymaganie **R2**).
3. Wybór maksymalnego czasu dojścia: **30 minut** (spośród dostępnych w formularzu opcji: `15`, `30`, `45` min lub brak limitu — wymaganie **R3**).
4. **Pokazanie wyniku:**
  - Aplikacja wyświetla **TOP 3 rekomendowane okolice** posortowane malejąco według oceny punktowej `0–100` (wymaganie **R4**).
  - Wskazanie wygenerowanego **uzasadnienia** (`justification`) oraz adnotacji (`disclaimer`) o liczeniu odległości w linii prostej od środka koła 500 m przy prędkości `4,5 km/h` (`75 m/min`) (wymaganie **R5**).
  - Prezentacja okręgów o promieniu 500 m na interaktywnej mapie Rzeszowa oraz przycisku **„Pobierz ranking TOP 3 (CSV)”**.

### Scenariusz 2 — Przypadek brzegowy: Brak dopasowań przy limicie 15 minut (Wymaganie R3)
1. Wybór lokalizacji **WSIiZ, Sucharskiego 2** oraz ustawienie limitu czasu dojścia na **15 minut** (formularz udostępnia limity 15 / 30 / 45 min lub brak limitu; limit 15 min jest poprawną wartością wejściową, dla której przy tej lokalizacji żaden z 25 obszarów się nie łapie).
2. **Pokazanie wyniku:** System nie zgłasza błędu technicznego, lecz filtruje wszystkie 25 obszarów, zwraca status `NO_MATCHES` i wyświetla w interfejsie czytelny komunikat o braku okolic spełniających kryteria w zadanym czasie.

---

## Część 4: Testy, wydajność i podsumowanie 
- **Testy automatyczne:** Pokazanie uruchomienia zestawu testów jednostkowych i integracyjnych:
  ```bash
  python -m unittest discover -s tests -v
  ```
  oraz skryptu wydajności (`scripts/benchmark_recommendation.py` — pełny pomiar niefunkcjonalny całego przepływu ma status `NOT RUN`).
- **Ograniczenia i rozwój:** Odległości liczone są w linii prostej (prędkość `75 m/min = 4,5 km/h`); w przyszłości system można rozbudować o routing po sieci chodników (OSRM), dane o cenach najmu oraz rozkład jazdy komunikacji miejskiej.

---

## Przewidywane pytania i rekomendowane odpowiedzi
1. **Dlaczego czas dojścia jest liczony w linii prostej przy `4,5 km/h` zamiast trasą po chodnikach?**  
   System używa wzoru Haversine'a i stałej prędkości `75 m/min` (`4,5 km/h`) jako uproszczonego, deterministycznego przybliżenia w lekkiej architekturze bez zewnętrznego serwera routingu. Ograniczenie to jest jawnie podawane w `disclaimer` oraz w dokumentacji (`./report.md`, `./architecture.md`).
2. **Skąd biorą się różnice między etykietą nazwy obszaru a polem `district`?**  
   Etykiety w `config/residential-areas.json` mają charakter orientacyjny i były weryfikowane przez odwrotne geokodowanie w OpenStreetMap (`./area-name-audit.md`), bez modyfikacji `id`, `district` i współrzędnych.
3. **Jak działa eksport rankingu i jak wygląda kwestia pomiaru wydajności?**  
   Aplikacja udostępnia przycisk **„Pobierz ranking TOP 3 (CSV)”** dla bieżącego wyniku rekomendacji, natomiast pełny pomiar niefunkcjonalny całego przepływu ma status `NOT RUN` (w repozytorium znajduje się skrypt benchmarkowy `scripts/benchmark_recommendation.py`).

---

## Plan próby generalnej

- **Planowana kolejność wystąpień:** Paulina (części 1–2) → Dana / Serhii (część 3: scenariusz standardowy + przypadek `WSIiZ, Sucharskiego 2` z limitem `15 min`) → Valentyna / Paulina (część 4 i pytania).
- **Na co zwrócić uwagę:** formularz ma tylko limity 15 / 30 / 45 min lub brak limitu — nie próbować ustawiać innych wartości (np. 1 lub 5 min).

## Wynik próby generalnej (Dry Run)

Próba jeszcze się nie odbyła. Po próbie należy uzupełnić:

- **Data próby:**
- **Prezentowana wersja (tag / commit):**
- **Środowisko (komputer, system, przeglądarka):**
- **Łączny czas:**
- **Uwagi (co najmniej jedna konkretna):**
- **Wprowadzone poprawki:**
- **Wynik ponownego sprawdzenia:**
