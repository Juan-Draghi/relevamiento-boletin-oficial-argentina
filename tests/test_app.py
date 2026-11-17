import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from desktop_app import app as app_module
from desktop_app.app import app, sync_keywords


class DesktopAppTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_index_is_operational_and_has_no_keyword_editor(self):
        response = self.client.get("/")
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('name="source_mode"', html)
        self.assertIn('id="search-form"', html)
        self.assertIn('id="results-body"', html)
        self.assertNotIn("keywords-editor", html)
        self.assertNotIn('name="keywords_text"', html)

    def test_index_does_not_accept_keyword_updates(self):
        response = self.client.post(
            "/",
            data={"action": "save_keywords", "keywords_text": "termino nuevo"},
        )
        self.assertEqual(response.status_code, 405)

    def test_sync_first_run_keeps_personal_terms_and_adds_defaults(self):
        user = ["termino personalizado", "arquitectura"]
        bundled = ["arquitectura", "construccion"]

        self.assertEqual(
            sync_keywords(user, bundled, None),
            ["arquitectura", "construccion", "termino personalizado"],
        )

    def test_sync_drops_removed_and_replaced_bundled_terms(self):
        previous = ["arquitectura", "centro de trasnformacion", "construccion"]
        bundled = ["arquitectura", "centros? de transformacion"]
        user = ["arquitectura", "centro de trasnformacion", "construccion", "termino propio"]

        self.assertEqual(
            sync_keywords(user, bundled, previous),
            ["arquitectura", "centros? de transformacion", "termino propio"],
        )

    def test_ensure_keywords_file_writes_copy_and_build_record(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            bundled_file = root / "bundle" / "keywords.json"
            user_file = root / "user" / "keywords.json"
            bundled_file.parent.mkdir()
            user_file.parent.mkdir()
            bundled_file.write_text(json.dumps({"keywords": ["arquitectura"]}), encoding="utf-8")
            user_file.write_text(
                json.dumps({"keywords": ["arquitectura", "construccion", "propio"]}),
                encoding="utf-8",
            )
            build_file = user_file.with_name("keywords_build.json")
            build_file.write_text(
                json.dumps({"keywords": ["arquitectura", "construccion"]}), encoding="utf-8"
            )

            with mock.patch.object(app_module, "DEFAULT_KEYWORDS_FILE", bundled_file),                     mock.patch.object(app_module, "KEYWORDS_FILE", user_file):
                result = app_module.ensure_keywords_file()

            self.assertEqual(result, ["arquitectura", "propio"])
            saved = json.loads(user_file.read_text(encoding="utf-8"))["keywords"]
            build = json.loads(build_file.read_text(encoding="utf-8"))["keywords"]
            self.assertEqual(saved, ["arquitectura", "propio"])
            self.assertEqual(build, ["arquitectura"])

if __name__ == "__main__":
    unittest.main()
