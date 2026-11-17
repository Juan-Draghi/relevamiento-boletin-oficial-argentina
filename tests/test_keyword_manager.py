import argparse
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = (
    PROJECT_ROOT
    / ".claude"
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


def make_repo(root: Path, keywords: list[str]) -> Path:
    """Create a minimal BORA repository layout for the keyword manager."""
    (root / "desktop_app").mkdir()
    (root / "docs/seguimiento").mkdir(parents=True)
    (root / "docs/adr").mkdir(parents=True)
    (root / "desktop_app/keywords.json").write_text(
        json.dumps({"keywords": keywords}), encoding="utf-8"
    )
    (root / "desktop_app/search_core.py").write_text("", encoding="utf-8")
    (root / "docs/seguimiento/log_cambios.md").write_text("# Log de cambios\n", encoding="utf-8")
    (root / "docs/adr/0005-gestion-controlada-de-keywords.md").write_text("# ADR-0005\n", encoding="utf-8")
    return root


def read_state(repo: Path) -> tuple[list[str], str]:
    data = json.loads((repo / "desktop_app/keywords.json").read_text(encoding="utf-8"))
    log = (repo / "docs/seguimiento/log_cambios.md").read_text(encoding="utf-8")
    return data["keywords"], log


class ReplaceAndRemoveTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.repo = make_repo(
            Path(self.temp_dir.name),
            ["arquitectura", "centro de trasnformación", "construcción", "obra pública"],
        )

    def change_args(self, **kwargs):
        defaults = dict(
            repo=str(self.repo),
            reason="Motivo de prueba.",
            evidence="Caso de prueba.",
            positive=[],
            negative=[],
            entry_date="2026-11-17",
        )
        defaults.update(kwargs)
        return argparse.Namespace(**defaults)

    def test_replace_keeps_position_and_logs_both_values(self):
        MANAGE_KEYWORD.replace_keyword(self.change_args(
            current="centro de trasnformación",
            value="centros? de transformación",
            positive=["Instalacion de centro de transformación"],
            negative=["Centro de salud"],
        ))
        keywords, log = read_state(self.repo)
        self.assertEqual(keywords[1], "centros? de transformación")
        self.assertEqual(len(keywords), 4)
        self.assertIn("se reemplazo `centro de trasnformación`", log)

    def test_replace_rejects_value_covered_by_another_keyword(self):
        with self.assertRaises(MANAGE_KEYWORD.KeywordManagerError):
            MANAGE_KEYWORD.replace_keyword(self.change_args(
                current="centro de trasnformación",
                value="Construccion",
                positive=["construccion"],
                negative=["transito"],
            ))
        keywords, log = read_state(self.repo)
        self.assertIn("centro de trasnformación", keywords)
        self.assertNotIn("Ajuste de keywords", log)

    def test_replace_requires_existing_exact_value(self):
        with self.assertRaises(MANAGE_KEYWORD.KeywordManagerError):
            MANAGE_KEYWORD.replace_keyword(self.change_args(
                current="inexistente", value="otro", positive=["otro"], negative=["x"],
            ))

    def test_remove_deletes_value_and_logs(self):
        MANAGE_KEYWORD.remove_keyword(self.change_args(
            value="construcción",
            negative=["Ley de construcción de caminos"],
        ))
        keywords, log = read_state(self.repo)
        self.assertNotIn("construcción", keywords)
        self.assertIn("se elimino `construcción`", log)

    def test_remove_fails_if_negative_still_detected_by_other_keyword(self):
        with self.assertRaises(MANAGE_KEYWORD.KeywordManagerError):
            MANAGE_KEYWORD.remove_keyword(self.change_args(
                value="construcción",
                negative=["construcción de obra pública"],
            ))
        keywords, _ = read_state(self.repo)
        self.assertIn("construcción", keywords)

    def test_remove_fails_if_positive_loses_coverage(self):
        with self.assertRaises(MANAGE_KEYWORD.KeywordManagerError):
            MANAGE_KEYWORD.remove_keyword(self.change_args(
                value="construcción",
                positive=["Codigo de construcción"],
            ))

    def test_remove_requires_some_example(self):
        with self.assertRaises(MANAGE_KEYWORD.KeywordManagerError):
            MANAGE_KEYWORD.remove_keyword(self.change_args(value="construcción"))


if __name__ == "__main__":
    unittest.main()
