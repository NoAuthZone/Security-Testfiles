"""Prüft ohne LLM, ob FalconEYE jede Testdatei erkennt, zuordnet und parsen kann.

    python scripts/check_fixtures.py
"""

import sys
from pathlib import Path

import tree_sitter_language_pack as tslp

from falconeye.domain.services.language_detector import LanguageDetector
from falconeye.infrastructure.ast.ast_analyzer import EnhancedASTAnalyzer
from falconeye.infrastructure.plugins.plugin_registry import PluginRegistry

FIXTURES = Path(__file__).resolve().parent.parent / "tests" / "fixtures"

registry = PluginRegistry()
registry.load_all_plugins()
analyzer = EnhancedASTAnalyzer()

errors = warnings = 0
print(f"{'Datei':<36} {'Erkannt':<11} {'Plugin':<11} {'AST':<11} Syntax")
print("-" * 78)
for path in sorted(p for p in FIXTURES.rglob("*") if p.is_file() and p.suffix in LanguageDetector.EXTENSION_TO_LANGUAGE):
    rel = str(path.relative_to(FIXTURES))
    language = LanguageDetector.EXTENSION_TO_LANGUAGE.get(path.suffix)
    plugin = registry.get_plugin(language) if language else None
    ast_lang = analyzer.LANGUAGE_MAP.get(path.suffix)
    grammar = ast_lang or language
    try:
        syntax_ok = not tslp.get_parser(grammar).parse(path.read_bytes()).root_node.has_error
    except Exception:
        syntax_ok = False

    note = ""
    if not (language and plugin and syntax_ok):
        errors += 1
        note = "  <-- Fehler"
    elif not ast_lang:
        warnings += 1
        note = "  <-- keine AST-Metadaten"
    print(f"{rel:<36} {language or '-':<11} {plugin.language_name if plugin else '-':<11} "
          f"{ast_lang or '-':<11} {'ok' if syntax_ok else 'FEHLER'}{note}")

print("-" * 78)
print(f"{errors} Fehler, {warnings} Warnungen")
sys.exit(1 if errors else 0)
