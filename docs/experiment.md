# Lab 4 — porównanie metod rekomendacji

## Pytanie i wymaganie

Czy ranking uwzględniający odległość od uczelni, sklepu, przystanku i parku daje
lepsze rekomendacje niż wariant bazowy, który sortuje okolice wyłącznie według
odległości od wybranego miejsca zajęć? Eksperyment odnosi się do wymagań R2,
R4 i R5 z `docs/problem.md`: użytkownik podaje preferencje, otrzymuje do
trzech wyników i może rozumieć ich ocenę.

## Dane i warunki

- `data/processed/services.json`: 500 obiektów OSM (274 sklepy, 185 przystanków,
  41 parków), stan zapisany w repozytorium.
- `data/processed/universities.json`: 28 lokalizacji zajęć.
- `config/residential-areas.json`: 25 kół o promieniu 500 m; środki są
  przybliżonymi punktami w zabudowie mieszkaniowej i wymagają późniejszej
  weryfikacji na mapie.
- Jednostką obserwacji jest okolica. Odległość jest liczona wzorem haversine
  w linii prostej od środka obszaru do najbliższego obiektu danej kategorii.
- Wybrana lokalizacja zajęć: `way/197227711` (Budynek P, Politechnika
  Rzeszowska). W aplikacji identyfikator powinien pochodzić z formularza.

## Warianty

**Baseline** to 100-punktowa ocena odległości od wybranej uczelni, z limitem
3000 m. **Metoda proponowana** jest średnią ważoną czterech ocen:

| Kryterium | Limit punktacji | Waga |
|---|---:|---:|
| uczelnia | 3000 m | 3 |
| sklep | 1000 m | 2 |
| przystanek | 600 m | 2 |
| park | 1500 m | 2 |

Każda ocena ma postać `100 * max(0, 1 - odległość / limit)`. Wyższy wynik
oznacza lepsze dopasowanie. To nie jest trasa piesza: wynik nie uwzględnia
ulic, przejść ani rzeki.

## Miara i kryterium praktyczne

Ponieważ dane nie zawierają etykiety „najlepsza okolica” od użytkownika,
porównujemy średnią pełną użyteczność (wynik proponowanej metody) wśród trzech
rekomendacji baseline'u i metody proponowanej. Wyższa wartość jest lepsza.
Jako wynik dodatkowy zapisujemy liczbę wspólnych obszarów w top 3. Praktycznie
metoda jest korzystniejsza, jeśli poprawia średnią pełną użyteczność bez
naruszania limitu trzech rekomendacji.

## Źródła

1. S. Opricovic, G.-H. Tzeng, *Compromise solution by MCDM methods: A
   comparative analysis of VIKOR and TOPSIS*, European Journal of Operational
   Research, 2004, DOI: https://doi.org/10.1016/S0377-2217(03)00020-1.
   Źródło uzasadnia porównywanie wariantów wielokryterialnych przy wielu
   kryteriach; wykorzystano prostą, jawną agregację ważoną zamiast
   implementowania TOPSIS/VIKOR.
2. T. L. Saaty, *Decision making with the analytic hierarchy process*,
   International Journal of Services Sciences, 2008, DOI:
   https://doi.org/10.1504/IJSSCI.2008.017590. Źródło opisuje znaczenie wag
   kryteriów; wykorzystano wagi 3/2/2/2 jako założenie demonstracyjne, a nie
   pomiar preferencji użytkowników.

Alternatywą byłoby wyznaczanie rzeczywistych tras pieszych. Odrzucono ją w
Lab 4, ponieważ projekt nie ma jeszcze routera ani zweryfikowanych wejść do
budynków; należy ją rozważyć po uzupełnieniu danych.

## Odtworzenie

Z katalogu repozytorium:

```shell
python scripts/prepare_data.py
python scripts/compare_methods.py
```

Wyniki podstawowe są w `results/lab4/`. Próba wrażliwości zmienia jeden
parametr — limit punktacji dla sklepów z 1000 m na 1500 m:

```shell
python scripts/compare_methods.py \
  --shop-limit 1500 \
  --output results/lab4/sensitivity
```

## Wynik porównania

Dla budynku P wynik podstawowy daje średnią pełną użyteczność top 3 równą
**59,8886** dla baseline'u i **63,1586** dla metody proponowanej; top 3 mają
**2 wspólne obszary**. Po zmianie limitu sklepu na 1500 m wartości wynoszą
odpowiednio **61,5153** i **64,6097**, a wniosek się nie zmienia. Szczegóły
jednostkowe i pełne rankingi znajdują się w plikach CSV.

## Wynik i ograniczenia

Wyniki liczbowe są zapisane w CSV i powinny być interpretowane razem z
`observations.csv` oraz rankingami. Eksperyment sprawdza procedurę na
przybliżonych środkach obszarów i obecnym wycinku OSM, nie dowodzi, że
rekomendacje odpowiadają preferencjom studentów. Brakuje walidacji użytkowników,
tras pieszych i pełnej kontroli kompletności usług. Po zmianie parametrów na
podstawie wyników ten sam zbiór jest używany do doboru, więc potrzebna będzie
ocena na osobnym zbiorze lub z udziałem użytkowników.
