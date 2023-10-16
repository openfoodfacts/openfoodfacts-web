import argparse
import json
import os
import time
from pathlib import Path

import requests
import ruamel.yaml as yaml
from openfoodfacts import Country, Lang
from openfoodfacts.utils import get_logger

from knowledge_panels._types import KnowledgeContent, KnowledgeContentGroup

session = requests.Session()

logger = get_logger()


RESPONSE_SAVE_DIR = Path(__file__).parent / "responses"
RESPONSE_SAVE_DIR.mkdir(exist_ok=True)


OPENAI_API_KEY = os.environ["OPENAPI_KEY"]

INSTRUCTIONS_TEMPLATE = """Translate to '%s' the following text in '%s'. Do *NOT* use the acronym "GRAS" (generally recognized as safe) in the output translation: an appropriate translation should be used instead."""


class ContextLengthExceededException(Exception):
    pass


def send_request(text: str, source_lang: str, target_lang: str) -> dict:
    instructions = INSTRUCTIONS_TEMPLATE % (source_lang, target_lang)
    user_message = f"{instructions}\n\n'''{text}'''"
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are ChatGPT, a large language model trained by OpenAI."
                ),
            },
            {"role": "user", "content": user_message},
        ],
    }

    while True:
        r = session.post(
            "https://api.openai.com/v1/chat/completions",
            json=payload,
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        )

        if r.status_code == 429 or str(r.status_code).startswith("5"):
            if r.status_code == 429:
                logger.info("Rate limit reached, sleeping for 1 min")
                time.sleep(60)
            else:
                logger.info("%d HTTP error, sleeping for 5s", r.status_code)
                time.sleep(5)
        else:
            break

    if (
        r.status_code == 400
        and r.json()["error"].get("code") == "context_length_exceeded"
    ):
        raise ContextLengthExceededException()

    r.raise_for_status()
    return r.json()


def save_response(identifier: str, response: dict):
    file_path = RESPONSE_SAVE_DIR / f"{identifier}.json"
    logger.debug("Saving OpenAI response in %s", file_path)

    with file_path.open("w") as f:
        json.dump(response, f, ensure_ascii=False)


def response_exists(identifier: str):
    return (RESPONSE_SAVE_DIR / f"{identifier}.json").is_file()


def fetch_cached_response(identifier: str):
    file_path = RESPONSE_SAVE_DIR / f"{identifier}.json"
    if file_path.is_file():
        return json.loads(file_path.read_text())


def translate(
    identifier: str, text: str, source_lang: str, target_lang: str
) -> list | None:
    if (response := fetch_cached_response(identifier)) is None:
        try:
            response = send_request(text, source_lang, target_lang)
        except ContextLengthExceededException:
            logger.info(f"Context length exception for {identifier}")
            return None

        response["data"] = {
            "prompt": INSTRUCTIONS_TEMPLATE,
            "text": text,
        }
        save_response(identifier, response)
    else:
        logger.debug("Cached response used for %s", identifier)

    usage = response["usage"]
    logger.debug(
        "Usage: completion tokens: %s, prompt tokens: %s, total tokens: %s",
        usage["completion_tokens"],
        usage["prompt_tokens"],
        usage["total_tokens"],
    )
    choice = response["choices"][0]
    text_response = choice["message"]["content"]
    return text_response.strip('" \t\n')


def run(
    input_path: Path, output_path: Path, source_lang: Lang, target_langs: list[Lang]
):
    data = yaml.safe_load(input_path.read_text())
    knowledge_content = KnowledgeContent.model_validate(data)

    new_groups = []
    for group in knowledge_content.groups:
        if group.lang != source_lang and group.country is Country.world:
            continue

        for target_lang in target_langs:
            new_items = []
            for item in group.items:
                logger.debug(
                    f"Translating {item.value_tag} ({source_lang} > {target_lang})"
                )
                id_ = f"translate-{source_lang.name}-{target_lang.name}-{group.country.name}-{item.value_tag}"

                if item.category_tag:
                    id_ += f"-{item.category_tag}"
                translation = translate(
                    id_, item.content, source_lang.name, target_lang.name
                )
                logger.debug(f"Translation: {translation}")

                new_item = item.model_copy()
                new_item.content = translation
                new_items.append(new_item)

            new_groups.append(
                KnowledgeContentGroup(
                    lang=target_lang,
                    country=group.country,
                    tag_type=group.tag_type,
                    items=new_items,
                )
            )

    knowledge_content = KnowledgeContent(groups=new_groups)
    logger.info(f"Writing to {output_path}")
    output_data = knowledge_content.model_dump(mode="json", exclude_none=True)
    output_data = {
        "groups": [
            {k: group[k] for k in ("lang", "tag_type", "country", "items")}
            for group in output_data["groups"]
        ]
    }
    output_path.write_text(
        yaml.safe_dump(output_data, default_flow_style=False, allow_unicode=True)
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path", type=Path)
    parser.add_argument("output_path", type=Path)
    parser.add_argument("--source-lang", type=Lang, default=Lang.en)
    args = parser.parse_args()

    run(
        args.input_path,
        args.output_path,
        args.source_lang,
        [Lang.fr, Lang.es, Lang.de],
    )
