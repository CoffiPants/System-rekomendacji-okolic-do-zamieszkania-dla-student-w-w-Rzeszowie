# Instrukcja użytkownika — StudentFinder Rzeszów

## 1. Cel aplikacji

StudentFinder Rzeszów to aplikacja wspomagająca studentów w wyborze okolicy do zamieszkania w Rzeszowie.

System generuje ranking trzech najlepiej dopasowanych obszarów mieszkalnych na podstawie lokalizacji uczelni oraz preferencji użytkownika.

## 2. Uruchomienie aplikacji

Aby uruchomić aplikację lokalnie:

1. Otwórz terminal w głównym katalogu projektu.
2. Zainstaluj wymagane biblioteki:

   `python -m pip install -r requirements.txt`

3. Uruchom aplikację:

   `python -m streamlit run app.py`

4. Otwórz adres lokalny wyświetlony w terminalu.

Do korzystania z aplikacji wymagane są Python oraz przeglądarka internetowa.

## 3. Wybór uczelni i budynku

W panelu bocznym:

1. Wybierz uczelnię z dostępnej listy.
2. Wybierz budynek lub wydział.
3. Sprawdź wyświetlony adres wybranej lokalizacji.

System wykorzystuje lokalizację wskazanego budynku do obliczania odległości.

## 4. Ustawienie maksymalnego czasu dojścia

W polu „Maksymalny czas dojścia do uczelni” wybierz dostępny limit.

Możesz również wybrać opcję „Bez limitu”.

Jeżeli zbyt mało obszarów spełnia wybrane kryterium, zwiększ limit czasu lub wybierz opcję „Bez limitu”.

## 5. Ustawienie ważności kryteriów

Aplikacja umożliwia określenie ważności czterech kryteriów:

- Bliskość uczelni.
- Dostępność sklepów.
- Dostępność komunikacji miejskiej.
- Dostępność parków.

Każde kryterium można ustawić w skali od 1 do 3:

- 1 — mniej ważne.
- 2 — średnio ważne.
- 3 — bardzo ważne.

## 6. Generowanie rekomendacji

Po ustawieniu preferencji kliknij przycisk „Generuj rekomendacje”.

System wyświetli maksymalnie trzy najlepiej ocenione okolice mieszkalne.

Dla każdej rekomendacji prezentowane są między innymi:

- Nazwa okolicy.
- Pozycja w rankingu.
- Ocena w skali 0–100.
- Szacowany czas dojścia do uczelni.
- Odległość od uczelni.
- Informacje o odległościach do wybranych usług.

## 7. Mapa rekomendowanych okolic

Poniżej rankingu znajduje się interaktywna mapa.

Kolory oznaczają pozycje w rankingu:

- Zielony — TOP 1.
- Pomarańczowy — TOP 2.
- Czerwony — TOP 3.

Na mapie oznaczono również wybraną lokalizację uczelni.

Mapę można przybliżać, oddalać i przesuwać.

## 8. Eksport rankingu do CSV

Aplikacja umożliwia pobranie wyników w formacie CSV.

Aby pobrać plik:

1. Wygeneruj rekomendacje.
2. Kliknij przycisk „Pobierz ranking TOP 3 (CSV)”.
3. Zapisz pobrany plik `studentfinder_top3.csv`.
4. Otwórz plik w programie Excel lub innym programie obsługującym CSV.

Plik zawiera pozycję w rankingu, nazwę uczelni i budynku, nazwę okolicy, osiedle, ocenę, szacowany czas dojścia oraz odległości do uczelni i wybranych usług.

## 9. Ograniczenia systemu

- Odległości są obliczane w linii prostej od środka obszaru.
- Czas dojścia jest szacowany przy prędkości 4,5 km/h.
- System nie uwzględnia rzeczywistych tras pieszych, przejść ani przeszkód terenowych.
- Wyniki zależą od dostępnych danych oraz ustawionych preferencji.
- Rekomendacje mają charakter pomocniczy i nie stanowią oceny dostępności konkretnych mieszkań.

## 10. Zakończenie pracy

Aby zakończyć działanie aplikacji uruchomionej lokalnie, przejdź do terminala i naciśnij `Ctrl+C`.