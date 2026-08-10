#!/usr/bin/env python3
"""Build or verify a portable Claude plugin ZIP archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import sys
from typing import BinaryIO, Optional
import zipfile


ARCHIVE_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
EXCLUDED_PARTS = {".git", ".pytest_cache", "__pycache__", "dist"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}
MAX_ARCHIVE_BYTES = 50_000_000
MANIFEST_PATH = ".claude-plugin/plugin.json"


def fail(message: str) -> None:
    raise RuntimeError(message)


def is_excluded(relative: Path) -> bool:
    return any(part in EXCLUDED_PARTS for part in relative.parts) or relative.suffix.lower() in EXCLUDED_SUFFIXES


def source_files(source: Path) -> list[tuple[Path, Path]]:
    if not source.is_dir():
        fail(f"plugin source is not a directory: {source}")
    files: list[tuple[Path, Path]] = []
    for path in sorted(source.rglob("*")):
        relative = path.relative_to(source)
        if is_excluded(relative):
            continue
        if path.is_symlink():
            fail(f"plugin source contains a symbolic link: {relative}")
        if path.is_file():
            files.append((path, relative))
    return files


def manifest_from_source(source: Path) -> dict[str, object]:
    manifest = source / MANIFEST_PATH
    if not manifest.is_file():
        fail(f"plugin source is missing {MANIFEST_PATH}")
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"plugin manifest is not valid JSON: {exc}")
    if not isinstance(data, dict):
        fail("plugin manifest must be a JSON object")
    for field in ("name", "version"):
        if not isinstance(data.get(field), str) or not data[field]:
            fail(f"plugin manifest has no non-empty {field}")
    return data


def content_hash(stream: BinaryIO) -> str:
    digest = hashlib.sha256()
    while True:
        chunk = stream.read(1024 * 1024)
        if not chunk:
            return digest.hexdigest()
        digest.update(chunk)


def archive_summary(archive: Path, source: Optional[Path] = None) -> dict[str, object]:
    archive = archive.resolve()
    if not archive.is_file() or not zipfile.is_zipfile(archive):
        fail(f"archive is not a valid ZIP file: {archive}")
    size = archive.stat().st_size
    if size >= MAX_ARCHIVE_BYTES:
        fail(f"archive must be smaller than {MAX_ARCHIVE_BYTES} bytes: {size}")
    with zipfile.ZipFile(archive) as bundle:
        infos = bundle.infolist()
        names = [info.filename for info in infos if not info.is_dir()]
        if len(names) != len(set(names)):
            fail("archive contains duplicate file names")
        for info in infos:
            name = info.filename
            path = PurePosixPath(name)
            if not name or name.startswith("/") or ".." in path.parts or "\\" in name:
                fail(f"archive contains an unsafe member path: {name!r}")
            mode = info.external_attr >> 16
            if stat.S_ISLNK(mode):
                fail(f"archive contains a symbolic link: {name}")
        if MANIFEST_PATH not in names:
            fail(f"archive is missing {MANIFEST_PATH} at its root")
        try:
            manifest = json.loads(bundle.read(MANIFEST_PATH).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            fail(f"archive manifest is invalid: {exc}")
        if not isinstance(manifest, dict):
            fail("archive manifest must be a JSON object")
        for field in ("name", "version"):
            if not isinstance(manifest.get(field), str) or not manifest[field]:
                fail(f"archive manifest has no non-empty {field}")
        if source is not None:
            source_paths = source_files(source.resolve())
            expected = {relative.as_posix() for _, relative in source_paths}
            actual = set(names)
            if actual != expected:
                missing = sorted(expected - actual)
                extra = sorted(actual - expected)
                fail(f"archive does not match source missing={missing} extra={extra}")
            changed = []
            for path, relative in source_paths:
                with path.open("rb") as source_file, bundle.open(relative.as_posix()) as archive_file:
                    if content_hash(source_file) != content_hash(archive_file):
                        changed.append(relative.as_posix())
            if changed:
                fail(f"archive contents do not match source changed={changed}")
    return {
        "archive": str(archive),
        "plugin": manifest["name"],
        "version": manifest["version"],
        "files": len(names),
        "bytes": size,
        "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
    }


def build_archive(source: Path, output: Path, force: bool = False) -> dict[str, object]:
    source = source.resolve()
    output = output.resolve()
    manifest_from_source(source)
    try:
        output.relative_to(source)
    except ValueError:
        pass
    else:
        if output.relative_to(source).parts[:1] != ("dist",):
            fail("archive output inside the plugin source must be under dist/")
    if output.exists() and not force:
        fail(f"archive already exists; choose another output or pass --force: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.{os.getpid()}.tmp")
    if temporary.exists():
        fail(f"temporary archive path already exists: {temporary}")
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
            for path, relative in source_files(source):
                info = zipfile.ZipInfo(relative.as_posix(), date_time=ARCHIVE_TIMESTAMP)
                info.create_system = 3
                info.compress_type = zipfile.ZIP_DEFLATED
                mode = stat.S_IMODE(path.stat().st_mode) or 0o644
                info.external_attr = (stat.S_IFREG | mode) << 16
                with path.open("rb") as source_file, bundle.open(info, "w") as destination:
                    shutil.copyfileobj(source_file, destination)
        summary = archive_summary(temporary, source)
        if summary["bytes"] >= MAX_ARCHIVE_BYTES:
            fail(f"archive must be smaller than {MAX_ARCHIVE_BYTES} bytes")
        if output.exists():
            output.unlink()
        temporary.replace(output)
        return archive_summary(output, source)
    finally:
        if temporary.exists():
            temporary.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="Build and validate a plugin ZIP archive")
    build.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1])
    build.add_argument("--output", type=Path, required=True)
    build.add_argument("--force", action="store_true", help="Replace an existing output archive")
    verify = commands.add_parser("verify", help="Validate an existing plugin ZIP archive")
    verify.add_argument("archive", type=Path)
    verify.add_argument("--source", type=Path, help="Require exact file parity with this source directory")
    args = parser.parse_args()
    if args.command == "build":
        result = build_archive(args.source, args.output, args.force)
    else:
        result = archive_summary(args.archive, args.source)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"plugin archive validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
