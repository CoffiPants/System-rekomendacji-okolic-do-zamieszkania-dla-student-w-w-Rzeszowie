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

Przygotujemy 25 obszarów w 20 osiedlach:
- po 2: Nowe Miasto, Drabinianka, Zalesie, Dąbrowskiego, Piastów;
- po 1: Baranówka, Generała Władysława Andersa, Miłocin, Staromieście, 1000-lecia, Śródmieście, Pułaskiego, Generała Roweckiego-Grota, Kmity, Franciszka Kotuli, Przybyszówka, Krakowska-Południe, Króla Stanisława Augusta, Paderewskiego, Mieszka I.

Każdy obszar będzie kołem o promieniu 500 m, a nie całym osiedlem. Środki wybierzemy w zabudowie mieszkalnej.

Odległości liczymy w linii prostej od środka obszaru. Czas marszu szacujemy przy 4,5 km/h. Szacowany czas nie uwzględnia przebiegu ulic, przejść przez rzekę ani innych przeszkód i może być krótszy od rzeczywistego. Filtr: 15, 30, 45 minut lub brak limitu. Nie obejmujemy ogłoszeń, cen najmu ani rzeczywistych tras autobusowych.

## Potrzebne dane

| Informacja | Do czego jest potrzebna? | Minimalny zakres | Format lub częstotliwość | Czy jest dostępna? |
|---|---|---|---|---|
| Budynki uczelni | Wybór miejsca zajęć. | 28 lokalizacji czterech uczelni; nazwy, adresy i współrzędne położenia. | Lista w bazie; sprawdzenie przed prezentacją. | tak — przygotowano zbiór 28 lokalizacji; dokładne wejścia nie należą do gotowego zbioru. |
| Sklepy, przystanki i parki | Punktacja dostępu do usług. | Położenie i kategoria obiektów w otoczeniu analizowanych obszarów. | JSON; pobranie na początku i przed prezentacją. | częściowo — pobrano i sprawdzono 500 obiektów. |
| Obszary mieszkalne | Kandydaci do rankingu i koła na mapie. | 25 nazw, środków i promieni w 20 osiedlach. | Lista przygotowana ręcznie. | nie — środki kół nie zostały jeszcze zapisane. |
| Preferencje | Dopasowanie wyniku do użytkownika. | Budynek, limit czasu i 4 wagi. | Formularz przy każdym wyszukiwaniu. | nie — poda je użytkownik. |

## Założenia i pytania otwarte
Przyjęte decyzje: wagi 1–3; punktacja 0–100 według wzoru
`100 × max(0, 1 − odległość / limit)`.
Limity: uczelnia 3000 m, sklep 1000 m, przystanek 600 m, park 1500 m.
To parametry startowe projektu, nie miejskie normy. Wynik jest średnią ważoną.
Limit punktacji nie odrzuca obszaru; robi to wyłącznie filtr czasu.

Przygotowano i sprawdzono dane miejsc zajęć oraz usług. Pozostaje wyznaczyć środki 25 obszarów mieszkalnych i ocenić kompletność usług w ich otoczeniu.
Dla parków środek geometrii nie oznacza wejścia — wejścia sprawdzimy ręcznie.
Brak obiektu w danych nie dowodzi braku usługi.

## Wymagania
„Potwierdzone” oznacza ustalenie projektu. Kolumna „Osoba” wskazuje osobę opracowującą wymaganie, a nie przyszłego wykonawcę funkcji. Aktualną dokumentację i zestawy danych przygotowuje Valentyna Boksha.

| ID | Wymaganie | Kryterium sprawdzenia | Źródło lub uzasadnienie | Status | Osoba |
|---|---|---|---|---|---|
| R1 | Użytkownik powinien móc wybrać konkretny budynek uczelni w Rzeszowie jako miejsce zajęć. | Po wyborze budynku mapa pokazuje jego lokalizację, a obliczenia wykorzystują współrzędne tego budynku. | Ustalenie koncepcji: odległość należy odnosić do miejsca zajęć. | Potwierdzone | Serhii Popovych |
| R2 | Użytkownik powinien móc określić znaczenie bliskości uczelni, sklepu, przystanku i parku. | Każde kryterium ma trzy poziomy znaczenia; na przygotowanym przykładzie zmiana wagi wpływa na ocenę zgodnie ze wzorem. | Założenie projektu: studenci mają różne preferencje dotyczące otoczenia. | Założenie | Valentyna Boksha |
| R3 | Użytkownik powinien móc ograniczyć wyniki maksymalnym orientacyjnym czasem dojścia. | Obszary przekraczające limit nie występują w wynikach; przy braku dopasowań pojawia się komunikat. Formularz i wyniki informują o szacowaniu z odległości w linii prostej. | Przyjęte uproszczenie umożliwiające realizację pierwszej wersji. | Założenie | Paulina Michalska |
| R4 | Użytkownik powinien zobaczyć maksymalnie trzy najlepiej dopasowane okolice na mapie i w rankingu. | Dla przykładowych danych lista zawiera do trzech obszarów w kolejności ocen; koła mają zgodne środki i promień 500 m. Przy remisie kolejność jest ustalana według identyfikatora obszaru. | Ustalenie koncepcji: wskazanie obszarów poszukiwania mieszkania. | Potwierdzone | Serhii Popovych |
| R5 | Użytkownik powinien rozumieć, dlaczego dana okolica została polecona. | Każdy wynik pokazuje ocenę, odległości i krótkie uzasadnienie zgodne z punktacją oraz informację o liczeniu od środka obszaru. | Potrzeba porównania wyników i poznania ograniczeń rekomendacji. | Potwierdzone | Dana Stadnyk |
| R6 | Zakres projektu powinien ograniczać się do Rzeszowa, wybranych budynków uczelni i przygotowanych obszarów, bez wymagania danych o ofertach i cenach najmu. | Pełne wyszukiwanie działa na przygotowanym zestawie danych; cena i oferta najmu nie są wymagane do obliczenia rankingu. | Ograniczenie projektu studenckiego i brak potwierdzonego źródła porównywalnych cen. | Potwierdzone | Valentyna Boksha |

## Plan pracy zespołu

Valentyna Boksha przygotowuje obecnie dokumentację i zestawy danych. Podział dalszej realizacji odpowiada osobom przypisanym do wymagań.

| Osoba | Wymagania | Zadania |
|---|---|---|
| Valentyna Boksha | R2, R6 | Dokumentacja, pozyskanie i oczyszczenie danych z OpenStreetMap, przygotowanie struktury bazy danych oraz import danych o uczelniach, usługach i okolicach; ustawianie wag preferencji i punktacja kryteriów. |
| Serhii Popovych | R1, R4 | Wybór uczelni i miejsca zajęć, obsługa ich lokalizacji na mapie oraz prezentacja do trzech najlepszych okolic w rankingu i na mapie. |
| Paulina Michalska | R3 | Obliczanie orientacyjnego czasu dojścia, filtr maksymalnego czasu oraz komunikat przy braku dopasowanych okolic. |
| Dana Stadnyk | R5 | Wyświetlanie ocen i odległości, przygotowanie uzasadnień rekomendacji oraz informacji o ograniczeniach obliczeń. |

Każda osoba sprawdzi działanie swojej części. Połączenie modułów i końcowe testy będą zadaniem całego zespołu.
