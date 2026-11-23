# Problem projektu

## Użytkownik i decyzja
Student rozpoczynający studia w Rzeszowie wybiera okolice, w których będzie szukać mieszkania. Aplikacja pokaże do trzech obszarów dopasowanych do miejsca zajęć i preferencji.

## Obecna trudność
Student nieznający miasta musi osobno porównywać odległości do uczelni, sklepów, przystanków i parków. Przyjęto, że wskazane kryteria odpowiadają potrzebom studentów. Założenie nie zostało jeszcze zweryfikowane w badaniu użytkowników.

## Zakres problemu
Strona z formularzem, mapą i rankingiem. Zakres obejmuje cztery wybrane uczelnie w Rzeszowie, z wyborem konkretnego miejsca zajęć.

| Uczelnia | Zakres pierwszej wersji |
|---|---|
| Uniwersytet Rzeszowski | 16 miejsc: A0, A1, A2, A3, E4 przy Cichej, D1, D7, D9 oraz lokalizacje przy Jałowego, Grunwaldzkiej, Moniuszki, Hoffmanowej, Warzywnej, Litawora, Warszawskiej i Leszka Czarnego. |
| Politechnika Rzeszowska | 10 miejsc: A, C, D, E, F, H, K, P, V i W. |
| Wyższa Szkoła Informatyki i Zarządzania | Kampus przy Sucharskiego 2. |
| WSPiA Rzeszowska Szkoła Wyższa | Kampus przy Cegielnianej 14. |

Łącznie przygotowano 28 lokalizacji z nazwami, adresami i współrzędnymi. Osobne korpusy o wspólnym adresie zachowano. Współrzędne oznaczają przybliżone położenie budynku lub kampusu, nie zweryfikowane wejście.

Projekt obejmuje wyłącznie lokalizacje w granicach Rzeszowa.

Przygotowano 25 obszarów w 20 osiedlach (`config/residential-areas.json`, etykiety środków weryfikowane w `docs/area-name-audit.md`):
- po 2: Nowe Miasto, Drabinianka, Zalesie, Dąbrowskiego, Piastów;
- po 1: Baranówka, Generała Władysława Andersa, Miłocin, Staromieście, 1000-lecia, Śródmieście, Pułaskiego, Generała Roweckiego-Grota, Kmity, Franciszka Kotuli, Przybyszówka, Krakowska-Południe, Króla Stanisława Augusta, Paderewskiego, Mieszka I.

Każdy obszar jest kołem o promieniu 500 m, a nie całym osiedlem. Środki wyznaczono w zabudowie mieszkalnej; etykiety `name` mają charakter orientacyjny i nie wyznaczają granic osiedla ani koła 500 m.

Odległości liczymy w linii prostej od środka obszaru. Czas marszu szacujemy przy 4,5 km/h (75 m/min). Szacowany czas nie uwzględnia przebiegu ulic, przejść przez rzekę ani innych przeszkód i może być krótszy od rzeczywistego. Filtr: 15, 30, 45 minut lub brak limitu. Nie obejmujemy ogłoszeń, cen najmu ani rzeczywistych tras autobusowych.

## Potrzebne dane

| Informacja | Do czego jest potrzebna? | Minimalny zakres | Format lub częstotliwość | Czy jest dostępna? |
|---|---|---|---|---|
| Budynki uczelni | Wybór miejsca zajęć. | 28 lokalizacji czterech uczelni; nazwy, adresy i współrzędne położenia. | Lista w bazie; sprawdzenie przed prezentacją. | tak — przygotowano zbiór 28 lokalizacji; dokładne wejścia nie należą do gotowego zbioru. |
| Sklepy, przystanki i parki | Punktacja dostępu do usług. | Położenie i kategoria obiektów w otoczeniu analizowanych obszarów. | JSON; pobranie na początku i przed prezentacją. | tak — pobrano i sprawdzono 500 obiektów (`data/processed/services.json`). |
| Obszary mieszkalne | Kandydaci do rankingu i koła na mapie. | 25 nazw, środków i promieni w 20 osiedlach. | `config/residential-areas.json` oraz `docs/area-name-audit.md`. | tak — zapisano 25 obszarów o promieniu 500 m; nazwy są orientacyjne. |
| Preferencje | Dopasowanie wyniku do użytkownika. | Budynek, limit czasu i 4 wagi (1–3). | Formularz przy każdym wyszukiwaniu. | nie — poda je użytkownik. |

## Założenia i pytania otwarte
Przyjęte decyzje: wagi 1–3; punktacja 0–100 według wzoru
`100 × max(0, 1 − odległość / limit)`.
Limity: uczelnia 3000 m, sklep 1000 m, przystanek 600 m, park 1500 m.
To parametry startowe projektu, nie miejskie normy. Wynik jest średnią ważoną.
Limit punktacji nie odrzuca obszaru; robi to wyłącznie filtr czasu.

Dla parków środek geometrii nie oznacza wejścia.
Brak obiektu w danych nie dowodzi braku usługi.

## Wymagania
„Potwierdzone” oznacza ustalenie projektu. Kolumna „Osoba” wskazuje osobę opracowującą wymaganie. Aktualny stan testów i weryfikacji opisuje `docs/tests.md` (na gałęzi `valentyna-data-validation`).

| ID | Wymaganie | Kryterium sprawdzenia | Źródło lub uzasadnienie | Status | Osoba |
|---|---|---|---|---|---|
| R1 | Użytkownik powinien móc wybrać konkretny budynek uczelni w Rzeszowie jako miejsce zajęć. | Po wyborze budynku mapa pokazuje jego lokalizację, a obliczenia wykorzystują współrzędne tego budynku. | Ustalenie koncepcji: odległość należy odnosić do miejsca zajęć. | Potwierdzone | Serhii Popovych |
| R2 | Użytkownik powinien móc określić znaczenie bliskości uczelni, sklepu, przystanku i parku. | Każde kryterium ma trzy poziomy znaczenia (1–3); na przygotowanym przykładzie zmiana wagi wpływa na ocenę zgodnie ze wzorem. | Założenie projektu: studenci mają różne preferencje dotyczące otoczenia. | Potwierdzone | Valentyna Boksha |
| R3 | Użytkownik powinien móc ograniczyć wyniki maksymalnym orientacyjnym czasem dojścia. | Obszary przekraczające limit nie występują w wynikach; przy braku dopasowań pojawia się komunikat. Formularz i wyniki informują o szacowaniu z odległości w linii prostej. | Przyjęte uproszczenie umożliwiające realizację pierwszej wersji. | Potwierdzone | Paulina Michalska |
| R4 | Użytkownik powinien zobaczyć maksymalnie trzy najlepiej dopasowane okolice na mapie i w rankingu. | Dla przykładowych danych lista zawiera do trzech obszarów w kolejności ocen; koła mają zgodne środki i promień 500 m. Przy remisie kolejność jest ustalana według identyfikatora obszaru. | Ustalenie koncepcji: wskazanie obszarów poszukiwania mieszkania. | Potwierdzone | Serhii Popovych |
| R5 | Użytkownik powinien rozumieć, dlaczego dana okolica została polecona. | Każdy wynik pokazuje ocenę, odległości i krótkie uzasadnienie zgodne z punktacją oraz informację o liczeniu od środka obszaru. | Potrzeba porównania wyników i poznania ograniczeń rekomendacji. | Potwierdzone | Dana Stadnyk |
| R6 | Zakres projektu powinien ograniczać się do Rzeszowa, wybranych budynków uczelni i przygotowanych obszarów, bez wymagania danych o ofertach i cenach najmu. | Pełne wyszukiwanie działa na przygotowanym zestawie danych; cena i oferta najmu nie są wymagane do obliczenia rankingu. | Ograniczenie projektu studenckiego i brak potwierdzonego źródła porównywalnych cen. | Potwierdzone | Valentyna Boksha |

## Plan pracy zespołu

Aktualny podział ról i odpowiedzialności w zespole:

| Osoba | Zakres odpowiedzialności |
|---|---|
| Dana Stadnyk | Interfejs użytkownika w Streamlit (`app.py`), wizualizacja wyników i mapy. |
| Valentyna Boksha | Dane oraz testy (`docs/tests.md`, testy walidacji i punktacji, kontrola jakości danych). |
| Serhii Popovych | Silnik rekomendacji (`scripts/recommendation_engine.py`), benchmarki i integracja modułów. |
| Paulina Michalska | Architektura systemu (`docs/architecture.md`) oraz dokumentacja (`docs/implementation.md`, `docs/report.md`, `docs/presentation.md`, `README.md`). |