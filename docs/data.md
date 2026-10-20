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

## Wynik sprawdzenia danych

| Element | Wynik sprawdzenia |
|---|---|
| Źródło i właściciel | Dane współtwórców OpenStreetMap, udostępniane na ODbL; odczyt przez Overpass API. |
| Link lub sposób dostępu | Overpass Turbo albo POST do https://overpass-api.de/api/interpreter z parametrem `data`. |
| Wymaganie, które źródło obsługuje | R1–R5: wybór miejsca zajęć, kryteria, filtr czasu, mapa i uzasadnienie rankingu. |
| Data pobrania | 20.10.2026 |
| Format i kodowanie | JSON, UTF-8. `sample.json` to surowa odpowiedź usług; `universities.json` to przygotowany zbiór miejsc zajęć. |
| Liczba rekordów | Usługi: 500 — 274 sklepy, 185 przystanków, 41 parków. Uczelnie: 105 obiektów przed selekcją; po przygotowaniu 28 miejsc — UR 16, PRz 10, WSIiZ 1, WSPiA 1. |
| Pola surowej odpowiedzi | `elements` — lista obiektów; `type` i `id` — klucz obiektu; `tags` — nazwa, adres i kategoria; `lat`, `lon` — punkt; `center` — środek obwiedni obszaru. |
| Pola przygotowanego zbioru uczelni | `locations` — lista miejsc; `id`, `university`, `name`, `address`, `latitude`, `longitude`, `location_type`, `coordinate_type`, `osm_url`, `source_name`, `source_address`, `supplement_sources`. Ostatnie pola zachowują pochodzenie i wskazują uzupełnienia. |
| Format dat i jednostki | Daty źródłowe: ISO 8601, UTC. Współrzędne: WGS84 w stopniach. Odległości i czas nie są pobrane — zostaną obliczone w aplikacji. |
| Brakujące wartości | 21 usług bez nazwy; można wyświetlać kategorię. Wszystkie 28 wybranych miejsc zajęć mają nazwę, adres i współrzędne. Nie oznacza to kompletności wszystkich budynków lub usług w terenie. |
| Limit zapytań, klucz i koszt | Bez klucza i opłaty w wykonanych próbach. Operator zaleca około maks. 10 tys. zapytań i poniżej 1 GB dziennie. |
| Licencja i ograniczenia | Dane OpenStreetMap są udostępniane na licencji ODbL. W aplikacji zamieścimy link do źródła https://www.openstreetmap.org/copyright.|
| Próba ponownego pobrania | Nie wykonano kontrolnego ponownego pobrania obecnych zapytań dla całego miasta.|
| Brakujące dane | Środki 25 obszarów mieszkalnych, zweryfikowane wejścia do parków i budynków oraz ocena kompletności usług. |
| Plan awaryjny | Wykorzystać zapisane dane; przy błędzie serwera powtórzyć pobranie później lub podzielić obszar. Braki uzupełniać dopiero po sprawdzeniu, z oznaczeniem źródła. |
| Wybrany pomysł realizacji | Formularz, mapa i ranking: HTML/CSS/JavaScript. Import danych wcześniej, bez zapytań do Overpass przy każdym wyszukiwaniu. |
| Odrzucony pomysł i powód | Aktualne oferty, ceny najmu i rzeczywisty czas dojazdu autobusem — brak przygotowanych danych i większy zakres realizacji. |

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
