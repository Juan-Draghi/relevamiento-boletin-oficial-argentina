from pathlib import Path
import json
import os
import sys
import threading
import webbrowser

from flask import Flask, render_template, request


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from desktop_app.search_core import DEFAULT_URL, SearchError, get_pdf_content, load_keywords, search_pdf_content


def get_bundle_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parent


def get_user_data_dir() -> Path:
    appdata = os.getenv("LOCALAPPDATA") or os.getenv("APPDATA")
    if appdata:
        return Path(appdata) / "BibliotecaCPAU" / "RelevamientoBORA"
    return Path.home() / ".biblioteca-cpau" / "relevamiento-bora"


def get_keywords_file() -> Path:
    if getattr(sys, "frozen", False):
        return get_user_data_dir() / "keywords.json"
    return Path(__file__).with_name("keywords.json")


BUNDLE_ROOT = get_bundle_root()
TEMPLATES_DIR = BUNDLE_ROOT / "templates"
STATIC_DIR = BUNDLE_ROOT / "static"
DEFAULT_KEYWORDS_FILE = BUNDLE_ROOT / "keywords.json"
KEYWORDS_FILE = get_keywords_file()

app = Flask(__name__, template_folder=str(TEMPLATES_DIR), static_folder=str(STATIC_DIR))


def format_keywords_text(keywords: list[str]) -> str:
    return "\n".join(keywords)


def parse_keywords_text(raw_keywords: str) -> list[str]:
    keywords = [line.strip() for line in raw_keywords.splitlines() if line.strip()]
    if not keywords:
        raise SearchError("Debes ingresar al menos una keyword.")
    return keywords


def save_keywords_file(keywords: list[str]) -> None:
    KEYWORDS_FILE.parent.mkdir(parents=True, exist_ok=True)
    KEYWORDS_FILE.write_text(
        json.dumps({"keywords": keywords}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def ensure_keywords_file() -> list[str]:
    if KEYWORDS_FILE.exists():
        return load_keywords(KEYWORDS_FILE)

    keywords = load_keywords(DEFAULT_KEYWORDS_FILE)
    save_keywords_file(keywords)
    return keywords


@app.route("/", methods=["GET", "POST"])
def index():
    results: list[dict[str, object]] = []
    message = ""
    message_kind = "info"
    selected_url = DEFAULT_URL
    keywords = ensure_keywords_file()
    keywords_text = format_keywords_text(keywords)

    if request.method == "POST":
        action = request.form.get("action", "search")
        selected_url = request.form.get("url_pdf", "").strip() or DEFAULT_URL
        posted_keywords_text = request.form.get("keywords_text")

        try:
            if action == "save_keywords":
                keywords_text = (posted_keywords_text or "").strip()
                keywords = parse_keywords_text(keywords_text)
                save_keywords_file(keywords)
                message = f"Listado de keywords actualizado: {len(keywords)} terminos."
                message_kind = "success"
            else:
                if posted_keywords_text is not None and posted_keywords_text.strip():
                    keywords_text = posted_keywords_text.strip()
                    keywords = parse_keywords_text(keywords_text)
                else:
                    keywords = ensure_keywords_file()
                    keywords_text = format_keywords_text(keywords)

                uploaded_file = request.files.get("pdf_file")
                pdf_bytes = uploaded_file.read() if uploaded_file and uploaded_file.filename else None
                pdf_content = get_pdf_content(selected_url, pdf_bytes)
                results = search_pdf_content(pdf_content, keywords)
                if results:
                    message = f"Se hallaron {len(results)} coincidencias."
                    message_kind = "success"
                else:
                    message = "No se detecto normativa relevante."
                    message_kind = "info"
        except SearchError as exc:
            message = f"Error: {exc}"
            message_kind = "error"

    return render_template(
        "index.html",
        default_url=DEFAULT_URL,
        keywords_count=len(keywords),
        keywords_text=keywords_text,
        message=message,
        message_kind=message_kind,
        results=results,
        selected_url=selected_url,
    )


def open_browser(port: int) -> None:
    webbrowser.open_new(f"http://127.0.0.1:{port}")


def main() -> None:
    port = 7861
    threading.Timer(1.0, open_browser, args=[port]).start()
    app.run(host="127.0.0.1", port=port, debug=False)


if __name__ == "__main__":
    main()
