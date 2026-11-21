# Dokumentacja implementacji — Laboratorium 6

## 1. Cel etapu i zakres wdrożenia
Celem Laboratorium 6 było przeniesienie projektu architektonicznego (`docs/architecture.md`) do działającej implementacji systemu rekomendacji okolic mieszkalnych dla studentów w Rzeszowie. System łączy warstwę analityczną w języku **Python** z interaktywnym interfejsem graficznym zbudowanym w bibliotece **Streamlit**.

---

## 2. Struktura kodu i organizacja modułów

Projekt zachowuje podział na warstwę danych, warstwę logiki analitycznej oraz warstwę prezentacji:

* `app.py` – główny plik interfejsu graficznego Streamlit (formularz preferencji, interaktywna mapa Rzeszowa, prezentacja i eksport rankingu TOP 3).
* `config/residential-areas.json` – definicja 25 obszarów mieszkalnych o promieniu 500 m w 20 osiedlach Rzeszowa.
* `data/raw/` – surowe zbiory pobrane z Overpass API (OpenStreetMap).
* `data/processed/` – oczyszczone zbiory wejściowe (`universities.json` – 28 lokalizacji, `services.json` – 500 punktów usługowych).
* `data/test/` – raporty walidacji jakości i powtarzalności danych.
* `scripts/prepare_data.py` – czyszczenie i normalizacja danych OSM do katalogu `data/processed/`.
* `scripts/check_data.py` – walidacja spójności, typów i współrzędnych.
* `scripts/audit_data.py` – audyt pokrycia przestrzennego i braków danych.
* `scripts/verify_repeatability.py` – weryfikacja determinizmu przetwarzania danych.
* `scripts/knn_recommender.py` – silnik rekomendacji oparty na algorytmie KNN.
* `scripts/compare_methods.py` i `scripts/compare_knn_weighted.py` – porównanie metod oceny obszarów.
* `scripts/benchmark_knn_weighted.py` – pomiar czasu wykonania i wydajności algorytmów.
* `results/` – wyeksportowane wyniki eksperymentów i rankingów w formacie CSV.
* `docs/` – kompletna dokumentacja projektowa (Lab 1 – Lab 8).

---

## 3. Realizacja wymagań funkcjonalnych (R1–R6)

Każde z wymagań zdefiniowanych w specyfikacji problemu zostało odwzorowane w kodzie aplikacji:

1. **R1 — Wybór budynku lub kampusu uczelni:**
   * Interfejs ładuje listę 28 lokalizacji z pliku `data/processed/universities.json` (m.in. Politechnika Rzeszowska, Uniwersytet Rzeszowski, WSIiZ) i udostępnia je na liście rozwijanej z przypisanym identyfikatorem `university_id`.
2. **R2 — Wagi preferencji otoczenia:**
   * Użytkownik określa ważność czterech kryteriów w skali całkowitej `1–3` (`1` – niska, `2` – średnia, `3` – wysoka) dla: odległości od uczelni (`university`), sklepów (`shop`), przystanków autobusowych (`bus_stop`) oraz terenów zielonych (`park`).
3. **R3 — Obliczanie czasu dojścia i filtr maksymalnego czasu:**
   * Odległość geograficzna pomiędzy środkiem każdego z 25 obszarów a wybraną uczelnią obliczana jest wzorem Haversine (w metrach, w linii prostej).
   * Szacowany czas marszu wyliczany jest przy stałej prędkości pieszego **4,5 km/h** (`75 m/min`): `czas_marszu [min] = odległość [m] / 75.0`.
   * Użytkownik wybiera maksymalny akceptowalny czas dojścia (`15 min`, `30 min`, `45 min` lub `Brak limitu`). Obszary niespełniające warunku `walk_time_to_univ_min <= max_walk_time_minutes` są odrzucane przed etapem rankingowania.
   * W przypadku odrzucenia wszystkich 25 obszarów aplikacja zwraca status `NO_MATCHES` i wyświetla komunikat informujący o braku dopasowań zamiast pustej tabeli lub błędu.
4. **R4 — Ranking do 3 najlepszych okolic:**
   * Zakwalifikowane obszary otrzymują wynik punktowy z przedziału `0–100 pkt`, są sortowane malejąco według `score` (przy remisie decyduje rosnące `area_id`), a system prezentuje maksymalnie **3 najlepsze okolice**.
5. **R5 — Uzasadnienie ocen i ograniczeń:**
   * Dla każdego z 3 obszarów generowany jest opis tekstowy wskazujący najsilniejsze atuty lokalizacji (np. najkrótszy czas marszu na uczelnię, bliskość przystanków lub sklepów) oraz stała adnotacja o liczeniu odległości w linii prostej od środka koła o promieniu 500 m.
6. **R6 — Zakres przestrzenny ograniczony do Rzeszowa:**
   * Dane wejściowe oraz siatka 25 obszarów obejmują wyłącznie granice administracyjne Rzeszowa.

---

## 4. Implementacja logiki obliczeniowej i interfejsu Streamlit

### 4.1. Algorytmy oceny obszarów
* **Weighted Scoring (Metoda średniej ważonej):** Odległości do uczelni oraz najbliższych usług w trzech kategoriach (`shop`, `bus_stop`, `park`) są normalizowane do skali `0–100` (im mniejsza odległość, tym wyższa wartość cząstkowa), a następnie mnożone przez wagi użytkownika (`1–3`) i dzielone przez sumę wag.
* **KNN (`scripts/knn_recommender.py`):** Wykorzystuje wektor znormalizowanych odległości z uwzględnieniem wag użytkownika oraz metrykę euklidesową do wyznaczenia najbliższych sąsiadów względem idealnego profilu studenta.

### 4.2. Warstwa prezentacji (Streamlit)
* **Buforowanie danych (`@st.cache_data`):** Pliki `universities.json`, `services.json` oraz `residential-areas.json` są wczytywane jednorazowo do pamięci podręcznej aplikacji, co zapewnia natychmiastową reakcję interfejsu przy zmianie suwaków wag lub limitu czasu.
* **Wizualizacja mapy:** Aplikacja renderuje interaktywną mapę Rzeszowa z zaznaczonym wybranym budynkiem uczelni oraz okręgami o promieniu **500 m** reprezentującymi rekomendowane okolice TOP 3.
* **Obsługa błędów i walidacja:** Zaimplementowano kontrolę poprawności danych wejściowych (`VALIDATION_ERROR`), kompletności plików źródłowych (`DATA_ERROR`) oraz pustych wyników filtrowania czasowego (`NO_MATCHES`).

---

## 5. Wymagania środowiskowe i uruchomienie aplikacji

### Wymagania wstępne
* Python w wersji **3.10** lub nowszej.
* Zainstalowane pakiety z pliku `requirements.txt` (m.in. `streamlit`, `pandas`, `numpy`, `folium`).

### Instrukcja uruchomienia krok po kroku
1. Sklonowanie repozytorium: `git clone https://github.com/CoffiPants/System-rekomendacji-okolic-do-zamieszkania-dla-student-w-w-Rzeszowie.git`
2. Przejście do katalogu projektu: `cd System-rekomendacji-okolic-do-zamieszkania-dla-student-w-w-Rzeszowie`
3. Instalacja zależności: `pip install -r requirements.txt`
4. Uruchomienie aplikacji webowej Streamlit: `streamlit run app.py` (aplikacja otworzy się pod adresem `http://localhost:8501`).
5. Opcjonalne uruchomienie testów i pomiarów wydajności: `python3 scripts/test_knn.py` oraz `python3 scripts/benchmark_knn_weighted.py`.

---

## 6. Weryfikacja poprawności implementacji (Testy)
* **Testy jakości danych (`scripts/check_data.py`):** Potwierdzają brak duplikatów kluczy głównych, poprawność współrzędnych WGS84 w granicach Rzeszowa oraz kompletność wymaganych pól.
* **Testy powtarzalności (`scripts/verify_repeatability.py`):** Gwarantują, że ponowne przetworzenie danych generuje identyczne pliki wyjściowe co w `data/test/repeatability-reference/`.
* **Testy algorytmu i przypadków brzegowych (`scripts/test_knn.py`):** Weryfikują sortowanie malejące po `score`, rozstrzyganie remisów po `area_id`, ograniczenie wyników do maksymalnie 3 pozycji oraz poprawną obsługę restrykcyjnego limitu czasu (np. `1 min` → status `NO_MATCHES`).
