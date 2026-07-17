import argparse
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = (
    PROJECT_ROOT
    / "skills"
    / "gestionar-keywords-bora-nacional"
    / "scripts"
    / "manage_keyword.py"
)
SPEC = importlib.util.spec_from_file_location("manage_keyword", SCRIPT_PATH)
MANAGE_KEYWORD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MANAGE_KEYWORD)


class KeywordManagerTests(unittest.TestCase):
    def test_detects_normalized_duplicate(self):
        result = MANAGE_KEYWORD.analyze_candidate(
            "CONSTRUCCION",
            ["construccion", "arquitectura"],
        )
        self.assertEqual(result["status"], "duplicate")

    def test_detects_coverage_by_existing_regex(self):
        result = MANAGE_KEYWORD.analyze_candidate(
            "Resolucion",
            [r"[Rr]esoluci[oó]n"],
        )
        self.assertEqual(result["status"], "covered")

    def test_add_writes_keyword_and_log_after_examples_pass(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir)
            (repo / "desktop_app").mkdir()
            (repo / "docs/seguimiento").mkdir(parents=True)
            (repo / "docs/adr").mkdir(parents=True)
            (repo / "desktop_app/keywords.json").write_text(
                json.dumps({"keywords": ["arquitectura"]}),
                encoding="utf-8",
            )
            (repo / "desktop_app/search_core.py").write_text("", encoding="utf-8")
            (repo / "docs/seguimiento/log_cambios.md").write_text(
                "# Log de cambios\n",
                encoding="utf-8",
            )
            (repo / "docs/adr/0005-gestion-controlada-de-keywords.md").write_text(
                "# ADR-0005\n",
                encoding="utf-8",
            )

            args = argparse.Namespace(
                repo=str(repo),
                value="planeamiento urbano",
                reason="Incorporar un concepto relevante.",
                evidence="Caso de prueba.",
                positive=["Normas de planeamiento urbano"],
                negative=["Normas de transito"],
                entry_date="2026-07-16",
            )
            MANAGE_KEYWORD.add_keyword(args)

            data = json.loads((repo / "desktop_app/keywords.json").read_text(encoding="utf-8"))
            log = (repo / "docs/seguimiento/log_cambios.md").read_text(encoding="utf-8")

            self.assertEqual(data["keywords"], ["arquitectura", "planeamiento urbano"])
            self.assertIn("planeamiento urbano", log)
            self.assertIn("ADR-0005", log)


if __name__ == "__main__":
    unittest.main()
