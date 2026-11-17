#!/usr/bin/env python3
"""Listar, analizar, agregar, modificar y eliminar keywords del BORA nacional.

Subcomandos:
- list: muestra las keywords con su posicion (opcionalmente filtradas).
- check: analiza un candidato sin modificar archivos.
- add: agrega una keyword validada y registra el cambio.
- replace: reemplaza una keyword existente por otra y registra el cambio.
- remove: elimina una keyword existente y registra el cambio.
"""

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


# ---------------------------------------------------------------------------
# Lectura, escritura y validaciones basicas
# ---------------------------------------------------------------------------


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


def read_keywords_file(path: Path) -> list[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise KeywordManagerError(f"{path} no es JSON valido: {exc}") from exc

    keywords = data.get("keywords") if isinstance(data, dict) else None
    if not isinstance(keywords, list) or not all(isinstance(item, str) for item in keywords):
        raise KeywordManagerError(f"{path} debe contener un objeto con una lista 'keywords'.")
    return keywords


def write_keywords_file(path: Path, keywords: list[str]) -> None:
    path.write_text(
        json.dumps({"keywords": keywords}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def load_keywords(repo: Path) -> list[str]:
    return read_keywords_file(repo / KEYWORDS_PATH)


def save_keywords(repo: Path, keywords: list[str]) -> None:
    write_keywords_file(repo / KEYWORDS_PATH, keywords)


def compile_pattern(value: str) -> re.Pattern[str]:
    try:
        return re.compile(value, re.IGNORECASE)
    except re.error as exc:
        raise KeywordManagerError(f"El valor no es un regex valido: {exc}") from exc


def find_exact_index(keywords: list[str], value: str) -> int:
    """Return the position of an existing keyword (exact text, ignoring outer spaces)."""
    target = value.strip()
    positions = [index for index, item in enumerate(keywords) if item.strip() == target]
    if not positions:
        raise KeywordManagerError(
            f"No existe la keyword exacta {target!r}. Usa el subcomando 'list' para ubicarla."
        )
    if len(positions) > 1:
        raise KeywordManagerError(
            f"La keyword {target!r} aparece {len(positions)} veces; revisar el JSON manualmente."
        )
    return positions[0]


# ---------------------------------------------------------------------------
# Analisis de candidatos y ejemplos
# ---------------------------------------------------------------------------


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


def keywords_matching(text: str, keywords: list[str]) -> list[str]:
    """Return the keywords that would still detect a text (same rule as the app)."""
    matches: list[str] = []
    for keyword in keywords:
        try:
            if re.search(keyword, text, re.IGNORECASE):
                matches.append(keyword)
        except re.error:
            continue
    return matches


# ---------------------------------------------------------------------------
# Log
# ---------------------------------------------------------------------------


def single_line(value: str) -> str:
    return " ".join(value.replace("`", "'").split())


def append_log_entry(
    repo: Path,
    change_line: str,
    reason: str,
    evidence: str,
    validation_line: str,
    entry_date: str,
) -> None:
    log_file = repo / LOG_PATH
    current = log_file.read_text(encoding="utf-8").rstrip()
    entry = (
        f"\n\n## {entry_date} - Ajuste de keywords BORA nacional\n\n"
        "- Tipo: configuracion de busqueda.\n"
        f"- Cambio: {change_line}\n"
        f"- Motivo: {single_line(reason)}\n"
        f"- Evidencia: {single_line(evidence)}\n"
        f"- Validacion: {validation_line}\n"
        "- ADR: no corresponde; se aplica ADR-0005.\n"
    )
    log_file.write_text(current + entry, encoding="utf-8")


# ---------------------------------------------------------------------------
# Subcomandos
# ---------------------------------------------------------------------------


def list_keywords(args: argparse.Namespace) -> None:
    repo = Path(args.repo).resolve()
    validate_repo(repo)
    keywords = load_keywords(repo)
    filter_text = normalize_term(args.contains) if args.contains else ""

    shown = 0
    for position, keyword in enumerate(keywords, start=1):
        if filter_text and filter_text not in normalize_term(keyword):
            continue
        print(f"{position:3d}. {keyword}")
        shown += 1
    print(f"\n{shown} de {len(keywords)} keyword(s).")


def check_keyword(args: argparse.Namespace) -> None:
    repo = Path(args.repo).resolve()
    validate_repo(repo)
    analysis = analyze_candidate(args.candidate, load_keywords(repo))
    print(json.dumps(analysis, ensure_ascii=False, indent=2))


def add_keyword(args: argparse.Namespace) -> None:
    repo = Path(args.repo).resolve()
    validate_repo(repo)
    keywords = load_keywords(repo)
    new_value = args.value.strip()
    analysis = analyze_candidate(new_value, keywords)

    if analysis["status"] != "available":
        raise KeywordManagerError(
            "No se agrego la keyword porque ya existe o esta cubierta. "
            + json.dumps(analysis, ensure_ascii=False)
        )

    validate_examples(compile_pattern(new_value), args.positive, args.negative)

    keywords.append(new_value)
    save_keywords(repo, keywords)
    append_log_entry(
        repo,
        change_line=f"se agrego `{single_line(new_value)}` a `desktop_app/keywords.json`.",
        reason=args.reason,
        evidence=args.evidence,
        validation_line=(
            f"{len(args.positive)} caso(s) positivo(s) y {len(args.negative)} "
            "caso(s) negativo(s) superados; regex compilado."
        ),
        entry_date=args.entry_date,
    )
    print(f"Keyword agregada y registrada: {new_value}")


def replace_keyword(args: argparse.Namespace) -> None:
    repo = Path(args.repo).resolve()
    validate_repo(repo)
    keywords = load_keywords(repo)
    old_value = args.current.strip()
    new_value = args.value.strip()
    position = find_exact_index(keywords, old_value)

    if new_value == old_value:
        raise KeywordManagerError("El valor nuevo es identico al actual.")

    # El valor nuevo se compara contra el resto de la lista, sin el valor que reemplaza.
    other_keywords = keywords[:position] + keywords[position + 1 :]
    analysis = analyze_candidate(new_value, other_keywords)
    if analysis["status"] != "available":
        raise KeywordManagerError(
            "No se reemplazo la keyword porque el valor nuevo ya existe o esta cubierto. "
            + json.dumps(analysis, ensure_ascii=False)
        )

    validate_examples(compile_pattern(new_value), args.positive, args.negative)

    keywords[position] = new_value
    save_keywords(repo, keywords)
    append_log_entry(
        repo,
        change_line=(
            f"se reemplazo `{single_line(old_value)}` por `{single_line(new_value)}` "
            f"en `desktop_app/keywords.json` (posicion {position + 1})."
        ),
        reason=args.reason,
        evidence=args.evidence,
        validation_line=(
            f"{len(args.positive)} caso(s) positivo(s) y {len(args.negative)} "
            "caso(s) negativo(s) superados con el valor nuevo; regex compilado."
        ),
        entry_date=args.entry_date,
    )
    print(f"Keyword reemplazada y registrada: {old_value} -> {new_value}")


def remove_keyword(args: argparse.Namespace) -> None:
    repo = Path(args.repo).resolve()
    validate_repo(repo)
    keywords = load_keywords(repo)
    old_value = args.value.strip()
    position = find_exact_index(keywords, old_value)
    remaining = keywords[:position] + keywords[position + 1 :]

    if not args.negative and not args.positive:
        raise KeywordManagerError(
            "Indicar al menos un ejemplo: --negative (debe dejar de detectarse) "
            "o --positive (debe seguir detectandose por otras keywords)."
        )

    # Ejemplos que deben dejar de detectarse: ninguna otra keyword debe captarlos.
    still_detected = {
        example: keywords_matching(example, remaining) for example in args.negative
    }
    still_detected = {example: hits for example, hits in still_detected.items() if hits}
    if still_detected:
        raise KeywordManagerError(
            "Tras la baja, estos ejemplos seguirian detectandose por otras keywords: "
            + json.dumps(still_detected, ensure_ascii=False)
        )

    # Ejemplos que deben seguir detectandose por otras keywords (cobertura que se conserva).
    lost_coverage = [example for example in args.positive if not keywords_matching(example, remaining)]
    if lost_coverage:
        raise KeywordManagerError(
            f"Tras la baja, estos ejemplos dejarian de detectarse: {lost_coverage}"
        )

    save_keywords(repo, remaining)
    append_log_entry(
        repo,
        change_line=(
            f"se elimino `{single_line(old_value)}` de `desktop_app/keywords.json` "
            f"(posicion {position + 1})."
        ),
        reason=args.reason,
        evidence=args.evidence,
        validation_line=(
            f"{len(args.negative)} caso(s) que dejan de detectarse y "
            f"{len(args.positive)} caso(s) que siguen detectandose por otras keywords, "
            "verificados contra la lista resultante."
        ),
        entry_date=args.entry_date,
    )
    print(f"Keyword eliminada y registrada: {old_value}")


# ---------------------------------------------------------------------------
# Linea de comandos
# ---------------------------------------------------------------------------


def add_change_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repo", required=True, help="Raiz del repositorio BORA nacional.")
    parser.add_argument("--reason", required=True, help="Motivo bibliotecario del cambio.")
    parser.add_argument("--evidence", required=True, help="Ejemplo o fuente que justifica el cambio.")
    parser.add_argument("--date", dest="entry_date", default=date.today().isoformat())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="Mostrar las keywords con su posicion.")
    list_parser.add_argument("--repo", required=True, help="Raiz del repositorio BORA nacional.")
    list_parser.add_argument("--contains", help="Filtrar por texto (sin distinguir mayusculas ni tildes).")
    list_parser.set_defaults(handler=list_keywords)

    check_parser = subparsers.add_parser("check", help="Analizar un candidato sin modificar archivos.")
    check_parser.add_argument("--repo", required=True, help="Raiz del repositorio BORA nacional.")
    check_parser.add_argument("--candidate", required=True, help="Termino o regex propuesto.")
    check_parser.set_defaults(handler=check_keyword)

    add_parser = subparsers.add_parser("add", help="Agregar una keyword validada y registrar el cambio.")
    add_change_arguments(add_parser)
    add_parser.add_argument("--value", required=True, help="Valor exacto aprobado para keywords.json.")
    add_parser.add_argument("--positive", action="append", required=True, help="Caso que debe coincidir.")
    add_parser.add_argument("--negative", action="append", required=True, help="Caso que no debe coincidir.")
    add_parser.set_defaults(handler=add_keyword)

    replace_parser = subparsers.add_parser("replace", help="Reemplazar una keyword existente.")
    add_change_arguments(replace_parser)
    replace_parser.add_argument("--current", required=True, help="Valor actual exacto en keywords.json.")
    replace_parser.add_argument("--value", required=True, help="Valor nuevo aprobado.")
    replace_parser.add_argument("--positive", action="append", required=True, help="Caso que el valor nuevo debe detectar.")
    replace_parser.add_argument("--negative", action="append", required=True, help="Caso que el valor nuevo no debe detectar.")
    replace_parser.set_defaults(handler=replace_keyword)

    remove_parser = subparsers.add_parser("remove", help="Eliminar una keyword existente.")
    add_change_arguments(remove_parser)
    remove_parser.add_argument("--value", required=True, help="Valor actual exacto en keywords.json.")
    remove_parser.add_argument(
        "--negative", action="append", default=[],
        help="Caso que debe dejar de detectarse tras la baja.",
    )
    remove_parser.add_argument(
        "--positive", action="append", default=[],
        help="Caso que debe seguir detectandose por otras keywords (opcional).",
    )
    remove_parser.set_defaults(handler=remove_keyword)
    return parser


def main() -> int:
    # Evita errores de codificacion al imprimir tildes en consolas de Windows.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
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
