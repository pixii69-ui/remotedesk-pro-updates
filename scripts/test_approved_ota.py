"""Offline tests for explicit, monotonic owner-approved OTA activation."""
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from check_release_metadata import check_release
from prepare_approved_manifest import make_manifest
from verify_public_release_assets import (
    APPLICATION_ID, RELEASE_CERT_SHA256, check_windows_zip,
    verify_badging, verify_certificate,
)


class ApprovedOtaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.apk = root / "RemoteDeskPRO.apk"
        self.windows = root / "RemoteDeskPRO-Windows.zip"
        self.apk.write_bytes(b"A" * 2048)
        self.windows.write_bytes(b"B" * 2048)

    def manifest(self, version="0.3.2", code=5, previous=None):
        return make_manifest(version, code, "Test OTA", self.apk, self.windows, previous)

    def test_first_ota_requires_newer_version_and_real_hashes(self):
        manifest = self.manifest()
        self.assertEqual(manifest["version_code"], 5)
        self.assertEqual(
            manifest["platforms"]["android"]["url"],
            "https://github.com/pixii69-ui/remotedesk-pro-updates/releases/download/v0.3.2/RemoteDeskPRO.apk",
        )
        self.assertEqual(len(manifest["platforms"]["windows"]["sha256"]), 64)
        self.assertNotEqual(manifest["platforms"]["android"]["sha256"], "0" * 64)

    def test_do_not_activate_installed_baseline(self):
        with self.assertRaises(ValueError):
            self.manifest("0.3.1", 4)
        with self.assertRaises(ValueError):
            self.manifest("0.3.2", 4)

    def test_do_not_downgrade_after_activation(self):
        previous = self.manifest()
        with self.assertRaises(ValueError):
            self.manifest("0.3.2", 6, previous)
        with self.assertRaises(ValueError):
            self.manifest("0.3.3", 5, previous)
        newer = self.manifest("0.3.3", 6, previous)
        self.assertEqual(newer["version_code"], 6)

    def test_only_approved_stable_release(self):
        check_release(
            {"tagName": "v0.3.2", "isDraft": False, "isPrerelease": False}, "0.3.2"
        )
        for bad in (
            {"tagName": "v0.3.2", "isDraft": True, "isPrerelease": False},
            {"tagName": "v0.3.2", "isDraft": False, "isPrerelease": True},
            {"tagName": "v0.3.1", "isDraft": False, "isPrerelease": False},
        ):
            with self.assertRaises(ValueError):
                check_release(bad, "0.3.2")

    def test_signer_and_badging_are_pinned(self):
        verify_certificate(
            "V2 Signer: certificate SHA-256 digest: " + RELEASE_CERT_SHA256
        )
        with self.assertRaises(ValueError):
            verify_certificate("V2 Signer: certificate SHA-256 digest: " + "a" * 64)
        verify_badging(
            "package: name='" + APPLICATION_ID
            + "' versionCode='5' versionName='0.3.2' targetSdkVersion='36'",
            "0.3.2", 5,
        )
        with self.assertRaises(ValueError):
            verify_badging(
                "package: name='com.example.wrong' versionCode='5' versionName='0.3.2'",
                "0.3.2", 5,
            )

    def test_complete_windows_bundle(self):
        with zipfile.ZipFile(self.windows, "w") as archive:
            archive.writestr("remotedesk_pro.exe", b"app")
            archive.writestr("flutter_windows.dll", b"dll")
            archive.writestr("data/flutter_assets/AssetManifest.bin", b"assets")
            archive.writestr("padding.dat", b"X" * (1024 * 1024), compress_type=zipfile.ZIP_STORED)
        check_windows_zip(self.windows)

    def test_zip_path_traversal_rejected(self):
        with zipfile.ZipFile(self.windows, "w") as archive:
            archive.writestr("remotedesk_pro.exe", b"app")
            archive.writestr("flutter_windows.dll", b"dll")
            archive.writestr("data/flutter_assets/AssetManifest.bin", b"assets")
            archive.writestr("../bad_file", b"X" * (1024 * 1024), compress_type=zipfile.ZIP_STORED)
        with self.assertRaises(ValueError):
            check_windows_zip(self.windows)


if __name__ == "__main__":
    unittest.main()
