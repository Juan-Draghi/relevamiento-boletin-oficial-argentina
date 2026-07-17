import unittest

from desktop_app.app import app, merge_keywords


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

    def test_merge_keywords_preserves_user_order_and_adds_defaults(self):
        existing = ["termino personalizado", "arquitectura"]
        defaults = ["arquitectura", "construccion"]

        self.assertEqual(
            merge_keywords(existing, defaults),
            ["termino personalizado", "arquitectura", "construccion"],
        )


if __name__ == "__main__":
    unittest.main()
