"""
This script builds the static HTML dump of information knowledge panels
from content YAML file.

This script should be launched before committing every time a change is done
to `content.yml`.
"""

from collections import Counter
from pathlib import Path
from typing import Literal

import markdown
import yaml
from openfoodfacts.types import Country, Lang
from pydantic import BaseModel, constr, validator

PROJECT_DIR = Path(__file__).parent
ROOT_HTML_DIR = PROJECT_DIR.parent / "lang"


# Models related to information knowledge panel content


class KnowledgeContentItem(BaseModel):
    lang: Lang
    tag_type: Literal["labels", "additives", "categories"]
    value_tag: constr(min_length=3)
    content: constr(min_length=2)
    country: Country
    category_tag: str | None = None


class KnowledgeContent(BaseModel):
    items: list[KnowledgeContentItem]

    @validator("items")
    def unique_items(cls, v):
        """We check that there is no duplicate items, using as keys:
        lang, tag_type, value_tag, country and category tag."""
        count = Counter(
            (item.lang, item.tag_type, item.value_tag, item.country, item.category_tag)
            for item in v
        )
        most_common = count.most_common(1)
        if most_common and most_common[0][1] > 1:
            raise ValueError(f"more than 1 item with fields={most_common[0][0]}")
        return v


def generate_file_path(root_dir: Path, item: KnowledgeContentItem) -> Path:
    """Generate a file path unique to the knowledge content item.

    The generated path depends on the `tag_type`, the `value_tag`, the
    `country` the `lang` and the `category_tag`.

    Args:
        root_dir: the root directory where HTML pages are located
        item: the knowledge content item

    Returns:
        Path: the path where the HTML page should be saved
    """
    category_tag_suffix = "" if item.category_tag is None else f"_{item.category_tag}"
    value_tag = item.value_tag.replace(":", "_")
    return (
        root_dir
        / item.lang.name
        / "knowledge_panels"
        / item.tag_type
        / f"{value_tag}_{item.country.name}{category_tag_suffix}.html"
    )


def build_content(root_dir: Path, file_path: Path):
    """Build content as HTML pages from `file_path` (a YAML file).

    The YAML file should follows the schema of `KnowledgeContent`.
    Files are saved as HTML files under `root_dir`, see
    `generate_file_path` for more information about how paths
    are generated.

    Args:
        root_dir: the root directory where HTML pages are located
        file_path: the input YAML file path
    """
    with file_path.open("r") as f:
        data = yaml.safe_load(f)
    knowledge_items = KnowledgeContent.parse_obj(data)

    for item in knowledge_items.items:
        output_path = generate_file_path(root_dir, item)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown.markdown(item.content))


if __name__ == "__main__":
    build_content(ROOT_HTML_DIR, PROJECT_DIR / "content.yml")
