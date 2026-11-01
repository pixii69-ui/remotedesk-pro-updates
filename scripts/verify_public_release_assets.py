"""Verify public Android signer and exact package ID before enabling OTA.

Only the public certificate fingerprint is pinned here; no signing secrets.
Windows ZIP is integrity-checked, but is not Authenticode-signed.
"""
import argparse
import re
import subprocess
import zipfile
from pathlib import Path, PurePosixPath

RELEASE_CERT_SHA256 = "1eb8ba1b463f9802da44f064383a93ceb6ebb4b5fe102cfd19d800f77716d4b9"
APPLICATION_ID = "pl.remotedesk.remotedesk_pro"
MAX_ANDROID_BYTES = 200 * 1024 * 1024
MAX_WINDOWS_BYTES = 400 * 1024 * 1024


def verify_certificate(output: str) -> None:
    fingerprints = {
        fingerprint.lower()
        for fingerprint in re.findall(
            r"(?:Signer #\d+|V\d+ Signer): certificate SHA-256 digest:\s*([0-9a-fA-F]{64})",
            output,
        )
    }
    if fingerprints != {RELEASE_CERT_SHA256}:
        raise ValueError("Android signing certificate differs from permanent RemoteDesk PRO key")


def verify_badging(output: str, version: str, code: int) -> None:
    package = re.search(
        r"^package:\s+name='([^']+)'\s+versionCode='(\d+)'\s+versionName='([^']+)'",
        output,
        re.MULTILINE,
    )
    if not package:
        raise ValueError("Cannot read Android package version and identity")
    app_id, build, name = package.groups()
    if app_id != APPLICATION_ID or int(build) != code or name != version:
        raise ValueError("APK app ID, versionName or versionCode does not match approved Release")


def run_tool(binary: str, args: list[str]) -> str:
    result = subprocess.run(
        [binary, *args],
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return result.stdout


def check_apk(apk: Path, version: str, code: int, apksigner: str, aapt: str) -> None:
    size = apk.stat().st_size
    if not (1024 * 1024 <= size <= MAX_ANDROID_BYTES):
        raise ValueError("Unexpected Android APK size")
    verify_certificate(run_tool(apksigner, ["verify", "--verbose", "--print-certs", str(apk)]))
    verify_badging(run_tool(aapt, ["dump", "badging", str(apk)]), version, code)


def check_windows_zip(path: Path) -> None:
    size = path.stat().st_size
    if not (1024 * 1024 <= size <= MAX_WINDOWS_BYTES):
        raise ValueError("Unexpected Windows ZIP size")
    with zipfile.ZipFile(path) as archive:
        files = [name.replace("\\", "/") for name in archive.namelist()]
        for name in files:
            pure = PurePosixPath(name)
            if not name or pure.is_absolute() or ".." in pure.parts or ":" in name:
                raise ValueError("Suspicious Windows ZIP member path")
        if len(files) != len(set(files)):
            raise ValueError("Windows ZIP has duplicate member names")
        if not {
            "remotedesk_pro.exe", "flutter_windows.dll"
        }.issubset(files) or not any(
            name.startswith("data/flutter_assets/") for name in files
        ):
            raise ValueError("Incomplete Flutter Windows portable package")
        if archive.testzip() is not None:
            raise ValueError("Windows ZIP has a corrupt member")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--code", type=int, required=True)
    parser.add_argument("--android", type=Path, required=True)
    parser.add_argument("--windows", type=Path, required=True)
    parser.add_argument("--apksigner", required=True)
    parser.add_argument("--aapt", required=True)
    args = parser.parse_args()
    check_apk(args.android, args.version, args.code, args.apksigner, args.aapt)
    check_windows_zip(args.windows)
    print("Approved Android certificate, APK package ID, version and Windows ZIP: PASS")
