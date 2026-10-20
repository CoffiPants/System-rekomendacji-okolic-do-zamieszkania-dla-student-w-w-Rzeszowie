# System rekomendacji okolic do zamieszkania dla studentów w Rzeszowie

## Opis problemu
Celem projektu jest opracowanie systemu rekomendacji, który pomoże studentom znaleźć odpowiednie okolice do zamieszkania w Rzeszowie.

## Zespół
- Członkowie zespołu:
- Dana Stadnyk
- Valentyna Boksha
- Serhii Popovych
- Paulina Michalska

## Dokumentacja
- [Opis problemu](docs/problem.md)
- [Opis danych](docs/data.md)

## Przygotowanie danych — Lab 3

Wymagane środowisko: Python 3.10 lub nowszy. Skrypt korzysta tylko z biblioteki standardowej; nie wymaga instalowania pakietów ani dostępu do internetu.

Uruchomienie z katalogu repozytorium:

```shell
python scripts/prepare_data.py
```

Wejście: data/raw/sample.json, data/raw/universities.json, config/university-selection.json.
Wynik: data/processed/services.json i data/processed/universities.json.

Dla bieżącej próbki: 500 usług, w tym 21 bez nazwy źródłowej, oraz 28 wybranych miejsc zajęć. Brakującym nazwom usług przypisano etykiety kategorii z ID, zachowując oznaczenie name_missing. Reguły wyboru uczelni i źródła uzupełnień znajdują się w config/university-selection.json.

Skrypt nie zmienia plików raw. Nie pobiera aktualizacji API i nie oblicza jeszcze tras ani rankingu okolic. Nieprawidłowe identyfikatory, współrzędne lub reguły powodują zakończenie z komunikatem błędu.
