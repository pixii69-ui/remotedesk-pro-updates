"""Validate an approved RemoteDesk PRO release manifest.

No deployment or publication is performed. Optional --verify-downloads checks
that the public GitHub Release files really match their advertised SHA-256.
"""
import argparse
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

REPO_RELEASES = "https://github.com/pixii69-ui/remotedesk-pro-updates/releases/download"
PLATFORM_FILENAMES = {
    "android": "RemoteDeskPRO.apk",
    "windows": "RemoteDeskPRO-Windows.zip",
}
MAX_PACKAGE_BYTES = 500 * 1024 * 1024
ALLOWED_FINAL_HOSTS = {
    "github.com",
    "release-assets.githubusercontent.com",
    "objects.githubusercontent.com",
}


class ManifestError(ValueError):
    """A manifest is invalid and must not be published."""


def validate(data: object) -> dict:
    if not isinstance(data, dict):
        raise ManifestError("Manifest must be a JSON object")
    if set(data) != {"version", "version_code", "notes", "platforms"}:
        raise ManifestError("Unexpected or missing manifest keys")
    version = data["version"]
    code = data["version_code"]
    notes = data["notes"]
    platforms = data["platforms"]

    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ManifestError("Invalid semantic version")
    if type(code) is not int or code < 1:
        raise ManifestError("version_code must be a positive integer")
    if not isinstance(notes, str) or len(notes) > 2000:
        raise ManifestError("Invalid release notes")
    if not isinstance(platforms, dict) or set(platforms) != set(PLATFORM_FILENAMES):
        raise ManifestError("Manifest must contain Android and Windows")

    for platform, filename in PLATFORM_FILENAMES.items():
        asset = platforms[platform]
        if not isinstance(asset, dict) or set(asset) != {"url", "filename", "sha256"}:
            raise ManifestError(f"Invalid {platform} asset")
        expected_url = f"{REPO_RELEASES}/v{version}/{filename}"
        if asset["filename"] != filename or asset["url"] != expected_url:
            raise ManifestError(f"Untrusted {platform} release URL or filename")
        pieces = urlsplit(asset["url"])
        if (pieces.scheme != "https" or pieces.hostname != "github.com"
                or pieces.username or pieces.password or pieces.port
                or pieces.query or pieces.fragment):
            raise ManifestError(f"Unsafe {platform} URL")
        sha = asset["sha256"]
        if not isinstance(sha, str) or not re.fullmatch(r"[a-fA-F0-9]{64}", sha):
            raise ManifestError(f"Invalid {platform} SHA-256")
        if sha == "0" * 64:
            raise ManifestError(f"{platform} has placeholder SHA-256")
    return data


def verify_downloads(manifest: dict) -> None:
    for platform in PLATFORM_FILENAMES:
        asset = manifest["platforms"][platform]
        request = urllib.request.Request(
            asset["url"],
            headers={"User-Agent": "RemoteDeskPRO-ManifestValidator/1.0"},
        )
        digest = hashlib.sha256()
        total = 0
        with urllib.request.urlopen(request, timeout=30) as response:
            final_url = urlsplit(response.url)
            if (final_url.scheme != "https"
                    or final_url.hostname not in ALLOWED_FINAL_HOSTS):
                raise ManifestError(f"Unexpected redirect for {platform}")
            if response.status != 200:
                raise ManifestError(f"{platform} release file not found")
            while True:
                block = response.read(1024 * 1024)
                if not block:
                    break
                total += len(block)
                if total > MAX_PACKAGE_BYTES:
                    raise ManifestError(f"{platform} release exceeds size limit")
                digest.update(block)
        if total == 0:
            raise ManifestError(f"{platform} release file is empty")
        if digest.hexdigest() != asset["sha256"].lower():
            raise ManifestError(f"{platform} public release SHA-256 mismatch")
        print(f"{platform}: verified {total} bytes and SHA-256", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path)
    parser.add_argument("--verify-downloads", action="store_true")
    args = parser.parse_args()
    try:
        manifest = validate(json.loads(args.file.read_text(encoding="utf-8")))
        print(f"Manifest v{manifest['version']} schema: PASS")
        if args.verify_downloads:
            verify_downloads(manifest)
            print("Public release asset checks: PASS")
        return 0
    except (ManifestError, OSError, ValueError, urllib.error.URLError) as error:
        print(f"Manifest validation FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
