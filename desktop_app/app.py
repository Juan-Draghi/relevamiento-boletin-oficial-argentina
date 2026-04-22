from pathlib import Path
import json
import os
import sys
import threading
import uuid
import webbrowser

from flask import Flask, jsonify, render_template, request


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
SEARCH_JOBS: dict[str, dict[str, object]] = {}
SEARCH_JOBS_LOCK = threading.Lock()


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


def set_job_state(job_id: str, **updates: object) -> None:
    with SEARCH_JOBS_LOCK:
        if job_id in SEARCH_JOBS:
            SEARCH_JOBS[job_id].update(updates)


def create_search_job(url_pdf: str, pdf_bytes: bytes | None) -> str:
    job_id = uuid.uuid4().hex
    with SEARCH_JOBS_LOCK:
        SEARCH_JOBS[job_id] = {
            "id": job_id,
            "status": "queued",
            "message": "Preparando busqueda...",
            "progress_percent": 2,
            "current_page": 0,
            "num_pages": 0,
            "results": [],
            "selected_url": url_pdf,
        }

    thread = threading.Thread(
        target=run_search_job,
        args=(job_id, url_pdf, pdf_bytes),
        daemon=True,
    )
    thread.start()
    return job_id


def run_search_job(job_id: str, url_pdf: str, pdf_bytes: bytes | None) -> None:
    try:
        set_job_state(job_id, status="running", message="Obteniendo PDF...", progress_percent=8)
        keywords = ensure_keywords_file()
        pdf_content = get_pdf_content(url_pdf, pdf_bytes)
        set_job_state(job_id, message="Procesando PDF...", progress_percent=12)

        results: list[dict[str, object]] = []
        last_num_pages = 0
        for page_number, num_pages, page_results in search_pdf_content_with_progress(pdf_content, keywords):
            results.extend(page_results)
            last_num_pages = num_pages
            progress_percent = 12 + int((page_number / num_pages) * 86)
            set_job_state(
                job_id,
                status="running",
                message=f"Analizando pagina {page_number} de {num_pages}...",
                current_page=page_number,
                num_pages=num_pages,
                progress_percent=min(progress_percent, 98),
            )

        if results:
            message = f"Se hallaron {len(results)} coincidencias."
        else:
            message = "No se detecto normativa relevante."

        set_job_state(
            job_id,
            status="completed",
            message=message,
            current_page=last_num_pages,
            num_pages=last_num_pages,
            progress_percent=100,
            results=results,
        )
    except SearchError as exc:
        set_job_state(
            job_id,
            status="error",
            message=f"Error: {exc}",
            progress_percent=100,
        )


def search_pdf_content_with_progress(pdf_content: bytes, keywords: list[str]):
    from desktop_app.search_core import iter_page_results

    yield from iter_page_results(pdf_content, keywords)


@app.route("/", methods=["GET", "POST"])
def index():
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

                message = "Usa el boton de busqueda para iniciar el analisis."
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
        selected_url=selected_url,
    )


@app.post("/api/search")
def api_search():
    selected_url = request.form.get("url_pdf", "").strip() or DEFAULT_URL
    uploaded_file = request.files.get("pdf_file")
    pdf_bytes = uploaded_file.read() if uploaded_file and uploaded_file.filename else None
    job_id = create_search_job(selected_url, pdf_bytes)
    return jsonify({"job_id": job_id})


@app.get("/api/search/<job_id>")
def api_search_status(job_id: str):
    with SEARCH_JOBS_LOCK:
        job = SEARCH_JOBS.get(job_id)

    if not job:
        return jsonify({"status": "error", "message": "Busqueda no encontrada."}), 404

    return jsonify(job)


def open_browser(port: int) -> None:
    webbrowser.open_new(f"http://127.0.0.1:{port}")


def main() -> None:
    port = 7861
    threading.Timer(1.0, open_browser, args=[port]).start()
    app.run(host="127.0.0.1", port=port, debug=False)


if __name__ == "__main__":
    main()
