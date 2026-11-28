import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import add_faq_question
import compile_faq


class FAQAnswerTests(unittest.TestCase):
    def test_keeps_proposed_answer_subsections_in_one_question(self):
        issue_body = """### Language

en (English)

### Category

volunteering-contribution (Volunteering & Contributions)

### Question Title

Where can I see a product's edit history?

### Proposed Answer (Markdown)

## Website

Open the product edit page.

### Mobile app

Use the website to see the revision history.

### Sources / Documentation Links (optional)

https://wiki.openfoodfacts.org/

### Contribution Checklist

- [x] I checked the proposed answer.
"""
        parsed = add_faq_question.parse_issue_markdown(issue_body)
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "en").mkdir()
            with (
                patch.object(add_faq_question, "FAQ_DIR", directory),
                patch.object(compile_faq, "FAQ_DIR", directory),
            ):
                result = add_faq_question.add_faq_question(**parsed)
                categories, errors, _ = compile_faq.load_faq_for_lang("en")

        self.assertTrue(result["success"], result)
        self.assertEqual(errors, [])
        [category] = categories
        [question] = category["questions"]
        self.assertEqual(question["question"], parsed["question"])
        self.assertIn("<h4>Website</h4>", question["answer_html"])
        self.assertIn("<h4>Mobile app</h4>", question["answer_html"])
        self.assertIn("Open the product edit page.", question["answer_html"])
        self.assertIn("Use the website to see the revision history.", question["answer_html"])
        self.assertIn("https://wiki.openfoodfacts.org/", question["answer_html"])
        self.assertNotIn("I checked the proposed answer.", question["answer_html"])
