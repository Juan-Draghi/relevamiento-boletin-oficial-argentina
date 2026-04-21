import io
import json
import re
from pathlib import Path
from typing import Iterable

import pdfplumber
import requests


DEFAULT_URL = "https://s3.arsat.com.ar/cdn-bo-001/pdf-del-dia/primera.pdf"


class SearchError(Exception):
    """Expected error while loading, downloading, or processing input files."""


def load_keywords(keywords_file: str | Path) -> list[str]:
    """Load keywords from the JSON file used by the desktop app."""
    try:
        with open(keywords_file, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError as exc:
        raise SearchError(f"No se encontro el archivo de keywords: {keywords_file}") from exc
    except json.JSONDecodeError as exc:
        raise SearchError(f"El archivo de keywords no es JSON valido: {exc}") from exc

    if isinstance(data, dict):
        keywords = data.get("keywords", [])
    else:
        keywords = data

    if not isinstance(keywords, list):
        raise SearchError("El archivo de keywords debe contener una lista.")

    return [str(keyword) for keyword in keywords if str(keyword).strip()]


def get_pdf_content(url_pdf: str | None, pdf_bytes: bytes | None) -> bytes:
    """Return PDF bytes from an uploaded file or from a URL."""
    if pdf_bytes:
        return pdf_bytes

    url = (url_pdf or DEFAULT_URL).strip()
    if not url:
        url = DEFAULT_URL

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise SearchError(f"No se pudo descargar el PDF: {exc}") from exc

    return response.content


def compile_keyword(term: str) -> re.Pattern[str]:
    """Compile a term as regex and fall back to a literal search if invalid."""
    try:
        return re.compile(term, re.IGNORECASE)
    except re.error:
        return re.compile(re.escape(term), re.IGNORECASE)


def iter_page_results(
    pdf_content: bytes,
    keywords: Iterable[str],
) -> Iterable[tuple[int, int, list[dict[str, object]]]]:
    """Yield search results page by page, including progress information."""
    try:
        with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
            num_pages = len(pdf.pages)
            if num_pages == 0:
                raise SearchError("El PDF no contiene paginas legibles.")

            compiled_keywords = [(term, compile_keyword(term)) for term in keywords]

            for page_index, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                page_results: list[dict[str, object]] = []

                if text:
                    for term, pattern in compiled_keywords:
                        for match in pattern.finditer(text):
                            start = max(match.start() - 200, 0)
                            end = match.end() + 200
                            fragment = text[start:end].replace("\n", " ").strip()
                            page_results.append(
                                {
                                    "keyword": term,
                                    "page_number": page_index,
                                    "fragment": fragment,
                                }
                            )

                yield page_index, num_pages, page_results
    except SearchError:
        raise
    except Exception as exc:
        raise SearchError(f"No se pudo procesar el PDF: {exc}") from exc


def search_pdf_content(pdf_content: bytes, keywords: Iterable[str]) -> list[dict[str, object]]:
    """Search all PDF pages and return a flat list of matches."""
    results: list[dict[str, object]] = []
    for _page_number, _num_pages, page_results in iter_page_results(pdf_content, keywords):
        results.extend(page_results)
    return results
