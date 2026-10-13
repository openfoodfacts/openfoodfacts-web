#!/usr/bin/env python3
"""
Unit tests for scripts/add_query.py
"""

import os
import shutil
import sys
import tempfile
import unittest
import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
if os.path.dirname(__file__) not in sys.path:
    sys.path.insert(0, os.path.dirname(__file__))

from scripts.add_query import (
    slugify,
    clean_field_value,
    clean_dropdown,
    clean_url,
    parse_query_params_from_url,
    parse_issue_markdown,
    build_query_dict,
    add_query,
)
from scripts.compile_queries import validate_query, VALID_TOPICS, VALID_QUERY_TYPES


class TestAddQuery(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_queries_")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_slugify(self):
        self.assertEqual(slugify("Sugars vs Additives in Yogurts"), "sugars-vs-additives-in-yogurts")
        self.assertEqual(slugify("Nutri-Score & Organic Status !"), "nutri-score-organic-status")
        self.assertEqual(slugify("What's in my Food?"), "whats-in-my-food")
        self.assertEqual(slugify(""), "")

    def test_clean_dropdown(self):
        self.assertEqual(clean_dropdown("beverages (🥤 Beverages / Boissons)"), "beverages")
        self.assertEqual(clean_dropdown("scatter_plot (📈 Scatter Plot / Nuage de points)"), "scatter_plot")
        self.assertEqual(clean_dropdown("world (🌍 Worldwide)"), "world")
        self.assertEqual(clean_dropdown("nutrition"), "nutrition")

    def test_clean_url(self):
        self.assertEqual(
            clean_url("https://world.openfoodfacts.org/cgi/search.pl?action=process"),
            "https://world.openfoodfacts.org/cgi/search.pl?action=process"
        )
        self.assertEqual(
            clean_url("<https://world.openfoodfacts.org/cgi/search.pl>"),
            "https://world.openfoodfacts.org/cgi/search.pl"
        )
        self.assertEqual(
            clean_url("[Query](https://world.openfoodfacts.org/cgi/search.pl)"),
            "https://world.openfoodfacts.org/cgi/search.pl"
        )
        self.assertEqual(clean_url("_No response_"), "")

    def test_parse_query_params_from_url(self):
        url = "https://world.openfoodfacts.org/cgi/search.pl?action=process&tagtype_0=categories&tag_0=sodas&axis_x=sugars&axis_y=additives_n&series_organic=on&generate_graph_scatter_plot=1"
        params, axis_x, axis_y, tags_combined = parse_query_params_from_url(url)
        self.assertEqual(axis_x, "sugars")
        self.assertEqual(axis_y, "additives_n")
        self.assertIn("category:sodas", tags_combined)
        self.assertIn("series:organic", tags_combined)
        self.assertEqual(params.get("generate_graph_scatter_plot"), "1")

    def test_parse_issue_markdown(self):
        md = """
### Query / Graph Title
Sugars vs Additives in Breakfast Cereals

### Open Food Facts Query URL
https://world.openfoodfacts.org/cgi/search.pl?action=process&tagtype_0=categories&tag_0=breakfast-cereals&axis_x=sugars&axis_y=additives_n&generate_graph_scatter_plot=1

### Description & Insights
Scatter plot comparing sugar levels and additive counts across popular breakfast cereals.

### Food Topic
breakfast (🥣 Breakfast & Cereals / Petit-déjeuner & Céréales)

### Visualization / Query Format
scatter_plot (📈 Scatter Plot / Nuage de points)

### Geographic Scope
fr (🇫🇷 France)

### Author / Contributor Name
Pierre

### Keywords (comma-separated, optional)
cereals, breakfast, sugars, additives
"""
        parsed = parse_issue_markdown(md)
        self.assertEqual(parsed["title"], "Sugars vs Additives in Breakfast Cereals")
        self.assertEqual(parsed["topic"], "breakfast")
        self.assertEqual(parsed["query_type"], "scatter_plot")
        self.assertEqual(parsed["geography"], "fr")
        self.assertEqual(parsed["author"], "Pierre")
        self.assertEqual(parsed["keywords"], ["cereals", "breakfast", "sugars", "additives"])

    def test_build_query_dict_and_add_query(self):
        data = {
            "title": "Protein vs Energy in Plant Milks",
            "url": "https://world.openfoodfacts.org/cgi/search.pl?action=process&tagtype_0=categories&tag_0=plant-milks&axis_x=energy-kcal&axis_y=proteins&generate_graph_scatter_plot=1",
            "description": "Exploration of protein richness in oat, soy, and almond milks.",
            "topic": "beverages (🥤 Beverages / Boissons)",
            "query_type": "scatter_plot",
            "geography": "world",
            "author": "Data Scientist",
            "keywords": ["plant-milks", "protein", "energy"],
        }
        query_dict = build_query_dict(data)
        self.assertEqual(query_dict["id"], "protein-vs-energy-in-plant-milks")
        self.assertEqual(query_dict["topic"], "beverages")
        self.assertEqual(query_dict["query_type"], "scatter_plot")
        self.assertEqual(query_dict["geographies"], ["world"])
        self.assertEqual(query_dict["axis_x"], "energy-kcal")
        self.assertEqual(query_dict["axis_y"], "proteins")

        success, warnings, filepath = add_query(query_dict, queries_dir=self.test_dir)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(filepath))

        with open(filepath, "r", encoding="utf-8") as f:
            loaded = yaml.safe_load(f)
        self.assertEqual(loaded["title"], "Protein vs Energy in Plant Milks")
        self.assertEqual(loaded["id"], "protein-vs-energy-in-plant-milks")


if __name__ == "__main__":
    unittest.main()
