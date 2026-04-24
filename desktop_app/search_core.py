import io
import html
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


def normalize_page_text(text: str) -> str:
    """Keep search positions stable while removing line breaks from excerpts."""
    return text.replace("\r", " ").replace("\n", " ")


def collect_page_matches(
    text: str,
    compiled_keywords: list[tuple[str, re.Pattern[str]]],
) -> list[dict[str, object]]:
    """Collect all regex matches for a page."""
    matches: list[dict[str, object]] = []
    for term, pattern in compiled_keywords:
        for match in pattern.finditer(text):
            matches.append(
                {
                    "keyword": term,
                    "start": match.start(),
                    "end": match.end(),
                }
            )

    matches.sort(key=lambda item: (int(item["start"]), int(item["end"])))
    return matches


def get_detected_keywords(matches: list[dict[str, object]]) -> list[str]:
    """Return keywords in first-detected order without duplicates."""
    detected_keywords: list[str] = []
    seen_keywords: set[str] = set()

    for match in matches:
        keyword = str(match["keyword"])
        if keyword not in seen_keywords:
            seen_keywords.add(keyword)
            detected_keywords.append(keyword)

    return detected_keywords


def merge_excerpt_ranges(
    matches: list[dict[str, object]],
    text_length: int,
    context_chars: int = 120,
    join_gap: int = 50,
    max_segments: int = 3,
) -> list[tuple[int, int]]:
    """Build a small set of page excerpts around the detected matches."""
    ranges: list[tuple[int, int]] = []

    for match in matches:
        start = max(int(match["start"]) - context_chars, 0)
        end = min(int(match["end"]) + context_chars, text_length)

        if not ranges:
            ranges.append((start, end))
            continue

        last_start, last_end = ranges[-1]
        if start <= last_end + join_gap:
            ranges[-1] = (last_start, max(last_end, end))
        else:
            ranges.append((start, end))

    return ranges[:max_segments]


def render_highlighted_segment(
    text: str,
    segment_start: int,
    segment_end: int,
    matches: list[dict[str, object]],
) -> str:
    """Render one excerpt segment with highlighted matches."""
    html_parts: list[str] = []
    cursor = segment_start

    for match in matches:
        match_start = max(int(match["start"]), segment_start)
        match_end = min(int(match["end"]), segment_end)

        if match_end <= cursor or match_start >= segment_end:
            continue

        match_start = max(match_start, cursor)

        if match_start > cursor:
            html_parts.append(html.escape(text[cursor:match_start]))

        html_parts.append("<mark>")
        html_parts.append(html.escape(text[match_start:match_end]))
        html_parts.append("</mark>")
        cursor = match_end

    if cursor < segment_end:
        html_parts.append(html.escape(text[cursor:segment_end]))

    rendered = "".join(html_parts).strip()
    if segment_start > 0:
        rendered = f"... {rendered}"
    if segment_end < len(text):
        rendered = f"{rendered} ..."
    return rendered


def build_fragment_html(text: str, matches: list[dict[str, object]]) -> str:
    """Render a compact HTML fragment for one page."""
    excerpt_ranges = merge_excerpt_ranges(matches, len(text))
    if not excerpt_ranges:
        return html.escape(text[:240].strip())

    segments: list[str] = []
    for segment_start, segment_end in excerpt_ranges:
        segments.append(render_highlighted_segment(text, segment_start, segment_end, matches))

    return " ".join(segment for segment in segments if segment).strip()


def build_page_result(
    page_number: int,
    text: str,
    matches: list[dict[str, object]],
) -> dict[str, object]:
    """Return one consolidated result per page."""
    detected_keywords = get_detected_keywords(matches)
    keyword_label = ", ".join(detected_keywords)

    return {
        "keywords": detected_keywords,
        "keyword_label": keyword_label,
        "page_number": page_number,
        "fragment_html": build_fragment_html(text, matches),
    }


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
                    normalized_text = normalize_page_text(text)
                    matches = collect_page_matches(normalized_text, compiled_keywords)
                    if matches:
                        page_results.append(build_page_result(page_index, normalized_text, matches))

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
