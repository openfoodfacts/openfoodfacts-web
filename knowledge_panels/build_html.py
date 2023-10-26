"""
This script builds the static HTML dump of information knowledge panels
from content YAML file.

This script should be launched before committing every time a change is done
to `content.yml`.
"""

import argparse
from pathlib import Path

import markdown
import yaml
from _types import KnowledgeContent, KnowledgeContentItem
from openfoodfacts.types import Country, Lang

PROJECT_DIR = Path(__file__).parent
ROOT_HTML_DIR = PROJECT_DIR.parent / "lang"


def generate_file_path(
    root_dir: Path,
    item: KnowledgeContentItem,
    tag_type: str,
    country: Country,
    lang: Lang,
) -> Path:
    """Generate a file path unique to the knowledge content item.

    The generated path depends on the `tag_type`, the `value_tag`, the
    `country` the `lang` and the `category_tag`.

    Args:
        root_dir: the root directory where HTML pages are located
        item: the knowledge content item
        tag_type: the target tag type
        country: the target country (2-letters code or 'world')
        lang: the target lang (2-letters code)

    Returns:
        Path: the path where the HTML page should be saved
    """
    category_tag_suffix = "" if item.category_tag is None else f"_{item.category_tag}"
    value_tag = item.value_tag.replace(":", "_")
    return (
        root_dir
        / lang.name
        / "knowledge_panels"
        / tag_type
        / f"{value_tag}_{country.name}{category_tag_suffix}.html"
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
    knowledge_content = KnowledgeContent.model_validate(data)

    for group in knowledge_content.groups:
        for item in group.items:
            output_path = generate_file_path(
                root_dir,
                item,
                tag_type=group.tag_type,
                country=group.country,
                lang=group.lang,
            )
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(markdown.markdown(item.content))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", type=Path)
    args = parser.parse_args()
    build_content(ROOT_HTML_DIR, args.file_path)
