"""Odtworzenie wyników z tej samej próbki oraz porównanie dwóch uruchomień."""

import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = {"services.json": "services", "universities.json": "locations"}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_pipeline():
    for name in ("prepare_data.py", "check_data.py"):
        subprocess.run([sys.executable, str(ROOT / "scripts" / name)], cwd=ROOT, check=True)


def normalized(path, key):
    document = json.loads(path.read_text(encoding="utf-8-sig"))
    rows = document[key]
    if not isinstance(rows, list) or not rows:
        raise ValueError("Brak niepustego zbioru wynikowego: " + path.name)
    document[key] = sorted(rows, key=lambda row: row["id"])
    return document


def main():
    sources = [ROOT / "data/raw/sample.json", ROOT / "data/raw/universities.json", ROOT / "config/university-selection.json"]
    initial_hashes = {str(path.relative_to(ROOT)): digest(path) for path in sources}
    processed = (ROOT / "data/processed").resolve()
    reference = ROOT / "data/test/repeatability-reference"
    reference.mkdir(parents=True, exist_ok=True)

    # Pierwsze uruchomienie i zachowanie punktu odniesienia.
    run_pipeline()
    first_quality = json.loads((ROOT / "data/test/quality-report.json").read_text(encoding="utf-8"))
    for filename in OUTPUTS:
        shutil.copyfile(processed / filename, reference / filename)

    # Usuwamy tylko dwa znane pliki wygenerowane, po sprawdzeniu ich ścieżek.
    targets = [(processed / filename).resolve() for filename in OUTPUTS]
    for target in targets:
        if target.parent != processed or not target.is_file():
            raise ValueError("Nieprawidłowa ścieżka wyniku: " + str(target))
    for target in targets:
        target.unlink()

    # Odtworzenie od początku; brak internetu i ponownego pobrania API.
    run_pipeline()
    second_quality = json.loads((ROOT / "data/test/quality-report.json").read_text(encoding="utf-8"))
    comparisons = []
    for filename, key in OUTPUTS.items():
        first = normalized(reference / filename, key)
        second = normalized(processed / filename, key)
        row = {
            "file": filename,
            "first_records": len(first[key]),
            "second_records": len(second[key]),
            "same_fields": [sorted(record) for record in first[key]] == [sorted(record) for record in second[key]],
            "same_values": first == second,
            "same_bytes": digest(reference / filename) == digest(processed / filename),
        }
        comparisons.append(row)
    unchanged = initial_hashes == {str(path.relative_to(ROOT)): digest(path) for path in sources}
    passed = unchanged and first_quality == second_quality and all(row["same_values"] and row["same_fields"] for row in comparisons)
    report = {"success": passed, "source_hashes": initial_hashes, "inputs_unchanged": unchanged, "same_quality_results": first_quality == second_quality, "comparisons": comparisons}
    path = ROOT / "data/test/repeatability-report.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = ["## Wynik sprawdzenia powtarzalności", "", "Porównano dwa uruchomienia procedury na tej samej próbce i konfiguracji. Po pierwszym uruchomieniu zachowano kopie w data/test/repeatability-reference/, usunięto wyłącznie dwa wygenerowane pliki z data/processed/ i odtworzono je skryptem.", "", "| Plik | Pierwszy wynik | Drugi wynik | Te same pola i wartości |", "|---|---:|---:|---|"]
    for row in comparisons:
        lines.append(f"| {row['file']} | {row['first_records']} | {row['second_records']} | {'tak' if row['same_values'] and row['same_fields'] else 'nie'} |")
    lines.extend(["", "Pliki porównano po uporządkowaniu rekordów według ID, bez tolerancji liczbowej: nie wprowadzamy obliczeń przybliżonych.", "", f"Dane wejściowe i konfiguracja niezmienione: {'tak' if unchanged else 'nie'}. Wyniki kontroli jakości identyczne: {'tak' if first_quality == second_quality else 'nie'}.", "", "Wynik: **" + ("PASS" if passed else "FAIL") + "**. Raport: data/test/repeatability-report.json.", ""])
    (ROOT / "data/test/repeatability-result.md").write_text("\n".join(lines), encoding="utf-8")
    processing_path = ROOT / "docs/processing.md"
    if processing_path.exists():
        current = processing_path.read_text(encoding="utf-8-sig")
        section = "## 9. Powtarzalność procesu\n" + "\n".join(lines[1:]) + "\n\n"
        current, replacements = re.subn(r"## 9\. Powtarzalność procesu[\s\S]*?(?=## 10\. Ograniczenia)", lambda match: section, current, count=1)
        if replacements:
            processing_path.write_text(current, encoding="utf-8")
    print("Powtarzalnosc:", "PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        print("BLAD:", error, file=sys.stderr)
        print("Jesli zabraklo plikow wynikowych, po usunieciu przyczyny uruchom scripts/prepare_data.py.", file=sys.stderr)
        sys.exit(1)
