"""Generate public OTA manifest only from reviewed Release files.

Called by manual owner-approved workflow after signature, version and package
checks. Never writes fake hashes or creates a public GitHub Release.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

from validate_manifest import REPO_RELEASES, validate

FIRST_OTA_VERSION = (0, 3, 2)
FIRST_OTA_CODE = 5
FILES = {"android": "RemoteDeskPRO.apk", "windows": "RemoteDeskPRO-Windows.zip"}


def parse_version(value: str) -> tuple[int, int, int]:
    if not isinstance(value, str) or not re.fullmatch(r"\d+\.\d+\.\d+", value):
        raise ValueError("Invalid semantic version")
    return tuple(int(part) for part in value.split("."))


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def make_manifest(
    version: str,
    code: int,
    notes: str,
    android: Path,
    windows: Path,
    previous: dict | None = None,
) -> dict:
    semver = parse_version(version)
    if type(code) is not int or code < FIRST_OTA_CODE or semver < FIRST_OTA_VERSION:
        raise ValueError("First OTA must be at least 0.3.2+5 (0.3.1+4 is already installed)")
    if not isinstance(notes, str) or len(notes) > 2000:
        raise ValueError("Invalid release notes")
    if previous is not None:
        validate(previous)
        if code <= previous["version_code"] or semver <= parse_version(previous["version"]):
            raise ValueError("OTA must strictly advance both versionCode and app version")
    for path in (android, windows):
        if not path.is_file() or path.stat().st_size < 1024:
            raise ValueError("Missing or implausibly small released package")

    base = f"{REPO_RELEASES}/v{version}/"
    result = {
        "version": version,
        "version_code": code,
        "notes": notes,
        "platforms": {
            platform: {
                "url": base + filename,
                "filename": filename,
                "sha256": file_sha256({"android": android, "windows": windows}[platform]),
            }
            for platform, filename in FILES.items()
        },
    }
    return validate(result)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--code", required=True, type=int)
    parser.add_argument("--notes", required=True)
    parser.add_argument("--android", required=True, type=Path)
    parser.add_argument("--windows", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    previous = None
    if args.output.exists():
        previous = json.loads(args.output.read_text(encoding="utf-8"))
    manifest = make_manifest(
        args.version, args.code, args.notes, args.android, args.windows, previous
    )
    args.output.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("Strictly newer public OTA manifest prepared, based on actual Release files.")


if __name__ == "__main__":
    main()
