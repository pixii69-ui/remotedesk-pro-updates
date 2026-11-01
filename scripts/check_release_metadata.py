"""Reject prerelease and draft Release metadata before OTA activation."""
import argparse
import json
import re
from pathlib import Path


def check_release(metadata: dict, version: str) -> None:
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Invalid semantic version")
    if not isinstance(metadata, dict):
        raise ValueError("Release metadata is not an object")
    if metadata.get("tagName") != f"v{version}":
        raise ValueError("Release tag mismatch")
    if metadata.get("isDraft") is not False or metadata.get("isPrerelease") is not False:
        raise ValueError("Only an already published stable Release can activate public OTA")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("metadata", type=Path)
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    check_release(json.loads(args.metadata.read_text(encoding="utf-8")), args.version)
    print("Existing stable public GitHub Release: PASS")
