#!/usr/bin/env python3
"""
Unit tests for scripts/i18n_utils.py
"""

import sys
import unittest

from i18n_utils import get_localized_field, validate_localized_field

class TestI18nUtils(unittest.TestCase):

    def test_get_localized_field_dict(self):
        item = {
            "title": {
                "en": "Sugars in Sodas",
                "fr": "Sucres dans les sodas",
                "es": "Azúcares en refrescos"
            }
        }
        self.assertEqual(get_localized_field(item, "title", "en"), "Sugars in Sodas")
        self.assertEqual(get_localized_field(item, "title", "fr"), "Sucres dans les sodas")
        self.assertEqual(get_localized_field(item, "title", "es"), "Azúcares en refrescos")
        # Fallback to English when German is missing
        self.assertEqual(get_localized_field(item, "title", "de"), "Sugars in Sodas")

    def test_get_localized_field_suffixed(self):
        item = {
            "title_en": "Sugars in Sodas",
            "title_fr": "Sucres dans les sodas"
        }
        self.assertEqual(get_localized_field(item, "title", "en"), "Sugars in Sodas")
        self.assertEqual(get_localized_field(item, "title", "fr"), "Sucres dans les sodas")
        self.assertEqual(get_localized_field(item, "title", "it"), "Sugars in Sodas")

    def test_get_localized_field_plain_string(self):
        item = {
            "title": "Universal English Title"
        }
        self.assertEqual(get_localized_field(item, "title", "en"), "Universal English Title")
        self.assertEqual(get_localized_field(item, "title", "fr"), "Universal English Title")

    def test_get_localized_field_mixed_override(self):
        item = {
            "description": "Base description",
            "description_fr": "Description française spécifique"
        }
        self.assertEqual(get_localized_field(item, "description", "fr"), "Description française spécifique")
        self.assertEqual(get_localized_field(item, "description", "en"), "Base description")
        self.assertEqual(get_localized_field(item, "description", "es"), "Base description")

    def test_validate_localized_field(self):
        # Valid string
        errors = validate_localized_field({"title": "Test"}, "title", "test.yaml", required=True)
        self.assertEqual(errors, [])

        # Valid dict
        errors = validate_localized_field({"title": {"en": "Test", "fr": "Essai"}}, "title", "test.yaml", required=True)
        self.assertEqual(errors, [])

        # Valid suffixed
        errors = validate_localized_field({"title_en": "Test"}, "title", "test.yaml", required=True)
        self.assertEqual(errors, [])

        # Missing required
        errors = validate_localized_field({}, "title", "test.yaml", required=True)
        self.assertIn("missing required field 'title'", errors[0])

        # Empty string
        errors = validate_localized_field({"title": "   "}, "title", "test.yaml", required=True)
        self.assertIn("missing or empty required field 'title'", errors[0])

        # Empty dict
        errors = validate_localized_field({"title": {"en": "  "}}, "title", "test.yaml", required=True)
        self.assertIn("translation dictionary has no non-empty values", errors[0])

if __name__ == "__main__":
    unittest.main()
