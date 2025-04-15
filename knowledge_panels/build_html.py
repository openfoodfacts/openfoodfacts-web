"""
This script builds the static HTML dump of information knowledge panels
from content YAML file.

This script should be launched before committing every time a change is done
to `content.yml`.
"""

import argparse
import itertools
from pathlib import Path

import markdown
import ruamel.yaml
from openfoodfacts.types import Country, Lang
from openfoodfacts.utils import get_logger
from pydantic import BaseModel, constr

yaml = ruamel.yaml.YAML(typ='safe')

logger = get_logger()

PROJECT_DIR = Path(__file__).parent
ROOT_HTML_DIR = PROJECT_DIR.parent / "lang"


class KnowledgeContentItem(BaseModel):
    value_tag: constr(min_length=3)
    content: constr(min_length=2)
    category_tag: str | None = None


def generate_file_path(
    root_dir: Path,
    item: KnowledgeContentItem,
    flavor: str|None,
    tag_type: str,
    country: str,
    lang: str,
) -> Path:
    """Generate a file path unique to the knowledge content item.

    The generated path depends on the `flavor` `tag_type`, the `value_tag`, the
    `country` the `lang` and the `category_tag`.

    Args:
        root_dir: the root directory where HTML pages are located
        item: the knowledge content item
        tag_type: the target tag type
        flavor: obf, opff, opf, off
        country: the target country (2-letters code or 'world')
        lang: the target lang (2-letters code)

    Returns:
        Path: the path where the HTML page should be saved
    """
    category_tag_suffix = "" if item.category_tag is None else f"_{item.category_tag}"
    flavor = flavor or ""
    value_tag = item.value_tag.replace(":", "_")
    return (
        root_dir
        / flavor
        / lang
        / "knowledge_panels"
        / tag_type
        / f"{value_tag}_{country}{category_tag_suffix}.html"
    )


def build_content(root_dir: Path, dir_paths: list[Path]):
    """Build content as HTML pages from YAML files.

    Each directory in `dir_paths` should contain YAML files following
    the schema of `KnowledgeContent`. Files are saved as HTML files
    under `root_dir`, see `generate_file_path` for more information.

    Args:
        root_dir: the root directory where HTML pages are located
        dir_paths: the directories containing YAML files
    """
    for dir_path in dir_paths:
        for file_path in dir_path.glob("*.yml"):
            build_content_from_file(root_dir, file_path)
        for file_path in dir_path.glob("*/*.yml"):
            build_content_from_file(root_dir, file_path, flavor=file_path.parent.stem)


def build_content_from_file(root_dir: Path, file_path: Path, flavor=None):
    """Build content as HTML pages from `file_path` (a YAML file).

    The YAML file should follows the schema of `KnowledgeContent`.
    Files are saved as HTML files under `root_dir`, see
    `generate_file_path` for more information about how paths
    are generated.

    Args:
        root_dir: the root directory where HTML pages are located
        file_path: the input YAML file path
    """
    if flavor and (flavor not in ("obf", "off", "opf", "opff")):
        logger.info("Ignoring file %s: unknown flavor %s", file_path, flavor)
        return

    # tag_type is in the name of the directory
    tag_type = (
        file_path.parent.stem if not flavor else file_path.parent.parent.stem
    )

    if tag_type not in ("labels", "additives", "categories", "ingredients", "nutrients"):
        logger.info("Ignoring file %s: unknown tag type %s", file_path, tag_type)
        return

    # country-lang is the name of the file
    country, lang = file_path.stem.split("-", maxsplit=1)

    if country not in Country.__members__:
        logger.info("Ignoring file %s: unknown country %s", file_path, country)

    elif lang not in Lang.__members__:
        logger.info("Ignoring file %s: unknown lang %s", file_path, lang)
        return

    # remove existing files
    for file in root_dir.glob(f"knowledge_panels{f'/{flavor}' if flavor else ''}/*.html"):
        file_path.unlink()

    # read data
    with file_path.open("r") as f:
        data = yaml.load(f)
    
    # generate html files
    for value_tag, item in data.items():
        content = item["content"]
        output_path = generate_file_path(
            root_dir,
            KnowledgeContentItem(
                value_tag=value_tag,
                content=content,
                category_tag=item.get("category_tag"),
            ),
            flavor=flavor,
            tag_type=tag_type,
            country=country,
            lang=lang,
        )
        logger.info("Writing file %s", output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown.markdown(content))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "dir_path",
        type=Path,
        nargs="+",
        help="One or more directories containing YAML files (and eventual flavors dirs)",
    )
    args = parser.parse_args()
    build_content(ROOT_HTML_DIR, args.dir_path)
