#!/usr/bin/env python3
"""Build and verify deterministic Cowork-compatible .plugin archives."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import sys
import zipfile


ARCHIVE_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
EXCLUDED_PARTS = {".git", ".pytest_cache", "__pycache__", "dist"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}
MANIFEST = ".claude-plugin/plugin.json"
MAX_BYTES = 50_000_000


def fail(message: str) -> None:
    raise RuntimeError(message)


def source_files(source: Path) -> list[tuple[Path, Path]]:
    if not source.is_dir():
        fail(f"plugin source is not a directory: {source}")
    files: list[tuple[Path, Path]] = []
    for path in sorted(source.rglob("*")):
        relative = path.relative_to(source)
        if any(part in EXCLUDED_PARTS for part in relative.parts) or relative.suffix.lower() in EXCLUDED_SUFFIXES:
            continue
        if path.is_symlink():
            fail(f"plugin source contains a symbolic link: {relative}")
        if path.is_file():
            files.append((path, relative))
    if not (source / MANIFEST).is_file():
        fail(f"plugin source is missing {MANIFEST}")
    return files


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_archive(archive: Path, source: Path | None = None) -> dict[str, object]:
    archive = archive.resolve()
    if not archive.is_file() or not zipfile.is_zipfile(archive):
        fail(f"not a valid ZIP archive: {archive}")
    if archive.stat().st_size >= MAX_BYTES:
        fail(f"archive exceeds {MAX_BYTES} bytes")
    with zipfile.ZipFile(archive) as bundle:
        infos = [info for info in bundle.infolist() if not info.is_dir()]
        names = [info.filename for info in infos]
        if len(names) != len(set(names)):
            fail("archive contains duplicate paths")
        for info in infos:
            path = PurePosixPath(info.filename)
            if info.filename.startswith("/") or ".." in path.parts or "\\" in info.filename:
                fail(f"unsafe archive path: {info.filename}")
            if stat.S_ISLNK(info.external_attr >> 16):
                fail(f"archive contains a symbolic link: {info.filename}")
        if MANIFEST not in names:
            fail(f"archive is missing {MANIFEST} at its root")
        manifest = json.loads(bundle.read(MANIFEST).decode("utf-8"))
        if source is not None:
            expected_files = source_files(source.resolve())
            expected = {relative.as_posix() for _, relative in expected_files}
            if set(names) != expected:
                fail(f"archive inventory mismatch missing={sorted(expected - set(names))} extra={sorted(set(names) - expected)}")
            for path, relative in expected_files:
                if hashlib.sha256(bundle.read(relative.as_posix())).hexdigest() != digest_file(path):
                    fail(f"archive content mismatch: {relative}")
    return {
        "archive": str(archive),
        "plugin": manifest["name"],
        "version": manifest["version"],
        "files": len(names),
        "bytes": archive.stat().st_size,
        "sha256": digest_file(archive),
    }


def build(source: Path, output: Path, force: bool) -> dict[str, object]:
    source = source.resolve()
    output = output.resolve()
    files = source_files(source)
    if output.exists() and not force:
        fail(f"output exists; pass --force to replace it: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.{os.getpid()}.tmp")
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
            for path, relative in files:
                info = zipfile.ZipInfo(relative.as_posix(), date_time=ARCHIVE_TIMESTAMP)
                info.create_system = 3
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = (stat.S_IFREG | (stat.S_IMODE(path.stat().st_mode) or 0o644)) << 16
                with path.open("rb") as source_handle, bundle.open(info, "w") as destination:
                    shutil.copyfileobj(source_handle, destination)
        inspect_archive(temporary, source)
        if output.exists():
            output.unlink()
        temporary.replace(output)
        return inspect_archive(output, source)
    finally:
        if temporary.exists():
            temporary.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build_command = commands.add_parser("build")
    build_command.add_argument("--source", required=True, type=Path)
    build_command.add_argument("--output", required=True, type=Path)
    build_command.add_argument("--force", action="store_true")
    verify_command = commands.add_parser("verify")
    verify_command.add_argument("archive", type=Path)
    verify_command.add_argument("--source", type=Path)
    args = parser.parse_args()
    result = build(args.source, args.output, args.force) if args.command == "build" else inspect_archive(args.archive, args.source)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"plugin archive validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
