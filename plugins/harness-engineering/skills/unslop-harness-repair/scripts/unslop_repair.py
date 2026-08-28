#!/usr/bin/env python3
"""Audit, freeze, and verify a bounded Unslop harness repair."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from typing import Any, Iterable


SCHEMA_VERSION = 1
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
ENGINE_MANIFEST = SKILL_ROOT / "references/unslop-engine-manifest.json"
TEXT_SUFFIXES = {".json", ".jsonl", ".md", ".py", ".sh", ".toml", ".txt", ".yaml", ".yml"}
EXCLUDED_DIRS = {".git", ".pytest_cache", ".venv", "__pycache__", "node_modules"}
HARD_GATES = {
    "authored_em_dash_free",
    "fabrication_free",
    "p0_clear",
    "protected_material_intact",
    "scope_intact",
    "terminal_findings",
    "unslop_engine_complete",
}
RESIDUAL_CLASSES = {"legitimate-technical", "protected-source"}
PLACEHOLDER_MARKERS = ("[" + "TODO:", "__" + "REPLACE_ME__")
FULLY_PROTECTED_SUFFIXES = {".json", ".jsonl", ".py", ".sh", ".toml", ".yaml", ".yml"}
QUALITY_CATEGORIES = {
    "meaning_factual_fidelity": 2.0,
    "protected_material": 2.0,
    "scope_authority": 1.5,
    "finding_reconciliation": 1.5,
    "language_quality": 2.0,
    "verification_evidence": 1.0,
}
WORKER_RETURN_KEYS = {
    "run_id",
    "unslop_engine_sha256",
    "worker_id",
    "owned_paths",
    "status",
    "changed_paths",
    "finding_dispositions",
    "residuals",
    "tests",
    "unresolved_count",
    "recursive_launches",
    "risks",
}


class RepairError(RuntimeError):
    """Raised when a repair contract fails closed."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RepairError(f"cannot read JSON {path}: {exc}") from exc


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as handle:
        temp_path = Path(handle.name)
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp_path, path)


def absolute_without_symlink(value: str | Path, must_exist: bool = True) -> Path:
    raw = Path(value).expanduser()
    requested = raw if raw.is_absolute() else Path.cwd() / raw
    requested = requested.absolute()
    if requested.is_symlink():
        raise RepairError(f"symbolic links are not allowed: {requested}")
    if must_exist and not requested.exists():
        raise RepairError(f"path does not exist: {requested}")
    return requested.resolve(strict=must_exist)


def is_within(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def engine_status() -> dict[str, Any]:
    manifest = load_json(ENGINE_MANIFEST)
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        raise RepairError("invalid bundled Unslop engine manifest")
    if manifest.get("runtime_dependency_on_writing_quality") is not False:
        raise RepairError("bundled Unslop engine declares an external Writing Quality dependency")
    files = manifest.get("files")
    if not isinstance(files, dict) or not files:
        raise RepairError("bundled Unslop engine manifest has no files")
    actual: dict[str, str] = {}
    for relative, expected_sha256 in sorted(files.items()):
        if not isinstance(relative, str) or not isinstance(expected_sha256, str):
            raise RepairError("bundled Unslop engine manifest has an invalid entry")
        candidate = (SKILL_ROOT / relative).absolute()
        if candidate.is_symlink() or not candidate.is_file():
            raise RepairError(f"bundled Unslop engine file is missing or symbolic: {relative}")
        resolved = candidate.resolve(strict=True)
        if not is_within(resolved, SKILL_ROOT):
            raise RepairError(f"bundled Unslop engine file escapes the skill root: {relative}")
        digest = sha256_bytes(resolved.read_bytes())
        if digest != expected_sha256:
            raise RepairError(f"bundled Unslop engine hash mismatch: {relative}")
        actual[relative] = digest
    payload = "".join(f"{relative}\0{digest}\n" for relative, digest in sorted(actual.items())).encode("utf-8")
    return {
        "status": "complete",
        "file_count": len(actual),
        "inventory_sha256": sha256_bytes(payload),
        "runtime_dependency_on_writing_quality": False,
    }


def load_engine_module(filename: str, module_name: str) -> Any:
    status = engine_status()
    if status["status"] != "complete":
        raise RepairError("bundled Unslop engine is incomplete")
    path = SCRIPT_DIR / "unslop-engine" / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RepairError(f"cannot load bundled Unslop engine module: {filename}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def inline_code_spans(text: str) -> list[tuple[int, int, str]]:
    spans: list[tuple[int, int, str]] = []
    offset = 0
    for line in text.splitlines(keepends=True):
        cursor = 0
        while cursor < len(line):
            start = line.find("`", cursor)
            if start < 0:
                break
            run = 1
            while start + run < len(line) and line[start + run] == "`":
                run += 1
            if run >= 3 and not line[:start].strip():
                cursor = start + run
                continue
            delimiter = "`" * run
            search = start + run
            close = -1
            while search < len(line):
                candidate = line.find(delimiter, search)
                if candidate < 0:
                    break
                after = candidate + run
                if (candidate == 0 or line[candidate - 1] != "`") and (after >= len(line) or line[after] != "`"):
                    close = candidate
                    break
                search = candidate + 1
            if close < 0:
                cursor = start + run
                continue
            end = close + run
            spans.append((offset + start, offset + end, line[start:end]))
            cursor = end
        offset += len(line)
    return spans


def quoted_spans(text: str) -> list[tuple[int, int, str]]:
    spans: list[tuple[int, int, str]] = []
    for opening, closing in (("\"", "\""), ("“", "”"), ("‘", "’")):
        cursor = 0
        while cursor < len(text):
            start = text.find(opening, cursor)
            if start < 0:
                break
            end_marker = text.find(closing, start + len(opening))
            if end_marker < 0:
                break
            end = end_marker + len(closing)
            spans.append((start, end, text[start:end]))
            cursor = end
    return sorted(spans)


def unclosed_fence_count(text: str) -> int:
    fence: tuple[str, int] | None = None
    for line in text.splitlines():
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})(.*)$", line)
        if not match:
            continue
        marker = match.group(1)
        if fence is None:
            fence = (marker[0], len(marker))
        elif marker[0] == fence[0] and len(marker) >= fence[1] and not match.group(2).strip():
            fence = None
    return int(fence is not None)


def normalize_roots(values: Iterable[str]) -> list[Path]:
    roots: list[Path] = []
    for value in values:
        root = absolute_without_symlink(value)
        if not root.is_file() and not root.is_dir():
            raise RepairError(f"root is not a regular file or directory: {root}")
        if root not in roots:
            roots.append(root)
    if not roots:
        raise RepairError("at least one approved root is required")
    return sorted(roots, key=str)


def protected_segments(text: str, suffix: str = "") -> list[dict[str, str]]:
    segments: list[dict[str, str]] = []
    lines = text.splitlines(keepends=True)

    if suffix.lower() in FULLY_PROTECTED_SUFFIXES:
        segments.append({"category": "structured-or-code-file", "value": text})

    if lines and lines[0].rstrip("\r\n") == "---":
        for index in range(1, len(lines)):
            if lines[index].rstrip("\r\n") == "---":
                segments.append({"category": "frontmatter", "value": "".join(lines[: index + 1])})
                break

    fence_start: tuple[str, int, int] | None = None
    for index, line in enumerate(lines):
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})(.*)$", line.rstrip("\r\n"))
        if not match:
            continue
        marker = match.group(1)
        if fence_start is None:
            fence_start = (marker[0], len(marker), index)
        elif marker[0] == fence_start[0] and len(marker) >= fence_start[1] and not match.group(2).strip():
            segments.append({"category": "fenced-code", "value": "".join(lines[fence_start[2] : index + 1])})
            fence_start = None
    if fence_start is not None:
        segments.append({"category": "fenced-code", "value": "".join(lines[fence_start[2] :])})

    table_lines: set[int] = set()
    separator = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$")
    for index, line in enumerate(lines):
        if not separator.fullmatch(line.rstrip("\r\n")):
            continue
        if index > 0 and "|" in lines[index - 1]:
            table_lines.add(index - 1)
        table_lines.add(index)
        cursor = index + 1
        while cursor < len(lines) and "|" in lines[cursor] and lines[cursor].strip():
            table_lines.add(cursor)
            cursor += 1

    quote_lines: set[int] = set()
    for index, line in enumerate(lines):
        if not line.lstrip().startswith(">"):
            continue
        quote_lines.add(index)
        cursor = index + 1
        while cursor < len(lines) and lines[cursor].strip():
            quote_lines.add(cursor)
            cursor += 1
    for index in sorted(quote_lines):
        segments.append({"category": "block-quote", "value": lines[index]})
    for line in lines:
        if (line.startswith("    ") or line.startswith("\t")) and line.strip():
            segments.append({"category": "indented-code", "value": line})
    for index in sorted(table_lines):
        segments.append({"category": "table", "value": lines[index]})

    for _, _, value in inline_code_spans(text):
        segments.append({"category": "inline-code", "value": value})
    for _, _, value in quoted_spans(text):
        category = "multiline-quoted-text" if "\n" in value else "quoted-text"
        segments.append({"category": category, "value": value})

    patterns = [
        ("markdown-link", r"!?\[[^\]\n]*\]\([^\)\n]+\)"),
        ("url", r"https?://[^\s<>\)\]]+"),
        ("absolute-path", r"(?<![\w.])(?:~|/)(?:[A-Za-z0-9._+-]+/)+[A-Za-z0-9._+-]+"),
        ("uuid", r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"),
        ("digest", r"\b[0-9a-fA-F]{40,64}\b"),
        ("skill-token", r"\$[a-z0-9][a-z0-9-]*"),
        ("namespaced-id", r"\b[a-z0-9][a-z0-9-]*:[a-z0-9][a-z0-9-]*\b"),
    ]
    for category, pattern in patterns:
        for match in re.finditer(pattern, text):
            segments.append({"category": category, "value": match.group(0)})

    return segments


def strong_content_fingerprints(text: str) -> dict[str, int]:
    """Freeze every occurrence of text that appears inside Markdown strong marks."""
    strong_keys: set[str] = set()
    lengths: set[int] = set()
    patterns = (
        r"(?<!\*)\*\*((?:(?!\*\*).)+?)\*\*(?!\*)",
        r"(?<!_)__((?:(?!__).)+?)__(?!_)",
    )
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.DOTALL):
            content = match.group(1)
            key = f"{len(content)}:{sha256_bytes(content.encode('utf-8'))}"
            strong_keys.add(key)
            lengths.add(len(content))
    all_occurrences = candidate_substring_fingerprints(text, lengths)
    return {key: all_occurrences[key] for key in sorted(strong_keys)}


def candidate_substring_fingerprints(text: str, lengths: set[int]) -> Counter[str]:
    """Count candidate substrings at the frozen emphasized-content lengths."""
    counts: Counter[str] = Counter()
    for length in sorted(lengths):
        if length <= 0 or length > len(text):
            continue
        for start in range(0, len(text) - length + 1):
            content = text[start : start + length]
            key = f"{length}:{sha256_bytes(content.encode('utf-8'))}"
            counts[key] += 1
    return counts


def ensure_strong_content_survives(frozen: dict[str, Any], current_path: Path) -> None:
    """Allow unbolding but reject edits to words that were emphasized at freeze time."""
    fingerprints = frozen.get("strong_content_fingerprints")
    if not isinstance(fingerprints, dict):
        raise RepairError(f"frozen strong-content evidence is invalid: {current_path}")
    required: Counter[str] = Counter()
    lengths: set[int] = set()
    for key, count in fingerprints.items():
        if not isinstance(key, str) or not isinstance(count, int) or isinstance(count, bool) or count < 1:
            raise RepairError(f"frozen strong-content evidence is invalid: {current_path}")
        try:
            raw_length, digest = key.split(":", 1)
            length = int(raw_length)
        except (TypeError, ValueError):
            raise RepairError(f"frozen strong-content evidence is invalid: {current_path}") from None
        if length < 1 or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise RepairError(f"frozen strong-content evidence is invalid: {current_path}")
        required[key] = count
        lengths.add(length)
    if not required:
        return
    try:
        current_text = current_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise RepairError(f"cannot validate frozen strong content in {current_path}: {exc}") from exc
    available = candidate_substring_fingerprints(current_text, lengths)
    missing = required - available
    if missing:
        raise RepairError(f"protected strong-text content drift: {current_path}")


def suffix_corruptions(text: str) -> list[str]:
    patterns = [
        r"(?<!\*)\*\*[^*\n]+\*\*(?!\*)[A-Za-z0-9_]+",
        r"(?<!_)__[^_\n]+__(?!_)[A-Za-z0-9_]+",
        r"!?\[[^\]\n]*\]\([^\)\n]+\)[A-Za-z0-9_]+",
    ]
    matches: list[str] = []
    for _, end, value in inline_code_spans(text):
        if end < len(text) and re.match(r"[A-Za-z0-9_]", text[end]):
            cursor = end
            while cursor < len(text) and re.match(r"[A-Za-z0-9_]", text[cursor]):
                cursor += 1
            matches.append(text[end - len(value) : cursor])
    for _, end, value in quoted_spans(text):
        if end < len(text) and re.match(r"[A-Za-z0-9_]", text[end]):
            cursor = end
            while cursor < len(text) and re.match(r"[A-Za-z0-9_]", text[cursor]):
                cursor += 1
            matches.append(text[end - len(value) : cursor])
    for pattern in patterns:
        matches.extend(match.group(0) for match in re.finditer(pattern, text))
    return sorted(matches)


def entry_for(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RepairError(f"approved text file is not UTF-8: {path}") from exc
    protected = protected_segments(text, path.suffix)
    counts = Counter(item["category"] for item in protected)
    protected_bytes = json.dumps(protected, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return {
        "path": str(path),
        "sha256": sha256_bytes(data),
        "size": len(data),
        "em_dash_count": text.count("\u2014"),
        "placeholder_count": sum(text.count(marker) for marker in PLACEHOLDER_MARKERS),
        "suffix_corruptions": suffix_corruptions(text),
        "unclosed_fence_count": unclosed_fence_count(text),
        "protected_sha256": sha256_bytes(protected_bytes),
        "protected_counts": dict(sorted(counts.items())),
        "strong_content_fingerprints": strong_content_fingerprints(text),
    }


def inventory(roots: list[Path]) -> list[dict[str, Any]]:
    files: dict[Path, None] = {}
    for root in roots:
        if root.is_file():
            if root.suffix.lower() in TEXT_SUFFIXES:
                files[root] = None
            continue
        for path in root.rglob("*"):
            if any(part in EXCLUDED_DIRS for part in path.parts):
                continue
            if path.is_symlink():
                raise RepairError(f"symbolic links are not allowed in approved roots: {path}")
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
                files[path.absolute()] = None
    return [entry_for(path) for path in sorted(files, key=str)]


def inventory_sha256(entries: list[dict[str, Any]]) -> str:
    payload = "".join(
        f"{entry['path']}\0{entry['sha256']}\0{entry['protected_sha256']}\n"
        for entry in sorted(entries, key=lambda item: item["path"])
    ).encode("utf-8")
    return sha256_bytes(payload)


def ensure_output_outside_roots(output: Path, roots: list[Path]) -> None:
    absolute = absolute_without_symlink(output, must_exist=False)
    if any(is_within(absolute, root) for root in roots):
        raise RepairError(f"evidence output must be outside approved source roots: {absolute}")


def validate_record(record: Any, expected_mode: str) -> dict[str, Any]:
    if not isinstance(record, dict) or record.get("schema_version") != SCHEMA_VERSION:
        raise RepairError(f"invalid {expected_mode} schema")
    if record.get("mode") != expected_mode or not isinstance(record.get("run_id"), str):
        raise RepairError(f"invalid {expected_mode} record")
    if not isinstance(record.get("roots"), list) or not isinstance(record.get("entries"), list):
        raise RepairError(f"invalid {expected_mode} inventory")
    return record


def cmd_audit(args: argparse.Namespace) -> int:
    roots = normalize_roots(args.root)
    output = absolute_without_symlink(args.output, must_exist=False)
    ensure_output_outside_roots(output, roots)
    entries = inventory(roots)
    engine = engine_status()
    record = {
        "schema_version": SCHEMA_VERSION,
        "mode": "audit",
        "run_id": args.run_id,
        "roots": [str(root) for root in roots],
        "entries": entries,
        "inventory_sha256": inventory_sha256(entries),
        "unslop_engine_sha256": engine["inventory_sha256"],
        "unslop_engine_file_count": engine["file_count"],
    }
    atomic_write_json(output, record)
    print(json.dumps({"status": "audited", "files": len(entries), "inventory_sha256": record["inventory_sha256"]}))
    return 0


def cmd_freeze(args: argparse.Namespace) -> int:
    audit_path = absolute_without_symlink(args.audit)
    audit = validate_record(load_json(audit_path), "audit")
    roots = normalize_roots(audit["roots"])
    output = absolute_without_symlink(args.output, must_exist=False)
    ensure_output_outside_roots(output, roots)
    current = inventory(roots)
    current_digest = inventory_sha256(current)
    engine = engine_status()
    if current_digest != audit.get("inventory_sha256") or current != audit["entries"]:
        raise RepairError("source drifted after audit; create a new audit before freezing")
    if engine["inventory_sha256"] != audit.get("unslop_engine_sha256"):
        raise RepairError("bundled Unslop engine drifted after audit")
    record = {
        "schema_version": SCHEMA_VERSION,
        "mode": "freeze",
        "run_id": audit["run_id"],
        "roots": audit["roots"],
        "entries": current,
        "inventory_sha256": current_digest,
        "audit_sha256": sha256_bytes(audit_path.read_bytes()),
        "unslop_engine_sha256": engine["inventory_sha256"],
        "unslop_engine_file_count": engine["file_count"],
    }
    atomic_write_json(output, record)
    print(json.dumps({"status": "frozen", "files": len(current), "inventory_sha256": current_digest}))
    return 0


def cmd_engine_check(_args: argparse.Namespace) -> int:
    status = engine_status()
    print(json.dumps(status, sort_keys=True))
    return 0


def cmd_scan(args: argparse.Namespace) -> int:
    input_path = absolute_without_symlink(args.input)
    if not input_path.is_file():
        raise RepairError(f"scan input is not a regular file: {input_path}")
    output = absolute_without_symlink(args.output, must_exist=False)
    if output == input_path:
        raise RepairError("scan output cannot overwrite the input")
    try:
        text = input_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise RepairError(f"cannot read scan input {input_path}: {exc}") from exc
    engine = engine_status()
    validator = load_engine_module("quality_validator.py", "bundled_unslop_quality_validator")
    result = validator.validate_content(text).to_dict()
    record = {
        "schema_version": SCHEMA_VERSION,
        "mode": "detect",
        "input": str(input_path),
        "input_sha256": sha256_bytes(input_path.read_bytes()),
        "unslop_engine_sha256": engine["inventory_sha256"],
        "runtime_dependency_on_writing_quality": False,
        "raw_result": result,
        "verdict_boundary": "raw scanner evidence requires contextual classification",
    }
    atomic_write_json(output, record)
    print(json.dumps({
        "status": "scanned",
        "input": str(input_path),
        "technical_score": result["technical_score"],
        "unslop_engine_sha256": engine["inventory_sha256"],
    }, sort_keys=True))
    return 0


def require_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise RepairError(f"{label} must be a list of non-empty strings")
    if len(value) != len(set(value)):
        raise RepairError(f"{label} must not contain duplicates")
    return value


def normalize_approved_paths(values: list[str], roots: list[Path], label: str) -> list[Path]:
    paths: list[Path] = []
    for value in values:
        path = absolute_without_symlink(value, must_exist=False)
        if not any(is_within(path, root) for root in roots):
            raise RepairError(f"{label} is outside frozen roots: {path}")
        paths.append(path)
    return paths


def scopes_overlap(first: Path, second: Path) -> bool:
    return is_within(first, second) or is_within(second, first)


def validate_workers(
    workers: Any,
    approved_paths: list[Path],
    actual_changed_paths: set[str],
    finding_ids: set[str],
    run_id: str,
    unslop_engine_sha256: str,
) -> None:
    if not isinstance(workers, list) or len(workers) > 3:
        raise RepairError("workers must contain zero to three direct workers")
    owned: list[tuple[str, Path]] = []
    seen_ids: set[str] = set()
    for worker in workers:
        if not isinstance(worker, dict) or not isinstance(worker.get("worker_id"), str) or not worker["worker_id"]:
            raise RepairError("each worker needs a non-empty worker_id")
        worker_id = worker["worker_id"]
        if set(worker) != WORKER_RETURN_KEYS:
            extras = sorted(set(worker) - WORKER_RETURN_KEYS)
            missing = sorted(WORKER_RETURN_KEYS - set(worker))
            details = []
            if extras:
                details.append("forbidden fields: " + ", ".join(extras))
            if missing:
                details.append("missing fields: " + ", ".join(missing))
            raise RepairError(f"worker {worker_id} return packet has the wrong fields: " + "; ".join(details))
        if worker_id in seen_ids:
            raise RepairError(f"duplicate worker id: {worker_id}")
        seen_ids.add(worker_id)
        if worker.get("run_id") != run_id:
            raise RepairError(f"worker {worker_id} run_id does not match the repair run")
        if worker.get("unslop_engine_sha256") != unslop_engine_sha256:
            raise RepairError(f"worker {worker_id} bundled Unslop engine digest does not match the freeze")
        if worker.get("recursive_launches") != 0:
            raise RepairError(f"worker {worker_id} attempted recursive launches")
        if worker.get("status") != "complete":
            raise RepairError(f"worker {worker_id} is not complete")
        owned_paths = require_string_list(worker.get("owned_paths"), f"worker {worker_id} owned_paths")
        normalized_owned: list[Path] = []
        for value in owned_paths:
            path = absolute_without_symlink(value, must_exist=False)
            if not any(is_within(path, approved) for approved in approved_paths):
                raise RepairError(f"worker {worker_id} path is not approved: {path}")
            for other_id, other in owned:
                if scopes_overlap(path, other):
                    raise RepairError(f"worker paths overlap: {worker_id} and {other_id}")
            owned.append((worker_id, path))
            normalized_owned.append(path)
        changed_paths = require_string_list(worker.get("changed_paths"), f"worker {worker_id} changed_paths")
        for value in changed_paths:
            path = absolute_without_symlink(value, must_exist=False)
            if not any(is_within(path, scope) for scope in normalized_owned):
                raise RepairError(f"worker {worker_id} changed an unowned path: {path}")
            if str(path) not in actual_changed_paths:
                raise RepairError(f"worker {worker_id} reported a path not changed by the candidate: {path}")
        dispositions = worker.get("finding_dispositions")
        if not isinstance(dispositions, list):
            raise RepairError(f"worker {worker_id} finding_dispositions must be an array")
        for disposition in dispositions:
            if not isinstance(disposition, dict) or disposition.get("id") not in finding_ids:
                raise RepairError(f"worker {worker_id} returned an unknown finding disposition")
            if disposition.get("state") not in {"repaired", "protected"}:
                raise RepairError(f"worker {worker_id} returned a non-terminal finding disposition")
            if not isinstance(disposition.get("evidence"), str) or not disposition["evidence"].strip():
                raise RepairError(f"worker {worker_id} finding disposition lacks evidence")
        require_string_list(worker.get("tests"), f"worker {worker_id} tests")
        risks = worker.get("risks")
        if not isinstance(risks, list) or any(not isinstance(item, str) for item in risks):
            raise RepairError(f"worker {worker_id} risks must be an array of strings")
        validate_residuals(worker.get("residuals"))
        if worker.get("unresolved_count") != 0:
            raise RepairError(f"worker {worker_id} has unresolved findings")


def validate_findings(findings: Any) -> tuple[int, int]:
    if not isinstance(findings, list):
        raise RepairError("findings must be an array")
    repaired = 0
    protected = 0
    seen: set[str] = set()
    for finding in findings:
        if not isinstance(finding, dict) or not isinstance(finding.get("id"), str) or not finding["id"]:
            raise RepairError("each finding needs a non-empty id")
        if finding["id"] in seen:
            raise RepairError(f"duplicate finding id: {finding['id']}")
        seen.add(finding["id"])
        state = finding.get("state")
        if state == "repaired":
            if not isinstance(finding.get("evidence"), str) or not finding["evidence"].strip():
                raise RepairError(f"repaired finding lacks evidence: {finding['id']}")
            repaired += 1
        elif state == "protected":
            for field in ("category", "reason", "source_owner", "evidence"):
                if not isinstance(finding.get(field), str) or not finding[field].strip():
                    raise RepairError(f"protected finding {finding['id']} lacks {field}")
            protected += 1
        else:
            raise RepairError(f"finding is unresolved or unclassified: {finding['id']}")
    return repaired, protected


def validate_residuals(residuals: Any) -> None:
    if not isinstance(residuals, list):
        raise RepairError("residuals must be an array")
    for index, residual in enumerate(residuals):
        if not isinstance(residual, dict) or residual.get("classification") not in RESIDUAL_CLASSES:
            raise RepairError(f"residual {index} is unclassified")
        for field in ("term", "reason", "source_owner", "evidence"):
            if not isinstance(residual.get(field), str) or not residual[field].strip():
                raise RepairError(f"residual {index} lacks {field}")


def validate_quality(quality: Any) -> float:
    if not isinstance(quality, dict):
        raise RepairError("quality must be an object")
    score = quality.get("score")
    floor = quality.get("floor")
    target = quality.get("target")
    if isinstance(score, bool) or not isinstance(score, (int, float)) or not 0 <= score <= 10:
        raise RepairError("quality score must be from 0 to 10")
    if isinstance(floor, bool) or not isinstance(floor, (int, float)) or floor < 8 or floor > 10:
        raise RepairError("quality floor cannot be below 8.0")
    if target != 10.0:
        raise RepairError("quality target must be 10.0")
    if score < floor:
        raise RepairError(f"quality score {score} is below floor {floor}")
    category_scores = quality.get("category_scores")
    if not isinstance(category_scores, dict) or set(category_scores) != set(QUALITY_CATEGORIES):
        raise RepairError("quality category_scores must contain the exact rubric categories")
    calculated = 0.0
    for name, maximum in QUALITY_CATEGORIES.items():
        category = category_scores[name]
        if not isinstance(category, dict) or set(category) != {"score", "max", "evidence"}:
            raise RepairError(f"quality category {name} needs score, max, and evidence")
        if category["max"] != maximum:
            raise RepairError(f"quality category {name} has the wrong maximum")
        category_score = category["score"]
        if isinstance(category_score, bool) or not isinstance(category_score, (int, float)) or not 0 <= category_score <= maximum:
            raise RepairError(f"quality category {name} score is invalid")
        if not isinstance(category["evidence"], str) or not category["evidence"].strip():
            raise RepairError(f"quality category {name} lacks evidence")
        calculated += float(category_score)
    if abs(calculated - float(score)) > 1e-9:
        raise RepairError(f"quality category total {calculated} does not match score {score}")
    gates = quality.get("hard_gates")
    if not isinstance(gates, dict) or set(gates) != HARD_GATES:
        raise RepairError("quality hard_gates must contain the exact required gates")
    failed = sorted(name for name, clear in gates.items() if clear is not True)
    if failed:
        raise RepairError("hard gates failed: " + ", ".join(failed))
    return float(score)


def validate_waves(waves: Any, finding_count: int) -> None:
    if not isinstance(waves, list):
        raise RepairError("repair_waves must be an array")
    if finding_count and not waves:
        raise RepairError("accepted findings require at least one repair wave")
    for index, wave in enumerate(waves):
        if not isinstance(wave, dict):
            raise RepairError(f"repair wave {index} must be an object")
        before = wave.get("unresolved_before")
        after = wave.get("unresolved_after")
        if any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in (before, after)):
            raise RepairError(f"repair wave {index} counts must be non-negative integers")
        if after >= before:
            raise RepairError(f"repair wave {index} made no progress; stop and re-plan")
    if waves and waves[-1]["unresolved_after"] != 0:
        raise RepairError("final repair wave must end with zero unresolved findings")


def cmd_verify(args: argparse.Namespace) -> int:
    freeze_path = absolute_without_symlink(args.freeze)
    ledger_path = absolute_without_symlink(args.ledger)
    freeze = validate_record(load_json(freeze_path), "freeze")
    ledger = load_json(ledger_path)
    if not isinstance(ledger, dict) or ledger.get("schema_version") != SCHEMA_VERSION:
        raise RepairError("invalid repair ledger schema")
    if ledger.get("run_id") != freeze["run_id"]:
        raise RepairError("repair ledger run_id does not match freeze")
    if "approved_protected_changes" in ledger:
        raise RepairError("protected changes are not allowed inside an Unslop repair")

    roots = normalize_roots(freeze["roots"])
    output = absolute_without_symlink(args.output, must_exist=False)
    ensure_output_outside_roots(output, roots)
    current = inventory(roots)
    current_digest = inventory_sha256(current)
    engine = engine_status()
    if engine["inventory_sha256"] != freeze.get("unslop_engine_sha256"):
        raise RepairError("bundled Unslop engine drifted after freeze")
    frozen_map = {entry["path"]: entry for entry in freeze["entries"]}
    current_map = {entry["path"]: entry for entry in current}

    approval = ledger.get("approval")
    if not isinstance(approval, dict) or approval.get("status") != "approved" or not approval.get("group"):
        raise RepairError("an approved repair group is required")
    if approval.get("authority") != "user":
        raise RepairError("repair approval must come from the user")
    if not isinstance(approval.get("evidence"), str) or not approval["evidence"].strip():
        raise RepairError("repair approval needs an evidence reference")
    approved_values = require_string_list(approval.get("approved_paths"), "approval.approved_paths")
    created_values = require_string_list(approval.get("created_paths"), "approval.created_paths")
    approved_paths = normalize_approved_paths(approved_values, roots, "approved path")
    created_paths = normalize_approved_paths(created_values, roots, "created path")
    approved_set = {str(path) for path in approved_paths}
    created_set = {str(path) for path in created_paths}

    deleted = sorted(set(frozen_map) - set(current_map))
    if deleted:
        raise RepairError("repair deleted frozen paths: " + ", ".join(deleted))
    changed = sorted(
        path for path in set(frozen_map) & set(current_map)
        if frozen_map[path]["sha256"] != current_map[path]["sha256"]
    )
    created = sorted(set(current_map) - set(frozen_map))
    unapproved_changed = [path for path in changed if path not in approved_set]
    unapproved_created = [path for path in created if path not in created_set]
    if unapproved_changed:
        raise RepairError("changed paths are outside approval: " + ", ".join(unapproved_changed))
    if unapproved_created:
        raise RepairError("created paths are outside approval: " + ", ".join(unapproved_created))
    for path in changed:
        if frozen_map[path]["protected_sha256"] != current_map[path]["protected_sha256"]:
            raise RepairError(f"protected-material drift: {path}")
        ensure_strong_content_survives(frozen_map[path], Path(path))
        if current_map[path]["em_dash_count"] > frozen_map[path]["em_dash_count"]:
            raise RepairError(f"authored em dash detected: {path}")
        if current_map[path]["placeholder_count"] > frozen_map[path]["placeholder_count"]:
            raise RepairError(f"placeholder corruption detected: {path}")
        if current_map[path]["unclosed_fence_count"] > frozen_map[path]["unclosed_fence_count"]:
            raise RepairError(f"unclosed fenced block detected: {path}")
        new_suffixes = Counter(current_map[path]["suffix_corruptions"]) - Counter(frozen_map[path]["suffix_corruptions"])
        if new_suffixes:
            raise RepairError(f"protected delimiter suffix corruption detected: {path}")
    for path in created:
        if current_map[path]["em_dash_count"]:
            raise RepairError(f"authored em dash detected in created file: {path}")
        if current_map[path]["placeholder_count"]:
            raise RepairError(f"placeholder remains in created file: {path}")
        if current_map[path]["suffix_corruptions"]:
            raise RepairError(f"protected delimiter suffix corruption detected in created file: {path}")
        if current_map[path]["unclosed_fence_count"]:
            raise RepairError(f"unclosed fenced block detected in created file: {path}")

    repaired, protected = validate_findings(ledger.get("findings"))
    validate_workers(
        ledger.get("workers"),
        approved_paths + created_paths,
        set(changed) | set(created),
        {finding["id"] for finding in ledger["findings"]},
        freeze["run_id"],
        freeze["unslop_engine_sha256"],
    )
    validate_residuals(ledger.get("residuals"))
    score = validate_quality(ledger.get("quality"))
    validate_waves(ledger.get("repair_waves"), repaired + protected)

    review = ledger.get("integrated_review")
    if not isinstance(review, dict) or review.get("status") != "clear" or review.get("fresh") is not True:
        raise RepairError("fresh integrated review is not clear")
    if not isinstance(review.get("reviewer"), str) or not review["reviewer"].strip():
        raise RepairError("integrated review needs a reviewer id")
    if review.get("inventory_sha256") != current_digest:
        raise RepairError("integrated review does not cover the current candidate inventory")

    report = {
        "schema_version": SCHEMA_VERSION,
        "run_id": freeze["run_id"],
        "status": "qualified",
        "inventory_sha256": current_digest,
        "changed_paths": changed,
        "created_paths": created,
        "findings": {"repaired": repaired, "protected": protected, "unresolved": 0},
        "residual_count": len(ledger["residuals"]),
        "quality_score": score,
        "quality_target": 10.0,
        "hard_gates": "clear",
        "integrated_review": "clear",
        "unslop_engine_sha256": engine["inventory_sha256"],
        "runtime_dependency_on_writing_quality": False,
    }
    atomic_write_json(output, report)
    print(json.dumps({"status": "qualified", "quality_score": score, "inventory_sha256": current_digest}))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    engine_check = subparsers.add_parser("engine-check", help="Verify the bundled Unslop engine")
    engine_check.set_defaults(func=cmd_engine_check)

    scan = subparsers.add_parser("scan", help="Create read-only raw Unslop scan evidence")
    scan.add_argument("--input", required=True)
    scan.add_argument("--output", required=True)
    scan.set_defaults(func=cmd_scan)

    audit = subparsers.add_parser("audit", help="Create a read-only approved-root inventory")
    audit.add_argument("--run-id", required=True)
    audit.add_argument("--root", action="append", required=True)
    audit.add_argument("--output", required=True)
    audit.set_defaults(func=cmd_audit)

    freeze = subparsers.add_parser("freeze", help="Freeze an unchanged audit inventory")
    freeze.add_argument("--audit", required=True)
    freeze.add_argument("--output", required=True)
    freeze.set_defaults(func=cmd_freeze)

    verify = subparsers.add_parser("verify", help="Verify scope, ledger, quality, and integrated review")
    verify.add_argument("--freeze", required=True)
    verify.add_argument("--ledger", required=True)
    verify.add_argument("--output", required=True)
    verify.set_defaults(func=cmd_verify)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except RepairError as exc:
        print(f"unslop repair failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
