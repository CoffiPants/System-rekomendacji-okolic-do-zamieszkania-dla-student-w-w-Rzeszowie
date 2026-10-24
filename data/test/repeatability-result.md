## Wynik sprawdzenia powtarzalności

Porównano dwa uruchomienia procedury na tej samej próbce i konfiguracji. Po pierwszym uruchomieniu zachowano kopie w data/test/repeatability-reference/, usunięto wyłącznie dwa wygenerowane pliki z data/processed/ i odtworzono je skryptem.

| Plik | Pierwszy wynik | Drugi wynik | Te same pola i wartości |
|---|---:|---:|---|
| services.json | 500 | 500 | tak |
| universities.json | 28 | 28 | tak |

Pliki porównano po uporządkowaniu rekordów według ID, bez tolerancji liczbowej: nie wprowadzamy obliczeń przybliżonych.

Dane wejściowe i konfiguracja niezmienione: tak. Wyniki kontroli jakości identyczne: tak.

Wynik: **PASS**. Raport: data/test/repeatability-report.json.
