# Architektura systemu — Laboratorium 5

## 1. Wybór architektury
System rekomendacji okolic zamieszkania dla studentów w Rzeszowie został zaprojektowany w architekturze **modułu analitycznego (CLI / skrypty Python)** przetwarzającego dane z plików **JSON/CSV**.

### Uzasadnienie wyboru
* Dane źródłowe (OpenStreetMap) oraz przetworzone (usługi i uczelnie) są już zapisane w spójnym formacie JSON.
* Skala danych (528 obiektów) nie wymaga narzutu relacyjnej bazy danych ani infrastruktury sieciowej REST API.
* Wszystkie obliczenia (Weighted Scoring, KNN) wykonywane są in-memory w języku Python.

---

## 2. Przypadek użycia: UC-01 — Generowanie rekomendacji okolic dla studenta

* **Aktor główny:** Student szukający mieszkania.
* **Cel:** Otrzymanie rankingu najlepszych okolic mieszkalnych na podstawie wybranych preferencji i ograniczeń czasowych.
* **Powiązane wymagania:** 
  * R1 (Wybór budynku uczelni)
  * R2 (Wagi preferencji otoczenia)
  * R3 (Obliczanie czasu dojścia i filtr maksymalnego czasu)
  * R4 (Ranking do 3 najlepszych okolic)
  * R5 (Uzasadnienie ocen i ograniczeń)
  * R6 (Zakres danych ograniczony do Rzeszowa)

### Przebieg główny
1. Student podaje budynek uczelni (miejsce zajęć), wagi dla usług (sklepy, przystanki, parki) oraz maksymalny dopuszczalny czas dojścia (np. 15, 30, 45 min).
2. System wczytuje dane o uczelniach (`universities.json`), usługach (`services.json`) oraz zdefiniowanych obszarach mieszkalnych (`residential-areas.json`).
3. System weryfikuje poprawność danych wejściowych.
4. System oblicza odległości w linii prostej i szacowany czas dojścia (przy prędkości 4,5 km/h).
5. Moduł filtrujący (powiązany z wymaganiem R3) odrzuca obszary, w których czas dojścia przekracza podany limit.
6. Silnik rekomendacji (Weighted Scoring / KNN) wylicza punkty dla pozostałych obszarów i sortuje je malejąco.
7. System zwraca ranking maksymalnie 3 najlepszych okolic wraz z uzasadnieniem punktacji i odległości.

### Przebieg alternatywny / Wyjątki
* **Brak dopasowań (R3):** Jeśli wszystkie obszary przekraczają limit czasu dojścia podany przez studenta, system wyświetla komunikat o braku wyników zamiast generować niepoprawne rekomendacje.
* **Brak danych o uczelni:** Jeśli wybrany budynek nie występuje w bazie `universities.json`, system zgłasza błąd walidacji.

---

## 3. Diagram sekwencji UML (Mermaid)

```mermaid
sequenceDiagram
    autonumber
    actor Student
    participant CLI as Interfejs / Skrypt
    participant Val as Moduł Walidacji
    participant Engine as Silnik Rekomendacji (KNN/Scoring)
    participant Data as Zbiory JSON

    Student->>CLI: Wybiera uczelnię, wagi i limit czasu (np. 30 min)
    CLI->>Data: Odczytuje universities.json, services.json, residential-areas.json
    Data-->>CLI: Zwraca obiekty JSON
    CLI->>Val: Przekazuje parametry i dane do weryfikacji
    alt Błąd danych lub brak uczelni
        Val-->>CLI: Błąd walidacji
        CLI-->>Student: Wyświetla komunikat o błędzie
    else Dane poprawne
        Val-->>CLI: Potwierdzenie poprawności
        CLI->>Engine: Przekazuje dane i parametry obliczeń
        Engine->>Engine: Oblicza odległości i czas dojścia (4.5 km/h)
        Engine->>Engine: Filtruje obszary przekraczające limit czasu (R3)
        alt Brak obszarów spełniających limit
            Engine-->>CLI: Brak wyników
            CLI-->>Student: Wyświetla komunikat o braku dopasowanych okolic
        else Znaleziono pasujące obszary
            Engine->>Engine: Oblicza punktację i tworzy TOP 3 ranking
            Engine-->>CLI: Zwraca wygenerowany ranking z uzasadnieniem
            CLI-->>Student: Prezentuje 3 najlepiej dopasowane okolice
        end
    end

graph TD
    A[data/raw & config/ JSON] -->|prepare_data.py| B[data/processed/ JSON]
    B -->|check_data.py| C{Weryfikacja jakości PASS?}
    C -->|Błędy| D[data/test/*-report.json]
    C -->|Tak| E[Moduł Rekomendacji]
    F[Preferencje studenta: Uczelnia, Wagi, Limit czasu R3] --> E
    E -->|Obliczenie odległości i filtrowanie czasu| G[Weryfikacja limitów czasu]
    G -->|Filtr R3: Czas > limit| H[Odrzucenie obszaru]
    G -->|Filtr R3: Czas <= limit| I[Obliczenie ocen Weighted Scoring / KNN]
    I --> J[results/ TOP 3 Rekomendacje CSV/JSON]

{
  "university_id": "way/208515700",
  "max_walk_time_minutes": 30,
  "weights": {
    "university": 3,
    "shop": 2,
    "bus_stop": 3,
    "park": 1
  }
}
{
  "status": "SUCCESS",
  "recommendations": [
    {
      "rank": 1,
      "area_id": "area_01",
      "area_name": "Nowe Miasto - Obszar A",
      "score": 84.5,
      "walk_time_to_univ_min": 18.2,
      "justification": "Wysoka dostępność przystanków i bliskość wybranego budynku UR."
    }
  ]
}