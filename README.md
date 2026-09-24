# FalconEYE-Testdateien

26 Testdateien in 11 Sprachen mit **43 absichtlich eingebauten Schwachstellen**.
Zu jeder Sprache gibt es mindestens eine verwundbare und eine sichere Datei.
Die sicheren Dateien lösen dieselben Aufgaben korrekt und prüfen auf Fehlalarme.

**Nur zum Testen, niemals produktiv verwenden.** Alle Schlüssel sind Platzhalter.

## Warum ohne Kommentare?

Der Code enthält keine Hinweise wie „VULNERABLE“ und hat neutrale Dateinamen.
Das LLM liest Kommentare und Dateinamen mit und würde sonst die Beschriftung
finden statt der Lücke. Die Erwartungen stehen deshalb in `expected.yaml`,
die FalconEYE nicht scannt. `tests/test_fixtures.py` stellt sicher, dass das so bleibt.

## Inhalt

| Sprache | Verwundbare Datei | Schwachstellen | Sichere Datei |
|---|---|---|---|
| C | `parser.c` | Format String, 2× Buffer Overflow (`strcpy`), Command Injection | `config.c` |
| C++ | `session.cpp` | Integer Overflow bei Allokation, Buffer Overflow (`memcpy`), Use-after-free | `cache.cpp` |
| Dart | `api_client.dart` | Hartkodierter API-Key, TLS-Prüfung deaktiviert, SQL-Injection, Command Injection | `sync_client.dart` |
| Go | `handlers.go` | SQL-Injection, Command Injection, SSRF | `api.go` |
| Java | `ReportController.java` | SQL-Injection, Path Traversal, XXE, MD5 für Passwörter | `InvoiceController.java` |
| JavaScript | `comments.js` | Prototype Pollution, XSS, Command Injection | `newsletter.js` |
| PHP | `profile.php` | SQL-Injection, XSS, `unserialize` auf Cookie, File Inclusion | `settings.php` |
| Python | `inventory_service.py` | SQL-Injection, Command Injection (`shell=True`), `pickle.loads` | `billing_service.py` |
| Ruby | `orders_controller.rb` | SQL-Injection, Command Injection, `YAML.unsafe_load`, Open Redirect | `products_controller.rb` |
| Rust | `server.rs` | SQL-Injection, Path Traversal, Command Injection | `store.rs` |
| TypeScript | `server.ts`, `Profile.tsx`, `fetcher.mts`, `legacy.cts` | SQL, Command, XSS, Open Redirect, Secret, SSRF, Path Traversal, `eval` | `accounts.ts`, `types.d.ts` |

Die genauen Zeilen stehen in `expected.yaml`.

## Nutzung

```bash
# 1. Ohne LLM: Erkennung, Plugin-Zuordnung, Parsing
python scripts/check_fixtures.py
pytest -q tests

# 2. Mit LLM: Scan als JSON
falconeye scan tests/fixtures -o json --output-file report.json --force-reindex

# 3. Auswertung
python scripts/evaluate_fixtures.py report.json
python scripts/evaluate_fixtures.py report.json --json                     # nur Kennzahlen
python scripts/evaluate_fixtures.py report.json --min-recall 0.7 --max-false-positives 3
```

Die Auswertung zeigt pro Sprache Treffer, korrekte Kategorien, Fehlalarme und
unerwartete Findings, danach alle übersehenen Lücken und Fehlalarme im Detail.
Speichere die JSON-Kennzahlen nach jedem Lauf, dann siehst du, ob ein neuer
Prompt oder ein anderes Modell besser oder schlechter abschneidet.

## Neue Testdatei hinzufügen

1. Datei unter `tests/fixtures/<sprache>/` ablegen, ohne Hinweiskommentare,
   mit neutralem Namen.
2. Eintrag in `expected.yaml` mit Zeile, Kategorie und einem Textausschnitt der Zeile.
3. `pytest -q tests` prüft Syntax, Zeilen und Hinweisfreiheit.
