# Lab 6 — Implementacja MVP

## 1. Cel

Celem laboratorium było przygotowanie działającego
prototypu systemu rekomendacji okolic do zamieszkania
dla studentów w Rzeszowie.

## 2. Zrealizowane komponenty

### Interfejs użytkownika

Plik: `app.py`

Interfejs został przygotowany w technologii Streamlit.

Użytkownik może wybrać uczelnię, budynek, maksymalny
czas dojścia oraz określić znaczenie poszczególnych
kryteriów.

### Silnik rekomendacji

Plik: `scripts/recommendation_engine.py`

Silnik odpowiada za analizę dostępnych okolic
i przygotowanie rankingu zgodnego z preferencjami.

Podstawową metodą oceny jest Weighted Scoring.

### Wizualizacja

Wyniki przedstawiane są w formie kart rekomendacji
oraz na interaktywnej mapie.

Dla każdej rekomendacji prezentowane są:

- nazwa okolicy,
- ocena punktowa,
- szacowany czas dojścia,
- odległość od uczelni,
- dodatkowe informacje o dostępności usług.

## 3. Dane wejściowe

System wykorzystuje:

- dane lokalizacji uczelni,
- dane obiektów usługowych,
- dane obszarów mieszkalnych,
- preferencje podane przez użytkownika.

## 4. Dane wyjściowe

Wynikiem działania systemu jest ranking maksymalnie
trzech najlepiej ocenionych okolic, które spełniają
ustalony limit czasu dojścia.

## 5. Obsługa sytuacji wyjątkowych

W interfejsie uwzględniono:

- brak okolic spełniających limit czasu,
- ustawienie wszystkich wag na zero,
- prezentację mniejszej liczby rekomendacji,
  jeżeli tylko część okolic spełnia wymagania.

## 6. Testowanie

Przewidziano następujące kontrole:

1. Uruchomienie aplikacji Streamlit.
2. Poprawność generowania rekomendacji.
3. Zmiana wyników po modyfikacji preferencji.
4. Obsługa zerowych wag.
5. Obsługa braku dostępnych wyników.
6. Weryfikacja działania mapy.
7. Testy automatyczne silnika rekomendacji.
8. Pomiar wydajności.

Wyniki testów automatycznych i benchmarku należy
uzupełnić po ich wykonaniu.

## 7. Ograniczenia

Czas dojścia jest wartością szacunkową, wyznaczaną
na podstawie odległości geograficznej.

System nie korzysta z rzeczywistych tras pieszych
ani z aktualnych ofert mieszkaniowych.

## 8. Podsumowanie

Przygotowano prototyp MVP umożliwiający wybór
preferencji, generowanie rekomendacji oraz
prezentację wyników na mapie.

Interfejs stanowi podstawę do dalszego rozwijania
funkcjonalności systemu.

**Odpowiedzialna: Dana Stadnyk**