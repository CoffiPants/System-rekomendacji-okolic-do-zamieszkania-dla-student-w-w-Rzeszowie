# Słownik danych

JSON przechowuje typy: tekst, liczba, wartość logiczna, lista, obiekt i null. WGS84 oznacza współrzędne geograficzne w stopniach. Środek obwiedni nie jest zweryfikowanym wejściem.

## Dane wejściowe — data/raw/sample.json i data/raw/universities.json

Opis obejmuje pola odczytywane przez procedurę oraz metadane używane przy interpretacji. Pozostałe tagi OSM nie są wykorzystywane w tym etapie.

| Pole | Znaczenie | Typ | Jednostka / format | Przykładowa wartość | Czy może być puste? |
|---|---|---|---|---|---|
| elements | Lista obiektów OSM | lista | — | obiekty usług lub uczelni | nie |
| remark | Komunikat błędu lub ostrzeżenia API; jego obecność zatrzymuje przetwarzanie | tekst | — | pole nieobecne w poprawnej próbce | tak |
| elements[].type | Rodzaj obiektu | tekst | node, way, relation | node | nie |
| elements[].id | Numer obiektu w obrębie jego typu | liczba całkowita | — | 566829496 | nie |
| elements[].tags | Właściwości obiektu | obiekt | klucz–wartość | nazwa i adres sklepu | tak — obiekt bez kategorii nie trafi do wyniku usług |
| tags.name | Oryginalna nazwa | tekst | — | A0 | tak |
| tags.shop | Typ sklepu | tekst | supermarket, convenience w zakresie projektu | supermarket | tak — dotyczy sklepów |
| tags.highway | Rodzaj obiektu drogowego | tekst | bus_stop dla wybranych przystanków | bus_stop | tak |
| tags.leisure | Rodzaj obiektu rekreacyjnego | tekst | park dla wybranych parków | park | tak |
| tags.addr:street | Ulica | tekst | — | Profesora Stanisława Pigonia | tak |
| tags.addr:housenumber | Numer budynku, zachowany jako tekst | tekst | — | 1 | tak |
| tags.addr:city | Miejscowość; przy braku skrypt przyjmuje Rzeszów | tekst | — | Rzeszów | tak |
| elements[].lat | Szerokość geograficzna punktu node | liczba | stopnie WGS84, od −90 do 90 | 50.0351183 | nie dla wybranego node; nie dotyczy way/relation |
| elements[].lon | Długość geograficzna punktu node | liczba | stopnie WGS84, od −180 do 180 | 21.980623 | nie dla wybranego node; nie dotyczy way/relation |
| elements[].center.lat | Szerokość środka obwiedni way/relation | liczba | stopnie WGS84 | 50.0301285 | nie dla wybranego way/relation |
| elements[].center.lon | Długość środka obwiedni way/relation | liczba | stopnie WGS84 | 22.0140556 | nie dla wybranego way/relation |
| osm3s.timestamp_osm_base | Stan bazy OSM w odpowiedzi, nie data aktualizacji każdego obiektu | tekst | ISO 8601, UTC | 2026-10-20T06:25:06Z w próbce usług | nie jest wymagane przez skrypt; wykorzystywane w opisie źródła |

## Reguły — config/university-selection.json

| Pole | Znaczenie | Typ | Jednostka / format | Przykładowa wartość | Czy może być puste? |
|---|---|---|---|---|---|
| locations | Lista reguł wyboru miejsc zajęć | lista | — | 28 reguł | nie |
| locations[].osm_id | Klucz łączący regułę z surowym obiektem | tekst | type/id | way/208515700 | nie |
| locations[].university | Przypisanie do uczelni | tekst | UR, PRz, WSIiZ, WSPiA | UR | nie |
| locations[].location_type | Rodzaj miejsca | tekst | building, campus | building | nie |
| locations[].selection_reason | Uzasadnienie wyboru; informacja dokumentacyjna | tekst | — | Wybrana lokalizacja z nazwą, adresem i współrzędnymi, przydatna jako miejsce zajęć w projekcie. | nie w przyjętej konfiguracji; skrypt nie waliduje tego pola |
| locations[].overrides.name | Uzupełniona nazwa zamiast wartości OSM | tekst | — | Budynek E4 — Cicha | tak — tylko dla potrzebnych uzupełnień |
| locations[].overrides.address | Uzupełniony pełny adres | tekst | — | Cegielniana 14, Rzeszów | tak |
| locations[].override_sources | Źródła dla każdego zastosowanego uzupełnienia; klucze name lub address | obiekt | adresy URL | https://portal.wspia.eu/pl/kontakt/ | tak, jeśli nie ma uzupełnień |

## Wspólne metadane plików wynikowych

Dotyczy data/processed/services.json i data/processed/universities.json.

| Pole | Znaczenie | Typ | Jednostka / format | Przykładowa wartość | Czy może być puste? |
|---|---|---|---|---|---|
| attribution | Oznaczenie źródła | tekst | — | © OpenStreetMap contributors | nie |
| license | Nazwa licencji | tekst | — | ODbL-1.0 | nie |
| license_url | Adres informacji o licencji | tekst | URL | https://www.openstreetmap.org/copyright | nie |

## Wynik usług — data/processed/services.json

Poniższe pola znajdują się w rekordach listy services. Lista musi być niepusta.

| Pole | Znaczenie | Typ | Jednostka / format | Przykładowa wartość | Czy może być puste? |
|---|---|---|---|---|---|
| id | Unikalny klucz utworzony z type i id OSM | tekst | type/id | node/566829496 | nie |
| category | Kategoria nadana według tagów źródłowych | tekst | shop, bus_stop, park | shop | nie |
| name | Nazwa po uporządkowaniu spacji albo etykieta kategorii z ID | tekst | — | FRAC | nie |
| name_missing | Czy oryginalna nazwa jest nieobecna lub pusta po usunięciu białych znaków | wartość logiczna | true/false | false | nie |
| source_name | Nazwa źródłowa bez zmiany wartości | tekst lub null | — | FRAC | tak |
| address | Ulica i numer oraz miasto; null, jeśli brakuje ulicy lub numeru | tekst lub null | — | Bohaterów 5, Rzeszów | tak |
| latitude | Szerokość geograficzna | liczba | stopnie WGS84 | 50.0351183 | nie |
| longitude | Długość geograficzna | liczba | stopnie WGS84 | 21.980623 | nie |
| coordinate_type | Pochodzenie współrzędnych | tekst | osm_node, osm_bounding_box_center | osm_node | nie |
| osm_url | Odnośnik utworzony z id | tekst | URL | https://www.openstreetmap.org/node/566829496 | nie |

name_missing nie oznacza błędu lokalizacji. Adres usługi jest opcjonalny, ponieważ odległości będą obliczane ze współrzędnych. Kategorie są wybierane kolejno: sklep, przystanek node, park.

## Wynik miejsc zajęć — data/processed/universities.json

Poniższe pola znajdują się w rekordach listy locations. Każdy rekord musi mieć nazwę, pełny adres i współrzędne. Przykłady dotyczą A0, a dla uzupełnienia — E4 lub WSPiA.

| Pole | Znaczenie | Typ | Jednostka / format | Przykładowa wartość | Czy może być puste? |
|---|---|---|---|---|---|
| id | Unikalny klucz obiektu OSM | tekst | type/id | way/208515700 | nie |
| university | Uczelnia z konfiguracji wyboru | tekst | UR, PRz, WSIiZ, WSPiA | UR | nie |
| name | Nazwa z OSM lub udokumentowanego uzupełnienia | tekst | — | A0 | nie |
| address | Pełny adres z tagów lub konfiguracji | tekst | — | Profesora Stanisława Pigonia 1, Rzeszów | nie |
| latitude | Szerokość geograficzna | liczba | stopnie WGS84 | 50.0301285 | nie |
| longitude | Długość geograficzna | liczba | stopnie WGS84 | 22.0140556 | nie |
| location_type | Budynek lub kampus | tekst | building, campus | building | nie |
| coordinate_type | Pochodzenie położenia | tekst | osm_node, osm_bounding_box_center | osm_bounding_box_center | nie |
| osm_url | Odnośnik do obiektu źródłowego | tekst | URL | https://www.openstreetmap.org/way/208515700 | nie |
| source_name | Oryginalna nazwa OSM | tekst lub null | — | A0 | tak — np. E4 |
| source_address | Oryginalne elementy adresu OSM | obiekt | klucze street i housenumber | street: Profesora Stanisława Pigonia; housenumber: 1 | obiekt nie; jego wartości mogą być null |
| supplement_sources | Źródła zastosowanych uzupełnień | obiekt | klucze name/address z URL | address: https://portal.wspia.eu/pl/kontakt/ | może być pustym obiektem, gdy nie ma uzupełnień |

Nie łączymy odrębnych budynków wyłącznie dlatego, że mają ten sam adres. Nazwy wydziałów z OSM mogą być historyczne. Zestaw jest wyborem miejsc do projektu, nie pełnym rejestrem uczelni.
