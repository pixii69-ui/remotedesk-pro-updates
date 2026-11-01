"""Offline regression tests for the release channel schema."""
import copy
import unittest

from validate_manifest import ManifestError, validate


def valid_manifest() -> dict:
    version = "0.4.0"
    base = ("https://github.com/pixii69-ui/remotedesk-pro-updates/"
            f"releases/download/v{version}/")
    return {
        "version": version,
        "version_code": 5,
        "notes": "Verified release",
        "platforms": {
            "android": {
                "url": base + "RemoteDeskPRO.apk",
                "filename": "RemoteDeskPRO.apk",
                "sha256": "a" * 64,
            },
            "windows": {
                "url": base + "RemoteDeskPRO-Windows.zip",
                "filename": "RemoteDeskPRO-Windows.zip",
                "sha256": "b" * 64,
            },
        },
    }


class ManifestValidatorTests(unittest.TestCase):
    def test_valid_manifest(self):
        data = valid_manifest()
        self.assertEqual(validate(data), data)

    def test_rejects_changed_repository(self):
        data = valid_manifest()
        data["platforms"]["android"]["url"] = (
            "https://github.com/attacker/repo/releases/download/v0.4.0/RemoteDeskPRO.apk"
        )
        with self.assertRaises(ManifestError):
            validate(data)

    def test_rejects_wrong_filename(self):
        data = valid_manifest()
        data["platforms"]["windows"]["filename"] = "setup.exe"
        with self.assertRaises(ManifestError):
            validate(data)

    def test_rejects_invalid_hash(self):
        data = valid_manifest()
        data["platforms"]["android"]["sha256"] = "not-a-sha"
        with self.assertRaises(ManifestError):
            validate(data)

    def test_rejects_placeholder_hash(self):
        data = valid_manifest()
        data["platforms"]["windows"]["sha256"] = "0" * 64
        with self.assertRaises(ManifestError):
            validate(data)

    def test_rejects_bool_version_code(self):
        data = valid_manifest()
        data["version_code"] = True
        with self.assertRaises(ManifestError):
            validate(data)

    def test_rejects_unknown_platform(self):
        data = valid_manifest()
        data["platforms"]["linux"] = copy.deepcopy(data["platforms"]["windows"])
        with self.assertRaises(ManifestError):
            validate(data)

    def test_rejects_notes_too_long(self):
        data = valid_manifest()
        data["notes"] = "a" * 2001
        with self.assertRaises(ManifestError):
            validate(data)


if __name__ == "__main__":
    unittest.main()
