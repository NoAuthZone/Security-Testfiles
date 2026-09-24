# Security-Testfiles

Intentionally vulnerable sample code with secure counterparts for testing and comparing security scanners: SAST tools, LLM-based code analysis, secret scanners, and linters.

> [!WARNING]
> These files contain **deliberate security vulnerabilities**. Use them for testing only. Never run, deploy, or reuse them as a template. All keys, hosts, and credentials are placeholders.

## Concept

- Every language has a **vulnerable** file and a **secure** file. The secure file solves the same tasks correctly. This lets you measure what a tool finds (recall) **and** how many false positives it produces.
- **No hints in the code:** no comments such as "VULNERABLE" and neutral file names. A tool, especially an LLM, should find the flaw, not the label.
- The expected findings (file, line, category) are listed in [`expected.yaml`](./expected.yaml). Exclude this file when scanning.

## Contents

| Language | Vulnerable | Vulnerabilities | Secure |
| --- | --- | --- | --- |
| C | `c/parser.c` | Format string, 2× buffer overflow (`strcpy`), command injection | `c/config.c` |
| C++ | `cpp/session.cpp` | Integer overflow in allocation, buffer overflow (`memcpy`), use-after-free | `cpp/cache.cpp` |
| Dart | `dart/api_client.dart` | Hardcoded API key, disabled TLS verification, SQL injection, command injection | `dart/sync_client.dart` |
| Go | `go/handlers.go` | SQL injection, command injection, SSRF | `go/api.go` |
| Java | `java/ReportController.java` | SQL injection, path traversal, XXE, MD5 for passwords | `java/InvoiceController.java` |
| JavaScript | `javascript/comments.js` | Prototype pollution, XSS, command injection | `javascript/newsletter.js` |
| PHP | `php/profile.php` | SQL injection, XSS, `unserialize` on cookie, file inclusion | `php/settings.php` |
| Python | `python/inventory_service.py` | SQL injection, command injection (`shell=True`), `pickle.loads` | `python/billing_service.py` |
| Ruby | `ruby/orders_controller.rb` | SQL injection, command injection, `YAML.unsafe_load`, open redirect | `ruby/products_controller.rb` |
| Rust | `rust/server.rs` | SQL injection, path traversal, command injection | `rust/store.rs` |
| TypeScript | `typescript/server.ts`, `Profile.tsx`, `fetcher.mts`, `legacy.cts` | SQL, command, XSS, open redirect, secret, SSRF, path traversal, `eval` | `typescript/accounts.ts`, `types.d.ts` |

In total: **26 files in 11 languages with 43 vulnerabilities**. The TypeScript files deliberately cover every extension (`.ts`, `.tsx`, `.mts`, `.cts`, `.d.ts`) to also test a tool's file discovery.

### Categories in `expected.yaml`

`sql` · `command` · `code_exec` · `deserialization` · `xss` · `path` · `ssrf` · `redirect` · `secret` · `xxe` · `weak_crypto` · `tls` · `prototype_pollution` · `format_string` · `buffer_overflow` · `integer_overflow` · `use_after_free`

## Usage with any tool

Clone the repository and point your tool at the directory, for example:

```bash
git clone https://github.com/NoAuthZone/Security-Testfiles.git
cd Security-Testfiles

semgrep scan --config auto --exclude expected.yaml .
gitleaks detect --no-git --source .
trivy fs --scanners secret .
```

Then compare the results with `expected.yaml`:

- **Hit:** a finding in the correct file, within ± `tolerance` lines (default: 3) of the expected line.
- **False positive:** any finding in a secure file (`findings: []`).
- **Additional:** extra findings in vulnerable files. These may be legitimate and are therefore counted separately.

## Automated evaluation (optional)

`scripts/evaluate_fixtures.py` compares a report with `expected.yaml` and prints recall, correct categories, and false positives per language. It only needs Python 3 and PyYAML.

```bash
pip install pyyaml
python scripts/evaluate_fixtures.py report.json --fixtures .
python scripts/evaluate_fixtures.py report.json --fixtures . --json          # metrics only
python scripts/evaluate_fixtures.py report.json --fixtures . --min-recall 0.7 --max-false-positives 3
```

The script expects a report in the following format. [FalconEYE-NG](https://github.com/NoAuthZone/FalconEYE-NG) produces it directly with `falconeye scan . -o json --output-file report.json`. Results from other tools can be converted with a few lines of code:

```json
{
  "findings": [
    {
      "issue": "SQL injection via string concatenation",
      "location": { "file_path": "java/ReportController.java", "line_start": 33, "line_end": 33 }
    }
  ]
}
```

A category counts as correct if the `issue` text contains a matching keyword (see `CATEGORY_KEYWORDS` in the script). With `--min-recall` or `--max-false-positives`, the script exits with code 1 if the threshold is missed, which makes it usable in CI.

`scripts/check_fixtures.py` is specific to FalconEYE-NG: it checks without an LLM whether FalconEYE detects, maps, and parses every file. It requires FalconEYE-NG to be installed.

## Adding a test file

1. Place the file in `<language>/` without hint comments and with a neutral name (avoid `safe`, `vuln`, `secure`, `bad`, `good`, and similar).
2. Add an entry to `expected.yaml` with the line, category, and a text snippet of that line (`contains`). Secure files get `findings: []`.
3. For every new language, also add a secure counterpart.

## Notes

- The placeholder keys (`sk_live_…FAKEKEYFORTESTS`, `AIzaSyD-FAKE-KEY…`) intentionally follow the format of real keys so that secret scanners trigger. GitHub Secret Scanning may flag them as well.
- The files are short, realistic snippets, not runnable applications.
