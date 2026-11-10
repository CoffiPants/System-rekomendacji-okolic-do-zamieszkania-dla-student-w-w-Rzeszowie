# ADR 001: Wybór formatu plików JSON/CSV zamiast relacyjnej bazy danych SQLite

* **Status:** Przyjęta (Accepted)
* **Data:** 2026-11-10
* **Autor:** Paulina Michalska

## Kontekst i problem
System rekomendacji okolic mieszkalnych dla studentów w Rzeszowie wymaga przechowywania oraz przetwarzania danych o:
- lokalizacjach budynków i kampusów uczelni (28 obiektów),
- obiektach usługowych, takich jak sklepy, przystanki i parki (500 obiektów),
- zdefiniowanych obszarach mieszkalnych (25 obszarów w 20 osiedlach),
- wynikach porównań algorytmów (Weighted Scoring oraz KNN).

Należy podjąć decyzję dotyczącą sposobu przechowywania danych wejściowych, pośrednich oraz wyników analitycznych w kontekście wymagań wydajnościowych, łatwości integracji z algorytmami w Pythonie oraz złożoności utrzymania projektu.

## Rozważane opcje
1. **Relacyjna baza danych (np. SQLite)**
2. **Pliki płaskie i półstrukturalne (JSON + CSV)**

## Ocena opcji

### Opcja 1: Relacyjna baza danych (SQLite)
* **Zalety:**
  * Wbudowane wsparcie dla zapytania SQL i relacji między tabelami.
  * ACID oraz transakcyjność.
* **Wady:**
  * Konieczność tworzenia i zarządzania migracjami schematu bazy danych.
  * Dodatkowy narzut technologiczny (ORM lub sterownik SQLite w Pythonie).
  * Złożoność przy bezpośredniej kontroli wersji w systemie Git (pliki binarne `.sqlite` utrudniają śledzenie zmian w kodzie).

### Opcja 2: Pliki JSON + CSV (Rekomendowana)
* **Zalety:**
  * **Natywna zgodność z danymi źródłowymi:** Dane pozyskane z OpenStreetMap (Overpass API) docierają w formacie JSON.
  * **Bezpośrednia integracja z Pythonem:** Biblioteka standardowa (`json`, `csv`) umożliwia szybki odczyt i zapis bez zewnętrznych zależności.
  * **Pełna kontrola wersji w Git:** Pliki tekstowe JSON/CSV pozwalają na precyzyjne śledzenie zmian (diffs), audytowanie jakości oraz weryfikację powtarzalności wyników.
  * **Wystarczająca skala:** Zbiór danych obejmuje 528 obiektów, co sprawia, że ładowanie całej struktury do pamięci RAM (in-memory processing) trwa ułamek sekundy.

## Decyzja
Wybieramy **wykorzystanie plików JSON dla konfiguracji i danych wejściowych/przetworzonych oraz CSV dla eksportu wyników i rankingów**.

Nie wdrażamy bazy SQL na obecnym etapie, ponieważ skomplikowałaby ona architekturę bez przynoszenia realnych korzyści wydajnościowych przy obecnej skali danych.

## Konsekwencje
* **Pozytywne:**
  * Prosta struktura projektu bez konieczności konfiguracji silnika bazy danych.
  * Pełna powtarzalność i łatwość audytowania danych w repetytorium Git.
  * Bezproblemowa integracja ze skryptami analitycznymi w Pythonie.
* **Negatywne / Ograniczenia:**
  * W przypadku wzrostu liczby obiektów do dziesiątek tysięcy konieczna będzie reewaluacja architektury pod kątem przejścia na bazę spacyjną (np. PostGIS / SQLite z SpatiaLite).