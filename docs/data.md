# Dane i pomysł realizacji

## Źródła danych

| Źródło | Co można pobrać? | Czy odpowiada potrzebom? | Dowód sprawdzenia | Braki lub ryzyko |
|---|---|---|---|---|
| OpenStreetMap przez Overpass API — źródło podstawowe | Lokalizacje sklepów, przystanków, parków oraz obiekty uczelni. | częściowo | Pobrano próbkę 500 obiektów usług oraz osobną próbkę 105 obiektów uczelnianych. | Niepełne nazwy i adresy; oznaczenie uczelni może dotyczyć kampusu, nie budynku. |
| Oficjalne strony uczelni — źródło pomocnicze | Nazwy, oznaczenia i adresy miejsc zajęć. | częściowo | Uzupełniono nazwę E4 przy Cichej 2A oraz adres WSPiA: Cegielniana 14. | Brak jednolitego API i współrzędnych wejść; nazwy jednostek mogą się zmieniać. |

## Kontrola źródeł

### OpenStreetMap przez Overpass API

| Obszar | Pytanie kontrolne | Wynik sprawdzenia |
|---|---|---|
| Dopasowanie do problemu | Czy źródło zawiera dane potrzebne do realizacji konkretnego wymagania? | Częściowo. Obsługuje R1–R5: miejsca zajęć i usług, mapę oraz obliczanie odległości. Nie wszystkie obiekty mają nazwy i adresy. |
| Właściciel i znaczenie danych | Kto publikuje dane? Co oznaczają pola, jednostki i daty? | Dane tworzą współtwórcy OSM; odczyt przez Overpass API. `type` i `id` identyfikują obiekt, `tags` opisuje właściwości, `lat`/`lon` i `center` określają położenie WGS84 w stopniach. |
| Jakość | Czy występują braki, duplikaty, błędne jednostki, niepełne okresy albo nieaktualne rekordy? | Usługi: 500 rekordów, 21 bez nazwy. Uczelnie przed selekcją: 105 rekordów, 37 bez nazwy. W obu próbkach nie stwierdzono braków współrzędnych ani duplikatów typu i ID. Nie potwierdzono kompletności terenowej i aktualności wszystkich nazw. |
| Dostęp i koszt | Ile zapytań można wykonać? Czy wymagany jest klucz, logowanie albo opłata? | Pobrania bez klucza, logowania i opłaty.|
| Licencja i prywatność | Czy można użyć danych w projekcie i czy nie zawierają danych osobowych? | ODbL umożliwia wykorzystanie z zachowaniem warunków, w tym oznaczenia źródła. Zapytania nie pobierają autorów edycji. Aplikacja wykorzysta tylko potrzebne pola, bez zbędnych kontaktów. |
| Powtarzalność | Czy inna osoba może ponownie pobrać podobne dane, korzystając z zapisanego adresu, parametrów i daty? | Można ponowić pobranie; wynik może się zmienić wraz z bazą. Nie wykonano kontrolnego ponownego pobrania obecnych zapytań dla całego miasta. |


Dokumentacja właścicieli źródeł:

- [Overpass QL — zapytania i format odpowiedzi](https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL).
- [OpenStreetMap — licencja i oznaczenie źródła](https://www.openstreetmap.org/copyright).
- [UR — budynki, w tym E4 przy Cichej 2A](https://bip.ur.edu.pl/deklaracja-dostepnosci-cyfrowej).
- [WSPiA — adres kampusu](https://portal.wspia.eu/pl/kontakt/).

## Plan pozyskania danych

| Element | Ustalenie zespołu |
|---|---|
| Źródło lub sposób pomiaru | OpenStreetMap przez Overpass API. Oficjalne strony UR i WSPiA służą do uzupełnienia wybranych nazw i adresów. |
| Właściciel danych | Współtwórcy OpenStreetMap; informacje uzupełniające publikują poszczególne uczelnie. |
| Zakres danych | Sklepy spożywcze, przystanki i parki w granicach Rzeszowa oraz wybrane miejsca zajęć UR, PRz, WSIiZ i WSPiA. |
| Okres i częstotliwość | Dane pobrano 20.10.2026. Przetwarzanie i kontrolę powtarzalności wykonujemy na tej samej zapisanej próbce. Aktualizację planujemy przed końcową prezentacją. |
| Jednostka obserwacji | Jeden obiekt OSM identyfikowany przez parę `type` i `id`. W wyniku: pojedyncza usługa albo wybrane miejsce zajęć. |
| Dobór obserwacji i liczebność próby | Dobór według kategorii i granic miasta: 500 usług — 274 sklepy, 185 przystanków i 41 parków. Osobno pobrano 105 obiektów uczelnianych, z których przygotowano zestaw 28 miejsc: UR 16, PRz 10, WSIiZ 1, WSPiA 1. |
| Sposób pobrania lub zebrania | Dwa zapytania w Overpass Turbo, zapisane poniżej, oraz eksport „raw OSM data” do JSON UTF-8. Niezmienione odpowiedzi znajdują się w `data/raw/sample.json` i `data/raw/universities.json`. Reguły wyboru i uzupełnień zapisano w `config/university-selection.json`. |
| Limit, koszt lub wymagane uprawnienia | Pobranie bez klucza, logowania i opłaty. Operator zaleca około maks. 10 tys. zapytań i poniżej 1 GB dziennie; dostępność zależy od obciążenia serwera. |
| Licencja i zasady publikacji | Dane OSM są udostępniane na licencji ODbL. Zamieścimy oznaczenie „© OpenStreetMap contributors” i link do https://www.openstreetmap.org/copyright. Przy udostępnianiu danych podamy licencję i link do https://opendatacommons.org/licenses/odbl/1-0/. Nie publikujemy zbędnych danych kontaktowych ani danych autorów edycji. |
| Osoba odpowiedzialna za pozyskanie | Valentyna Boksha — pobranie, uporządkowanie danych i przygotowanie reguł wyboru lokalizacji. |
| Plan awaryjny | Pracować na zapisanych próbkach. Przy błędzie API ponowić pobranie później lub podzielić obszar. Brakujące informacje uzupełniać ze sprawdzonych źródeł, zachowując informację o ich pochodzeniu. |

## Przygotowanie listy miejsc zajęć

Z surowej próbki wybrano miejsca dla UR, PRz, WSIiZ i WSPiA. Usunięto obiekty innych instytucji, pomocnicze obiekty nieprzydatne do wyboru miejsca zajęć oraz rekordy bez danych pozwalających je jednoznacznie opisać. Zestaw nie jest pełnym wykazem wszystkich korpusów.

Dla E4 uzupełniono nazwę na podstawie oznaczenia korpusu i strony UR. Dla WSPiA dodano adres z oficjalnej strony. Pozostałe nazwy i adresy pochodzą z OSM. Oddzielne korpusy pod wspólnym adresem zachowano.

WSIiZ i WSPiA reprezentują kampusy. Współrzędne obszarów oznaczają środki ich obwiedni, nie wejścia. W interfejsie podstawowym opisem będzie uczelnia, oznaczenie korpusu i adres; nazwa wydziału może wymagać aktualizacji.

## Zapytania użyte w Overpass Turbo

### Sklepy, przystanki i parki

```text
[out:json][timeout:90];
area["name"="Rzeszów"]["boundary"="administrative"]["admin_level"="8"]->.city;
(
  nwr["shop"~"^(supermarket|convenience)$"](area.city);
  node["highway"="bus_stop"](area.city);
  nwr["leisure"="park"](area.city);
);
out center;
```

### Surowa lista obiektów uczelni

```text
[out:json][timeout:90];
area["name"="Rzeszów"]["boundary"="administrative"]["admin_level"="8"]->.city;
(
  nwr["amenity"="university"](area.city);
  nwr["building"="university"](area.city);
);
out center;
```

Pliki sprawdzono programowo: poprawność JSON i UTF-8, strukturę, nazwy pól, liczbę rekordów, współrzędne, brakujące wartości i duplikaty. Dane są poprawne strukturalnie i nadają się do rozpoczęcia realizacji projektu.
