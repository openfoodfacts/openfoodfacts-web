#!/usr/bin/env python3
"""
Unit tests for scripts/fetch_reuse_icons.py
"""

import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from fetch_reuse_icons import (
    ensure_reuse_icon,
    extract_apple_id,
    extract_play_pkg,
    is_valid_cached_icon,
)


class TestFetchReuseIcons(unittest.TestCase):

    def test_extract_play_pkg(self):
        self.assertEqual(
            extract_play_pkg("https://play.google.com/store/apps/details?id=org.openfoodfacts.scanner&hl=en"),
            "org.openfoodfacts.scanner",
        )
        self.assertEqual(
            extract_play_pkg("https://play.google.com/apps/testing/com.example.app"),
            "com.example.app",
        )
        self.assertIsNone(extract_play_pkg("https://example.com"))
        self.assertIsNone(extract_play_pkg(None))

    def test_extract_apple_id(self):
        self.assertEqual(
            extract_apple_id("https://apps.apple.com/fr/app/open-food-facts/id588797948"),
            "588797948",
        )
        self.assertIsNone(extract_apple_id("https://example.com"))
        self.assertIsNone(extract_apple_id(None))

    def test_ensure_reuse_icon_uses_existing_valid_file(self):
        temp_icons = tempfile.mkdtemp()
        try:
            icon_path = os.path.join(temp_icons, "my-app.png")
            with open(icon_path, "wb") as f:
                f.write(b"\x89PNG\r\n\x1a\n" + b"0" * 200)

            item = {"id": "my-app", "cached_icon": None}
            res = ensure_reuse_icon(item, icons_dir=temp_icons)
            self.assertEqual(res["status"], "existing")
            self.assertEqual(item["cached_icon"], "/images/reuses/icons/my-app.png")
            self.assertTrue(is_valid_cached_icon("/images/reuses/icons/my-app.png", icons_dir=temp_icons))
        finally:
            shutil.rmtree(temp_icons)

    def test_ensure_reuse_icon_falls_back_to_play_store(self):
        temp_icons = tempfile.mkdtemp()
        try:
            item = {
                "id": "play-app",
                "play_store": "https://play.google.com/store/apps/details?id=com.example.play",
                "cached_icon": None,
            }

            def fake_cache(url, reuse_id, icons_dir=None):
                out = os.path.join(icons_dir, f"{reuse_id}.png")
                with open(out, "wb") as f:
                    f.write(b"\x89PNG\r\n\x1a\n" + b"1" * 200)
                return f"/images/reuses/icons/{reuse_id}.png"

            with patch("fetch_reuse_icons.fetch_play_store_details", return_value={
                "status": "ok",
                "icon_url": "https://play-lh.googleusercontent.com/abc=s512",
                "rating": 4.6,
            }), patch("fetch_reuse_icons.cache_reuse_icon", side_effect=fake_cache):
                res = ensure_reuse_icon(item, icons_dir=temp_icons, include_domain_favicon=False)

            self.assertEqual(res["status"], "resolved_play")
            self.assertEqual(item["cached_icon"], "/images/reuses/icons/play-app.png")
            self.assertEqual(item["rating"], 4.6)
        finally:
            shutil.rmtree(temp_icons)


if __name__ == "__main__":
    unittest.main()
