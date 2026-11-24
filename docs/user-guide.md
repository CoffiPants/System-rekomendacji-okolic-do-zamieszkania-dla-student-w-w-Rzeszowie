# Instrukcja użytkownika — StudentFinder Rzeszów

StudentFinder Rzeszów to aplikacja wspomagająca studentów w wyborze okolicy do zamieszkania w Rzeszowie.

System generuje ranking maksymalnie trzech najlepiej dopasowanych obszarów mieszkalnych na podstawie lokalizacji uczelni oraz preferencji użytkownika.

## 1. Wymagane dane wejściowe

### 1.1. Wymagania techniczne

Do korzystania z aplikacji wymagane są:

- Python.
- Biblioteki wymienione w pliku `requirements.txt`.
- Przeglądarka internetowa.
- Dostęp do Internetu w celu wyświetlania podkładu mapowego.

Aplikacja wykorzystuje przygotowane wcześniej dane dotyczące lokalizacji uczelni, obiektów usługowych oraz obszarów mieszkalnych. Użytkownik nie musi samodzielnie wprowadzać ani przygotowywać tych danych.

### 1.2. Dane wprowadzane przez użytkownika

Użytkownik określa następujące parametry:

| Parametr | Dostępne wartości |
|---|---|
| Uczelnia | Uczelnia z dostępnej listy |
| Budynek lub wydział | Lokalizacja przypisana do wybranej uczelni |
| Maksymalny czas dojścia | 15, 30, 45 minut lub „Bez limitu” |
| Bliskość uczelni | Waga od 1 do 3 |
| Dostępność sklepów | Waga od 1 do 3 |
| Dostępność komunikacji miejskiej | Waga od 1 do 3 |
| Dostępność parków | Waga od 1 do 3 |

Domyślny maksymalny czas dojścia wynosi 30 minut.

Ważność każdego kryterium określana jest w skali:

- 1 — mniej ważne.
- 2 — średnio ważne.
- 3 — bardzo ważne.

## 2. Wykonanie krok po kroku

### 2.1. Uruchomienie aplikacji

1. Otwórz terminal w głównym katalogu projektu.
2. Zainstaluj wymagane biblioteki:

   `python -m pip install -r requirements.txt`

3. Uruchom aplikację:

   `python -m streamlit run app.py`

4. Otwórz adres lokalny wyświetlony w terminalu.

### 2.2. Wybór uczelni i budynku

W panelu bocznym:

1. Wybierz uczelnię z dostępnej listy.
2. Wybierz budynek lub wydział.
3. Sprawdź wyświetlony adres wybranej lokalizacji.

System wykorzystuje lokalizację wskazanego budynku do obliczania odległości.

### 2.3. Ustawienie maksymalnego czasu dojścia

W polu „Maksymalny czas dojścia do uczelni” wybierz jedną z dostępnych opcji:

- 15 minut.
- 30 minut — wartość domyślna.
- 45 minut.
- Bez limitu.

Jeżeli zbyt mało obszarów spełnia wybrane kryterium, zwiększ limit czasu lub wybierz opcję „Bez limitu”.

### 2.4. Ustawienie ważności kryteriów

Za pomocą suwaków określ ważność czterech kryteriów:

- Bliskość uczelni.
- Dostępność sklepów.
- Dostępność komunikacji miejskiej.
- Dostępność parków.

Im wyższa waga, tym większy wpływ danego kryterium na końcową ocenę okolicy.

### 2.5. Generowanie rekomendacji

Po ustawieniu preferencji kliknij przycisk „Generuj rekomendacje”.

System wyświetli maksymalnie trzy najlepiej ocenione okolice mieszkalne spełniające wybrane kryteria.

Po zmianie ustawień wcześniejsze wyniki zostają usunięte. Aby otrzymać ranking odpowiadający nowym preferencjom, należy ponownie kliknąć przycisk „Generuj rekomendacje”.

### 2.6. Korzystanie z mapy

Poniżej rankingu znajduje się interaktywna mapa rekomendowanych okolic.

Mapę można przybliżać, oddalać i przesuwać.

### 2.7. Eksport rankingu do CSV

Aby pobrać wyniki:

1. Wygeneruj rekomendacje.
2. Kliknij przycisk „Pobierz ranking TOP 3 (CSV)”.
3. Zapisz pobrany plik `studentfinder_top3.csv`.
4. Otwórz plik w programie Excel lub innym programie obsługującym CSV.

Plik zawiera pozycję w rankingu, nazwę uczelni i budynku, nazwę okolicy, osiedle, ocenę, szacowany czas dojścia oraz odległości do uczelni i wybranych usług.

### 2.8. Zakończenie pracy

Aby zakończyć działanie aplikacji uruchomionej lokalnie, przejdź do terminala i naciśnij `Ctrl+C`.

## 3. Interpretacja wyniku

### 3.1. Ranking rekomendowanych okolic

Dla każdej rekomendacji prezentowane są:

- Nazwa okolicy.
- Pozycja w rankingu.
- Ocena w skali 0–100.
- Szacowany czas dojścia do uczelni.
- Odległość od uczelni.
- Informacje o odległościach do wybranych usług.

### 3.2. Znaczenie oceny 0–100

Ocena określa stopień dopasowania okolicy do preferencji użytkownika.

Im wyższa ocena, tym lepiej dana okolica spełnia uwzględnione kryteria z przypisanymi im wagami.

Ocena jest obliczana metodą Weighted Scoring, która uwzględnia bliskość uczelni, sklepów, przystanków komunikacji miejskiej oraz parków.

Wartość 100 oznacza maksymalną możliwą ocenę w przyjętym modelu, natomiast 0 oznacza najniższą możliwą ocenę.

Ocena nie jest prawdopodobieństwem znalezienia mieszkania ani procentową oceną jakości życia w danej okolicy.

### 3.3. Interpretacja mapy

Kolory oznaczają pozycje w rankingu:

- Zielony — TOP 1.
- Pomarańczowy — TOP 2.
- Czerwony — TOP 3.

Na mapie oznaczono również wybraną lokalizację uczelni.

### 3.4. Ograniczenia systemu

- Odległości są obliczane w linii prostej od środka obszaru.
- Czas dojścia jest szacowany przy prędkości 4,5 km/h.
- System nie uwzględnia rzeczywistych tras pieszych, przejść ani przeszkód terenowych.
- Wyniki zależą od dostępnych danych oraz ustawionych preferencji.
- Rekomendacje mają charakter pomocniczy i nie stanowią oceny dostępności konkretnych mieszkań.

## 4. Komunikaty błędów i sposób postępowania

| Komunikat aplikacji | Znaczenie | Zalecane postępowanie |
|---|---|---|
| „Nie znaleziono okolic spełniających limit czasu dojścia…” | Żaden obszar mieszkalny nie spełnia wybranego limitu czasu. | Zwiększ maksymalny czas dojścia lub wybierz opcję „Bez limitu”, a następnie ponownie wygeneruj rekomendacje. |
| „W wybranym limicie czasu znaleziono tylko…” | W wybranym limicie mieszczą się mniej niż trzy okolice. Jest to poprawny wynik działania systemu, a nie błąd. | Zaakceptuj dostępne rekomendacje lub zwiększ limit czasu, aby uzyskać więcej wyników. |
| „Nie można wczytać danych projektu…” | Aplikacja nie może wczytać wymaganych danych projektu. | Sprawdź obecność i poprawność plików w katalogach `data/processed/` oraz `config/`. Następnie ponownie uruchom aplikację. Jeżeli problem nadal występuje, skontaktuj się z zespołem projektu. |