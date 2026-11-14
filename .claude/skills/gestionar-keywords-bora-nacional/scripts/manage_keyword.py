#!/usr/bin/env python3
"""Validate and add keywords to the national BORA desktop application."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path


KEYWORDS_PATH = Path("desktop_app/keywords.json")
LOG_PATH = Path("docs/seguimiento/log_cambios.md")
REQUIRED_PATHS = (
    KEYWORDS_PATH,
    Path("desktop_app/search_core.py"),
    LOG_PATH,
    Path("docs/adr/0005-gestion-controlada-de-keywords.md"),
)
REGEX_META_PATTERN = re.compile(r"[\\.^$*+?{}\[\]|()]")


class KeywordManagerError(Exception):
    """Expected validation or project-layout error."""


def normalize_term(value: str) -> str:
    """Normalize spacing, case and accents for duplicate detection."""
    collapsed = " ".join(value.split()).casefold()
    decomposed = unicodedata.normalize("NFKD", collapsed)
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def validate_repo(repo: Path) -> None:
    missing = [str(path) for path in REQUIRED_PATHS if not (repo / path).exists()]
    if missing:
        raise KeywordManagerError(
            "El repositorio no tiene la estructura BORA nacional esperada. "
            f"Faltan: {', '.join(missing)}"
        )

    if (repo / "config/config_keywords.json").exists():
        raise KeywordManagerError(
            "Se detecto la estructura del proyecto CABA. Usa ajustar-keywords-bo-caba."
        )


def load_keywords(repo: Path) -> list[str]:
    try:
        data = json.loads((repo / KEYWORDS_PATH).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise KeywordManagerError(f"keywords.json no es JSON valido: {exc}") from exc

    keywords = data.get("keywords") if isinstance(data, dict) else None
    if not isinstance(keywords, list) or not all(isinstance(item, str) for item in keywords):
        raise KeywordManagerError("keywords.json debe contener un objeto con una lista 'keywords'.")
    return keywords


def compile_pattern(value: str) -> re.Pattern[str]:
    try:
        return re.compile(value, re.IGNORECASE)
    except re.error as exc:
        raise KeywordManagerError(f"El valor no es un regex valido: {exc}") from exc


def analyze_candidate(candidate: str, keywords: list[str]) -> dict[str, object]:
    candidate = candidate.strip()
    if not candidate:
        raise KeywordManagerError("El candidato no puede estar vacio.")

    compile_pattern(candidate)
    candidate_casefold = candidate.casefold()
    candidate_normalized = normalize_term(candidate)

    exact_matches: list[str] = []
    normalized_matches: list[str] = []
    covered_by_patterns: list[str] = []
    overlapping_patterns: list[str] = []

    for existing in keywords:
        if existing.strip().casefold() == candidate_casefold:
            exact_matches.append(existing)
            continue
        if normalize_term(existing) == candidate_normalized:
            normalized_matches.append(existing)
            continue

        try:
            existing_pattern = re.compile(existing, re.IGNORECASE)
        except re.error:
            continue

        if existing_pattern.fullmatch(candidate):
            covered_by_patterns.append(existing)
        elif existing_pattern.search(candidate):
            overlapping_patterns.append(existing)

    if exact_matches or normalized_matches:
        status = "duplicate"
    elif covered_by_patterns:
        status = "covered"
    else:
        status = "available"

    return {
        "candidate": candidate,
        "status": status,
        "looks_like_regex": bool(REGEX_META_PATTERN.search(candidate)),
        "exact_matches": exact_matches,
        "normalized_matches": normalized_matches,
        "covered_by_patterns": covered_by_patterns,
        "overlapping_patterns": overlapping_patterns,
    }


def validate_examples(pattern: re.Pattern[str], positives: list[str], negatives: list[str]) -> None:
    failed_positives = [example for example in positives if not pattern.search(example)]
    failed_negatives = [example for example in negatives if pattern.search(example)]

    if failed_positives or failed_negatives:
        details: list[str] = []
        if failed_positives:
            details.append(f"positivos sin match: {failed_positives}")
        if failed_negatives:
            details.append(f"negativos con match: {failed_negatives}")
        raise KeywordManagerError("Fallo la validacion de ejemplos; " + "; ".join(details))


def single_line(value: str) -> str:
    return " ".join(value.replace("`", "'").split())


def append_log_entry(
    repo: Path,
    value: str,
    reason: str,
    evidence: str,
    positives: list[str],
    negatives: list[str],
    entry_date: str,
) -> None:
    log_file = repo / LOG_PATH
    current = log_file.read_text(encoding="utf-8").rstrip()
    entry = (
        f"\n\n## {entry_date} - Ajuste de keywords BORA nacional\n\n"
        "- Tipo: configuracion de busqueda.\n"
        f"- Cambio: se agrego `{single_line(value)}` a `desktop_app/keywords.json`.\n"
        f"- Motivo: {single_line(reason)}\n"
        f"- Evidencia: {single_line(evidence)}\n"
        f"- Validacion: {len(positives)} caso(s) positivo(s) y "
        f"{len(negatives)} caso(s) negativo(s) superados; regex compilado.\n"
        "- ADR: no corresponde; se aplica ADR-0005.\n"
    )
    log_file.write_text(current + entry, encoding="utf-8")


def add_keyword(args: argparse.Namespace) -> None:
    repo = Path(args.repo).resolve()
    validate_repo(repo)
    keywords = load_keywords(repo)
    analysis = analyze_candidate(args.value, keywords)

    if analysis["status"] != "available":
        raise KeywordManagerError(
            "No se agrego la keyword porque ya existe o esta cubierta. "
            + json.dumps(analysis, ensure_ascii=False)
        )

    pattern = compile_pattern(args.value.strip())
    validate_examples(pattern, args.positive, args.negative)

    keywords.append(args.value.strip())
    (repo / KEYWORDS_PATH).write_text(
        json.dumps({"keywords": keywords}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    append_log_entry(
        repo,
        args.value.strip(),
        args.reason,
        args.evidence,
        args.positive,
        args.negative,
        args.entry_date,
    )
    print(f"Keyword agregada y registrada: {args.value.strip()}")


def check_keyword(args: argparse.Namespace) -> None:
    repo = Path(args.repo).resolve()
    validate_repo(repo)
    analysis = analyze_candidate(args.candidate, load_keywords(repo))
    print(json.dumps(analysis, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check", help="Analizar un candidato sin modificar archivos.")
    check_parser.add_argument("--repo", required=True, help="Raiz del repositorio BORA nacional.")
    check_parser.add_argument("--candidate", required=True, help="Termino o regex propuesto.")
    check_parser.set_defaults(handler=check_keyword)

    add_parser = subparsers.add_parser("add", help="Agregar una keyword validada y registrar el cambio.")
    add_parser.add_argument("--repo", required=True, help="Raiz del repositorio BORA nacional.")
    add_parser.add_argument("--value", required=True, help="Valor exacto aprobado para keywords.json.")
    add_parser.add_argument("--reason", required=True, help="Motivo bibliotecario del cambio.")
    add_parser.add_argument("--evidence", required=True, help="Ejemplo o fuente que justifica el cambio.")
    add_parser.add_argument("--positive", action="append", required=True, help="Caso que debe coincidir.")
    add_parser.add_argument("--negative", action="append", required=True, help="Caso que no debe coincidir.")
    add_parser.add_argument("--date", dest="entry_date", default=date.today().isoformat())
    add_parser.set_defaults(handler=add_keyword)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.handler(args)
    except KeywordManagerError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
